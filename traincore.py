"""
traincore.py - Genuine SFL Manifold Drift Training Engine.
Strictly ingests empirical corpus data (data/empirical_trajectories.jsonl or data/uam_meaning_trajectories.npz).
NO SYNTHETIC FALLBACKS OR RANDOM WALKS: fails with explicit errors if real empirical data is missing.
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
        # x: (batch_size, seq_len, input_dim) or (batch_size, input_dim)
        if x.dim() == 2:
            x = x.unsqueeze(1)
        b, s, _ = x.shape
        h = self.in_proj(x) + self.pos_encoder[:, :s, :]
        out = self.transformer(h)
        delta = self.out_proj(out)
        return delta.squeeze(1) if s == 1 else delta

class EmpiricalSFLDataset(Dataset):
    def __init__(self, data_path="data/empirical_trajectories.jsonl", npz_path="data/uam_meaning_trajectories.npz"):
        self.trajectories = []
        
        # 1. Primary: empirical_trajectories.jsonl
        if os.path.exists(data_path):
            print(f"[Dataset] Loading authentic empirical trajectories from {data_path}...")
            with open(data_path, "r", encoding="utf-8") as f:
                for line_idx, line in enumerate(f):
                    line = line.strip()
                    if not line:
                        continue
                    try:
                        record = json.loads(line)
                        # Extract sequence of 9D state matrices
                        seq = None
                        for key in ["trajectory", "matrices", "states", "m_seq", "points"]:
                            if key in record and isinstance(record[key], list) and len(record[key]) > 1:
                                seq = record[key]
                                break
                        if seq is None and isinstance(record, list) and len(record) > 1:
                            seq = record

                        if seq:
                            parsed_seq = []
                            for pt in seq:
                                arr = np.array(pt, dtype=np.float32).flatten()
                                if len(arr) == 9:
                                    parsed_seq.append(arr)
                            if len(parsed_seq) >= 2:
                                self.trajectories.append(np.array(parsed_seq, dtype=np.float32))
                    except Exception as e:
                        pass
            print(f"[Dataset] Ingested {len(self.trajectories)} empirical multi-step trajectories.")

        # 2. Secondary: uam_meaning_trajectories.npz
        elif os.path.exists(npz_path):
            print(f"[Dataset] Loading authentic empirical trajectories from {npz_path}...")
            data = np.load(npz_path, allow_pickle=True)
            for k in data.files:
                arr = data[k]
                if arr.ndim == 2 and arr.shape[1] == 9 and len(arr) >= 2:
                    self.trajectories.append(arr.astype(np.float32))
                elif arr.ndim == 3 and arr.shape[2] == 9:
                    for item in arr:
                        if len(item) >= 2:
                            self.trajectories.append(item.astype(np.float32))
            print(f"[Dataset] Ingested {len(self.trajectories)} empirical trajectory matrices from NPZ.")

        # Fail explicitly if no real data is found - NEVER use synthetic noise
        if len(self.trajectories) == 0:
            raise FileNotFoundError(
                f"FATAL: No empirical trajectory datasets found at '{data_path}' or '{npz_path}'. "
                "Synthetic fallbacks are disabled to prevent training on mock data. "
                "Ensure data/empirical_trajectories.jsonl is populated."
            )

        # Build pair transitions (M_t -> M_{t+1})
        self.transitions = []
        for traj in self.trajectories:
            for t in range(len(traj) - 1):
                self.transitions.append((traj[t], traj[t+1]))

        print(f"[Dataset] Total authentic empirical transitions (M_t -> M_{{t+1}}): {len(self.transitions)}")

    def __len__(self):
        return len(self.transitions)

    def __getitem__(self, idx):
        m_t, m_next = self.transitions[idx]
        delta = m_next - m_t
        return torch.tensor(m_t, dtype=torch.float32), torch.tensor(delta, dtype=torch.float32), torch.tensor(m_next, dtype=torch.float32)

def train_sfl_manifold(
    data_path="data/empirical_trajectories.jsonl",
    output_path="sfl_model_3x3.pt",
    epochs=25,
    batch_size=32,
    lr=1e-3
):
    print("=" * 65)
    print("SFL MANIFOLD DRIFT MODEL - AUTHENTIC EMPIRICAL TRAINING")
    print("=" * 65)

    dataset = EmpiricalSFLDataset(data_path=data_path)
    dataloader = DataLoader(dataset, batch_size=batch_size, shuffle=True)

    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    print(f"[Device] Using {device} for training.")

    model = SFLManifoldTransformer(input_dim=9).to(device)
    optimizer = torch.optim.AdamW(model.parameters(), lr=lr, weight_decay=1e-4)
    scheduler = torch.optim.lr_scheduler.CosineAnnealingLR(optimizer, T_max=epochs)
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
            
            # Loss: MSE on step delta + Cosine alignment on resulting next state
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
            print(f"Epoch {epoch:02d}/{epochs} | Loss: {avg_loss:.6f} | LR: {scheduler.get_last_lr()[0]:.6f}")

    torch.save(model.state_dict(), output_path)
    print("\n" + "=" * 65)
    print(f"[Success] Checkpoint saved directly to {output_path}")
    print("=" * 65 + "\n")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Train SFL Manifold Drift Transformer on Empirical Datasets.")
    parser.add_argument("--data_path", type=str, default="data/empirical_trajectories.jsonl", help="Path to empirical JSONL")
    parser.add_argument("--output_path", type=str, default="sfl_model_3x3.pt", help="Path to save model weights")
    parser.add_argument("--epochs", type=int, default=25, help="Number of training epochs")
    parser.add_argument("--batch_size", type=int, default=32, help="Batch size")
    parser.add_argument("--lr", type=float, default=1e-3, help="Learning rate")
    args = parser.parse_args()

    train_sfl_manifold(
        data_path=args.data_path,
        output_path=args.output_path,
        epochs=args.epochs,
        batch_size=args.batch_size,
        lr=args.lr
    )
