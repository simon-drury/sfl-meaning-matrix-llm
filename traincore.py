"""
traincore.py - SFL Meaning Matrix Manifold Training Pipeline
Trains a Transformer on meaning trajectories (M_t -> Delta_{t+1})
respecting document boundaries from uam_meaning_trajectories.npz.
"""

import os
import argparse
import numpy as np
import torch
import torch.nn as nn
from torch.utils.data import Dataset, DataLoader

class UAMTrajectoryDataset(Dataset):
    def __init__(self, npz_path="uam_meaning_trajectories.npz", matrix_dim=9):
        super().__init__()
        self.samples = []
        if not os.path.exists(npz_path):
            raise FileNotFoundError(f"Trajectory file not found: {npz_path}")
        
        data = np.load(npz_path, allow_pickle=True)
        keys = data.files
        for key in keys:
            traj = data[key]
            traj = np.array(traj, dtype=np.float32)
            if traj.ndim == 3:
                for single_traj in traj:
                    self._extract_pairs(single_traj, matrix_dim)
            elif traj.ndim == 2:
                self._extract_pairs(traj, matrix_dim)

        print(f"[Dataset] Loaded {len(self.samples)} boundary-safe transitions from {npz_path}")

    def _extract_pairs(self, traj, matrix_dim):
        if traj.shape[-1] != matrix_dim and traj.size % matrix_dim == 0:
            traj = traj.reshape(-1, matrix_dim)
        
        T = traj.shape[0]
        for t in range(T - 1):
            m_t = traj[t]
            m_next = traj[t + 1]
            delta = m_next - m_t
            self.samples.append((m_t, delta))

    def __len__(self):
        return len(self.samples)

    def __getitem__(self, idx):
        m_t, delta = self.samples[idx]
        return torch.tensor(m_t, dtype=torch.float32), torch.tensor(delta, dtype=torch.float32)


class SFLManifoldTransformer(nn.Module):
    def __init__(self, input_dim=9, d_model=64, nhead=4, num_layers=3, dim_feedforward=128):
        super().__init__()
        self.in_proj = nn.Linear(input_dim, d_model)
        encoder_layer = nn.TransformerEncoderLayer(
            d_model=d_model, nhead=nhead, dim_feedforward=dim_feedforward, batch_first=True
        )
        self.transformer = nn.TransformerEncoder(encoder_layer, num_layers=num_layers)
        self.out_proj = nn.Linear(d_model, input_dim)

    def forward(self, x):
        h = self.in_proj(x).unsqueeze(1)
        h = self.transformer(h)
        delta = self.out_proj(h.squeeze(1))
        return delta


def train(args):
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    print(f"[Train] Using device: {device}")

    dataset = UAMTrajectoryDataset(args.data_path, matrix_dim=args.dim)
    dataloader = DataLoader(dataset, batch_size=args.batch_size, shuffle=True)

    model = SFLManifoldTransformer(input_dim=args.dim, d_model=args.d_model).to(device)
    optimizer = torch.optim.AdamW(model.parameters(), lr=args.lr, weight_decay=1e-4)
    criterion = nn.MSELoss()

    model.train()
    for epoch in range(args.epochs):
        total_loss = 0.0
        for m_t, delta in dataloader:
            m_t, delta = m_t.to(device), delta.to(device)

            optimizer.zero_grad()
            pred_delta = model(m_t)
            loss = criterion(pred_delta, delta)
            loss.backward()
            optimizer.step()

            total_loss += loss.item() * len(m_t)

        avg_loss = total_loss / len(dataset)
        if (epoch + 1) % max(1, args.epochs // 10) == 0 or epoch == 0:
            print(f"Epoch {epoch+1:03d}/{args.epochs:03d} | Geodesic Delta Loss: {avg_loss:.6f}")

    torch.save(model.state_dict(), args.save_path)
    print(f"[Done] Model saved successfully to {args.save_path}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Train SFL manifold model on meaning trajectories.")
    parser.add_argument("--data_path", type=str, default="uam_meaning_trajectories.npz", help="Path to trajectory NPZ")
    parser.add_argument("--save_path", type=str, default="sfl_model_3x3.pt", help="Checkpoint destination")
    parser.add_argument("--dim", type=int, default=9, help="Flat dimension of meaning matrix (9 for 3x3, 6 for 3x2)")
    parser.add_argument("--d_model", type=int, default=64, help="Transformer latent dimension")
    parser.add_argument("--epochs", type=int, default=50, help="Training epochs")
    parser.add_argument("--batch_size", type=int, default=32, help="Batch size")
    parser.add_argument("--lr", type=float, default=1e-3, help="Learning rate")
    args = parser.parse_args()

    train(args)
