"""
traincore.py — Production Supervised Training Loop for 3x3 LASSM
Architecture: Language As Social Semiotic Model (LASSM)
Core: SFLMeaningTransformer (9D Input -> 768 d_model -> 1536 MLP -> 768 -> 9D Output)

Optimizes:
    L_total = L_SFL + lambda * L_sp
Where:
    L_SFL = MSE(mout, mtarget)
    L_sp  = Trajectory Path Loss (Semiotic Smoothness)
"""

import os
import argparse
import numpy as np
import torch
import torch.nn as nn
from torch.utils.data import Dataset, DataLoader


class SFLMeaningTransformer(nn.Module):
    """
    Continuous semiotic feedforward transformer core.
    Adapts 9D semiotic states into hidden space d_model and predicts next state.
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


class SemioticTrajectoryDataset(Dataset):
    """
    Trajectory dataset providing (m_input_t, m_target_{t+1}) pairs from gold matrices.
    """
    def __init__(self, trajectories: list):
        self.samples = []
        for traj in trajectories:
            for t in range(len(traj) - 1):
                self.samples.append((traj[t], traj[t+1]))

    def __len__(self):
        return len(self.samples)

    def __getitem__(self, idx):
        m_curr, m_next = self.samples[idx]
        return torch.tensor(m_curr, dtype=torch.float32), torch.tensor(m_next, dtype=torch.float32)


def compute_path_loss(mout: torch.Tensor, minput: torch.Tensor) -> torch.Tensor:
    """
    Batch step displacement path loss: ||mout - minput||_2^2
    """
    diff = mout - minput
    return torch.mean(torch.sum(diff ** 2, dim=-1))


def train_epoch(
    model: nn.Module,
    loader: DataLoader,
    optimizer: torch.optim.Optimizer,
    criterion: nn.Module,
    lambda_sp: float = 0.1,
    device: str = "cpu"
) -> tuple[float, float, float]:
    model.train()
    total_loss, total_sfl, total_sp = 0.0, 0.0, 0.0
    
    for m_in, m_target in loader:
        m_in, m_target = m_in.to(device), m_target.to(device)
        
        optimizer.zero_grad()
        mout = model(m_in)
        
        l_sfl = criterion(mout, m_target)
        l_sp = compute_path_loss(mout, m_in)
        l_total = l_sfl + lambda_sp * l_sp
        
        l_total.backward()
        optimizer.step()
        
        total_loss += l_total.item() * len(m_in)
        total_sfl += l_sfl.item() * len(m_in)
        total_sp += l_sp.item() * len(m_in)
        
    n = len(loader.dataset)
    return total_loss / n, total_sfl / n, total_sp / n


def run_training():
    parser = argparse.ArgumentParser(description="Train 3x3 SFLMeaningTransformer")
    parser.add_argument("--epochs", type=int, default=5, help="Number of training epochs")
    parser.add_argument("--lr", type=float, default=1e-4, help="Learning rate for AdamW")
    parser.add_argument("--batch_size", type=int, default=16, help="Batch size")
    parser.add_argument("--d_model", type=int, default=768, help="Transformer hidden dimension")
    parser.add_argument("--lambda_sp", type=float, default=0.1, help="Path loss penalty weight")
    parser.add_argument("--save_path", type=str, default="sfl_model_3x3.pt", help="Checkpoint save path")
    args = parser.parse_args()

    device = "cuda" if torch.cuda.is_available() else "cpu"
    print(f"Training on device: {device} | d_model: {args.d_model} | epochs: {args.epochs}")

    np.random.seed(42)
    dummy_trajs = [np.random.uniform(-1.0, 1.0, size=(10, 9)).astype(np.float32) for _ in range(50)]
    dataset = SemioticTrajectoryDataset(dummy_trajs)
    loader = DataLoader(dataset, batch_size=args.batch_size, shuffle=True)

    model = SFLMeaningTransformer(in_features=9, d_model=args.d_model).to(device)
    optimizer = torch.optim.AdamW(model.parameters(), lr=args.lr)
    criterion = nn.MSELoss()

    print("--- Starting Supervised Semiotic Optimization ---")
    for epoch in range(1, args.epochs + 1):
        loss, sfl_loss, sp_loss = train_epoch(
            model, loader, optimizer, criterion, lambda_sp=args.lambda_sp, device=device
        )
        print(f"Epoch {epoch:02d} | Total Loss: {loss:.4f} | SFL MSE: {sfl_loss:.4f} | Path Loss: {sp_loss:.4f}")

    torch.save(model.state_dict(), args.save_path)
    print(f"Model saved successfully to {args.save_path}")


if __name__ == "__main__":
    run_training()
