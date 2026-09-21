"""
traincore.py — Production Supervised Training Loop for 3x3 LASSM
Task Agent 2 & 3: Supervised Continuous Optimization & Live Generation Debugger
Architecture: Language As Social Semiotic Model (LASSM)

Core Architecture:
    SFLMeaningTransformer: 9D Input -> W_adapt (d_model) -> 1536 MLP -> d_model -> 9D Output

Objective Function:
    L_total = L_SFL + lambda_sp * L_sp
    - L_SFL: Mean Squared Error against empirical 9D target trajectories
    - L_sp:  Semiotic manifold path loss (gradient smoothness / trajectory regularization)
"""

import os
import json
import argparse
from typing import List, Tuple
import numpy as np
import torch
import torch.nn as nn
from torch.utils.data import Dataset, DataLoader


class SFLMeaningTransformer(nn.Module):
    """
    Continuous neural transformer core operating over continuous 3x3 semiotic states.
    Projects unrolled 9D coordinates into hidden space and predicts next-step state.
    """
    def __init__(self, in_features: int = 9, d_model: int = 768, hidden_dim: int = 1536):
        super().__init__()
        self.w_adapt = nn.Linear(in_features, d_model)
        self.fc1 = nn.Linear(d_model, hidden_dim)
        self.act1 = nn.ReLU()
        self.fc2 = nn.Linear(hidden_dim, d_model)
        self.act2 = nn.ReLU()
        self.w_out = nn.Linear(d_model, in_features)

    def forward(self, m: torch.Tensor) -> torch.Tensor:
        h0 = self.w_adapt(m)
        h1 = self.act1(self.fc1(h0))
        h2 = self.act2(self.fc2(h1))
        mout = torch.clamp(self.w_out(h2), -1.0, 1.0)
        return mout


class EmpiricalTrajectoryDataset(Dataset):
    """
    Loads sequential (m_t, m_{t+1}) continuous coordinate pairs from data/empirical_trajectories.jsonl.
    """
    def __init__(self, jsonl_path: str):
        self.samples: List[Tuple[np.ndarray, np.ndarray]] = []
        if not os.path.exists(jsonl_path):
            raise FileNotFoundError(f"Training dataset not found: {jsonl_path}. Run ingest_corpus.py first.")

        records = []
        with open(jsonl_path, "r", encoding="utf-8") as f:
            for line in f:
                if line.strip():
                    records.append(json.loads(line))

        for i in range(len(records) - 1):
            curr_vec = np.array(records[i]["vector_9d"], dtype=np.float32)
            next_vec = np.array(records[i+1]["vector_9d"], dtype=np.float32)
            self.samples.append((curr_vec, next_vec))

    def __len__(self):
        return len(self.samples)

    def __getitem__(self, idx):
        m_curr, m_next = self.samples[idx]
        return torch.tensor(m_curr, dtype=torch.float32), torch.tensor(m_next, dtype=torch.float32)


def compute_path_loss(mout: torch.Tensor, minput: torch.Tensor) -> torch.Tensor:
    """
    Trajectory step displacement loss: ||mout - minput||_2^2
    """
    diff = mout - minput
    return torch.mean(torch.sum(diff ** 2, dim=-1))


def debug_generation(model: nn.Module, vocab_path: str, seed_vector: np.ndarray, top_k: int = 3):
    """
    Live Generation Debugger: Evaluates model prediction against empirical vocabulary centroids.
    """
    if not os.path.exists(vocab_path):
        print(f"Vocabulary centroids not found at {vocab_path}, skipping generation preview.")
        return

    with open(vocab_path, "r", encoding="utf-8") as f:
        vocab = json.load(f)

    model.eval()
    with torch.no_grad():
        inp = torch.tensor(seed_vector, dtype=torch.float32).unsqueeze(0)
        pred_out = model(inp).squeeze(0).cpu().numpy()

    distances = []
    for word, entry in vocab.items():
        centroid = np.array(entry["centroid_9d"], dtype=np.float32)
        dist = float(np.linalg.norm(pred_out - centroid))
        distances.append((word, dist))

    distances.sort(key=lambda x: x[1])
    print(f"\n--- [Task 3] Live Semiotic Boundary Realization Preview ---")
    print(f"Predicted 9D State Vector: {np.round(pred_out, 3).tolist()}")
    print("Closest Lexical Items:")
    for word, d in distances[:top_k]:
        print(f"  • '{word}' (Euclidean Distance: {d:.4f})")


def run_training():
    parser = argparse.ArgumentParser(description="Train SFLMeaningTransformer on Empirical Trajectories")
    parser.add_argument("--data_path", type=str, default="data/empirical_trajectories.jsonl", help="Path to empirical trajectories JSONL")
    parser.add_argument("--vocab_path", type=str, default="data/empirical_vocabulary_9d.json", help="Path to vocabulary centroids JSON")
    parser.add_argument("--epochs", type=int, default=10, help="Number of epochs")
    parser.add_argument("--lr", type=float, default=1e-4, help="AdamW learning rate")
    parser.add_argument("--batch_size", type=int, default=4, help="Batch size")
    parser.add_argument("--d_model", type=int, default=768, help="Hidden transformer dimension")
    parser.add_argument("--lambda_sp", type=float, default=0.1, help="Path loss weight")
    parser.add_argument("--save_path", type=str, default="sfl_model_3x3.pt", help="Checkpoint output file")
    args = parser.parse_args()

    device = "cuda" if torch.cuda.is_available() else "cpu"
    print(f"Training on device: {device} | d_model: {args.d_model} | epochs: {args.epochs}")

    if not os.path.exists(args.data_path):
        print(f"{args.data_path} not found. Running ingest_corpus.py to build empirical targets...")
        from ingest_corpus import run_corpus_ingestion, seed_corpus
        run_corpus_ingestion(seed_corpus)

    dataset = EmpiricalTrajectoryDataset(args.data_path)
    loader = DataLoader(dataset, batch_size=args.batch_size, shuffle=True)

    model = SFLMeaningTransformer(in_features=9, d_model=args.d_model).to(device)
    optimizer = torch.optim.AdamW(model.parameters(), lr=args.lr)
    criterion = nn.MSELoss()

    print("--- [Task 2] Starting Supervised Semiotic Optimization ---")
    for epoch in range(1, args.epochs + 1):
        model.train()
        total_loss, total_sfl, total_sp = 0.0, 0.0, 0.0
        
        for m_in, m_target in loader:
            m_in, m_target = m_in.to(device), m_target.to(device)
            optimizer.zero_grad()
            
            mout = model(m_in)
            l_sfl = criterion(mout, m_target)
            l_sp = compute_path_loss(mout, m_in)
            l_total = l_sfl + args.lambda_sp * l_sp
            
            l_total.backward()
            optimizer.step()
            
            total_loss += l_total.item() * len(m_in)
            total_sfl += l_sfl.item() * len(m_in)
            total_sp += l_sp.item() * len(m_in)

        n = len(loader.dataset)
        print(f"Epoch {epoch:02d} | Total Loss: {total_loss/n:.4f} | SFL MSE: {total_sfl/n:.4f} | Path Loss: {total_sp/n:.4f}")

    torch.save(model.state_dict(), args.save_path)
    print(f"\nModel checkpoint saved successfully to {args.save_path}")

    seed_vec, _ = dataset[0]
    debug_generation(model, args.vocab_path, seed_vec.numpy())


if __name__ == "__main__":
    run_training()
