"""Train SFL-pi from random initialisation on empirical 9D trajectories."""
import argparse
import json
import random
from pathlib import Path

import numpy as np
import torch
from torch import nn
from torch.utils.data import DataLoader, Dataset

from sfl_pi_model import SFLPi, SFLPiConfig


class TrajectoryDataset(Dataset):
    def __init__(self, path: Path, max_seq_len: int):
        self.items = []
        with path.open() as handle:
            for line in handle:
                if not line.strip():
                    continue
                item = json.loads(line)
                states = item.get("states", item.get("trajectory", item)) if isinstance(item, dict) else item
                if isinstance(states, dict):
                    states = states.get("vector_9d")
                array = np.asarray(states, dtype=np.float32)
                if array.ndim != 2 or array.shape[1] != 9 or array.shape[0] < 2:
                    continue
                self.items.append(array[:max_seq_len])
        if not self.items:
            raise RuntimeError(f"no 9D trajectories of length >=2 in {path}")

    def __len__(self):
        return len(self.items)

    def __getitem__(self, index):
        return torch.from_numpy(self.items[index])


def collate(batch):
    longest = max(x.size(0) for x in batch)
    states = torch.zeros(len(batch), longest, 9)
    valid = torch.zeros(len(batch), longest, dtype=torch.bool)
    for i, item in enumerate(batch):
        states[i, :item.size(0)] = item
        valid[i, :item.size(0)] = True
    return states, valid


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--data", default="data/empirical_trajectories.jsonl")
    parser.add_argument("--output", default="artifacts/sfl_pi")
    parser.add_argument("--epochs", type=int, default=25)
    parser.add_argument("--batch-size", type=int, default=16)
    parser.add_argument("--lr", type=float, default=3e-4)
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--d-model", type=int, default=128)
    parser.add_argument("--layers", type=int, default=4)
    parser.add_argument("--heads", type=int, default=4)
    parser.add_argument("--max-seq-len", type=int, default=64)
    args = parser.parse_args()

    random.seed(args.seed)
    np.random.seed(args.seed)
    torch.manual_seed(args.seed)
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    dataset = TrajectoryDataset(Path(args.data), args.max_seq_len)
    loader = DataLoader(dataset, batch_size=args.batch_size, shuffle=True, collate_fn=collate)
    cfg = SFLPiConfig(d_model=args.d_model, n_layers=args.layers, n_heads=args.heads, max_seq_len=args.max_seq_len)
    model = SFLPi(cfg).to(device)
    optimiser = torch.optim.AdamW(model.parameters(), lr=args.lr, weight_decay=0.01)
    criterion = nn.MSELoss(reduction="none")
    output = Path(args.output)
    output.mkdir(parents=True, exist_ok=True)
    history = []

    for epoch in range(1, args.epochs + 1):
        model.train()
        total_loss = 0.0
        total_steps = 0
        for states, valid in loader:
            states, valid = states.to(device), valid.to(device)
            prediction = model(states[:, :-1])
            target = states[:, 1:]
            mask = valid[:, 1:].unsqueeze(-1).float()
            loss = (criterion(prediction, target) * mask).sum() / mask.sum().clamp_min(1.0)
            optimiser.zero_grad(set_to_none=True)
            loss.backward()
            torch.nn.utils.clip_grad_norm_(model.parameters(), 1.0)
            optimiser.step()
            total_loss += loss.item()
            total_steps += 1
        epoch_loss = total_loss / max(total_steps, 1)
        history.append({"epoch": epoch, "next_state_mse": epoch_loss})
        print(json.dumps(history[-1]))

    torch.save({"model_state": model.state_dict(), "config": cfg.__dict__, "history": history}, output / "sfl_pi_random_init.pt")
    (output / "metrics.json").write_text(json.dumps({"device": str(device), "parameters": model.parameter_count(), "examples": len(dataset), "history": history}, indent=2))


if __name__ == "__main__":
    main()