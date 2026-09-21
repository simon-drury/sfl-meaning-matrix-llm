"""
traincore.py - Genuine SFL Manifold Drift Training Engine.
Robust empirical parser for meaning matrix datasets.
Supports records formatted as lists of floats, 3x3 matrices, dicts with vector/matrix keys, or sequence objects.
"""

import os
import sys
import json
import argparse
import numpy as np
import torch
import torch.nn as nn
from torch.utils.data import Dataset, DataLoader

class SFLManifoldTransformer(nn.Module):
    def __init__(self, input_dim=9, d_model=128, nhead=4, num_layers=4, dim_feedforward=256, dropout=0.1):
        super().__init__()
        self.input_dim = input_dim
        self.in_proj = nn.Linear(input_dim, d_model)
        self.pos_encoder = nn.Parameter(torch.zeros(1, 64, d_model))
        encoder_layer = nn.TransformerEncoderLayer(
            d_model=d_model, nhead=nhead, dim_feedforward=dim_feedforward,
            dropout=dropout, batch_first=True
        )
        self.transformer = nn.TransformerEncoder(encoder_layer, num_layers=num_layers)
        self.out_proj = nn.Linear(d_model, input_dim)

    def forward(self, x):
        if x.dim() == 2:
            x = x.unsqueeze(1)
        b, s, _ = x.shape
        h = self.in_proj(x) + self.pos_encoder[:, :s, :]
        out = self.transformer(h)
        delta = self.out_proj(out)
        return delta.squeeze(1) if s == 1 else delta

def parse_9d_vector(obj):
    """Extract a 9-element 1D numpy array from varied json representations."""
    if obj is None:
        return None
    if isinstance(obj, (list, tuple)):
        flat = []
        for elem in obj:
            if isinstance(elem, (list, tuple)):
                flat.extend(elem)
            elif isinstance(elem, (int, float)):
                flat.append(float(elem))
        if len(flat) == 9:
            return np.array(flat, dtype=np.float32)
    elif isinstance(obj, dict):
        for k in ["matrix", "matrix_3x3", "vector", "m_9d", "values", "m"]:
            if k in obj:
                v = parse_9d_vector(obj[k])
                if v is not None:
                    return v
        # Try flattened Hallidayan keys
        halliday_keys = ["ideational", "field", "transitivity", "interpersonal", "tenor", "mood", "textual", "mode", "theme"]
        if all(k in obj for k in halliday_keys):
            return np.array([float(obj[k]) for k in halliday_keys], dtype=np.float32)
    return None

class EmpiricalSFLDataset(Dataset):
    def __init__(self, data_path="data/empirical_trajectories.jsonl", gold_path="data/meaning_matrix_gold_v0.1.jsonl"):
        self.trajectories = []
        
        target_files = [p for p in [data_path, gold_path] if os.path.exists(p)]
        if not target_files:
            raise FileNotFoundError(f"Neither {data_path} nor {gold_path} could be found.")

        for fpath in target_files:
            print(f"[Dataset] Parsing empirical records from {fpath}...")
            with open(fpath, "r", encoding="utf-8") as f:
                current_block_vectors = []
                for line in f:
                    line = line.strip()
                    if not line:
                        if len(current_block_vectors) >= 2:
                            self.trajectories.append(np.array(current_block_vectors, dtype=np.float32))
                        current_block_vectors = []
                        continue
                    try:
                        record = json.loads(line)
                        # Case 1: Record contains an explicit sequence list
                        seq_cand = None
                        for key in ["trajectory", "trajectories", "states", "sequence", "steps", "points"]:
                            if key in record and isinstance(record[key], list) and len(record[key]) >= 2:
                                seq_cand = record[key]
                                break
                        if seq_cand:
                            parsed_seq = [v for v in (parse_9d_vector(p) for p in seq_cand) if v is not None]
                            if len(parsed_seq) >= 2:
                                self.trajectories.append(np.array(parsed_seq, dtype=np.float32))
                        else:
                            # Case 2: Individual clause state record
                            v = parse_9d_vector(record)
                            if v is not None:
                                current_block_vectors.append(v)
                    except Exception:
                        pass
                if len(current_block_vectors) >= 2:
                    self.trajectories.append(np.array(current_block_vectors, dtype=np.float32))

        # Build pair transitions
        self.transitions = []
        for traj in self.trajectories:
            for t in range(len(traj) - 1):
                self.transitions.append((traj[t], traj[t+1]))

        # If records were individual states rather than multi-step sequences, chain adjacent pairs
        if len(self.transitions) == 0 and len(self.trajectories) >= 2:
            all_states = [traj[0] for traj in self.trajectories if len(traj) > 0]
            for t in range(len(all_states) - 1):
                self.transitions.append((all_states[t], all_states[t+1]))

        print(f"[Dataset] Total authentic empirical transitions (M_t -> M_{{t+1}}): {len(self.transitions)}")
        if len(self.transitions) == 0:
            raise ValueError(f"FATAL: Found records in {target_files}, but could not parse valid 9D transitions.")

    def __len__(self):
        return len(self.transitions)

    def __getitem__(self, idx):
        m_t, m_next = self.transitions[idx]
        delta = m_next - m_t
        return torch.tensor(m_t, dtype=torch.float32), torch.tensor(delta, dtype=torch.float32), torch.tensor(m_next, dtype=torch.float32)

def train_sfl_manifold(data_path="data/empirical_trajectories.jsonl", output_path="sfl_model_3x3.pt", epochs=25, batch_size=32, lr=1e-3):
    print("=" * 65)
    print("SFL MANIFOLD DRIFT MODEL - AUTHENTIC EMPIRICAL TRAINING")
    print("=" * 65)

    dataset = EmpiricalSFLDataset(data_path=data_path)
    dataloader = DataLoader(dataset, batch_size=min(batch_size, len(dataset)), shuffle=True)

    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    print(f"[Device] Using {device} for training.")

    model = SFLManifoldTransformer(input_dim=9).to(device)
    optimizer = torch.optim.AdamW(model.parameters(), lr=lr, weight_decay=1e-4)
    scheduler = torch.optim.lr_scheduler.CosineAnnealingLR(optimizer, T_max=max(1, epochs))
    criterion_delta = nn.MSELoss()
    criterion_cosine = nn.CosineSimilarity(dim=-1)

    print(f"\nStarting {epochs} epochs of authentic manifold drift learning...\n")
    for epoch in range(1, epochs + 1):
        model.train()
        total_loss = 0.0
        total_batches = 0

        for m_t, delta_target, m_next in dataloader:
            m_t = m_t.to(device)
            delta_target = delta_target.to(device)
            m_next = m_next.to(device)

            optimizer.zero_grad()
            delta_pred = model(m_t)
            
            pred_next = m_t + delta_pred
            loss_mse = criterion_delta(delta_pred, delta_target)
            loss_cos = 1.0 - criterion_cosine(pred_next, m_next).mean()
            loss = loss_mse + 0.5 * loss_cos

            loss.backward()
            torch.nn.utils.clip_grad_norm_(model.parameters(), max_norm=1.0)
            optimizer.step()

            total_loss += loss.item()
            total_batches += 1

        scheduler.step()
        avg_loss = total_loss / max(1, total_batches)
        if epoch % 5 == 0 or epoch == 1 or epoch == epochs:
            print(f"Epoch {epoch:02d}/{epochs} | Loss: {avg_loss:.6f}")

    torch.save(model.state_dict(), output_path)
    print("\n" + "=" * 65)
    print(f"[Success] Checkpoint saved directly to {output_path}")
    print("=" * 65 + "\n")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--data_path", type=str, default="data/empirical_trajectories.jsonl")
    parser.add_argument("--output_path", type=str, default="sfl_model_3x3.pt")
    parser.add_argument("--epochs", type=int, default=25)
    parser.add_argument("--batch_size", type=int, default=32)
    parser.add_argument("--lr", type=float, default=1e-3)
    args = parser.parse_args()

    train_sfl_manifold(
        data_path=args.data_path,
        output_path=args.output_path,
        epochs=args.epochs,
        batch_size=args.batch_size,
        lr=args.lr
    )
