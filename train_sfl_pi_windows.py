"""Windowed next-state training for the 9D meaning-state data.

Same model and objective as train_sfl_pi.py (SFL-pi, next-state
prediction). The difference is data coverage: instead of loading one
trajectory truncated to max_seq_len, this script builds sliding windows
over ALL records and holds out the final 20% of records for evaluation.

Writes: run_manifest.json, metrics.json, heldout_evaluation.json,
run_report.md and sfl_pi_windows.pt to the output directory.

Run: python train_sfl_pi_windows.py
"""
import argparse
import json
import random
from pathlib import Path

import numpy as np
import torch
from torch import nn
from torch.utils.data import DataLoader, Dataset

from sfl_pi_model import SFLPi, SFLPiConfig

STATE_DIM = 9


class WindowDataset(Dataset):
    """Sliding windows over one ordered block of meaning-state records."""

    def __init__(self, vectors, window):
        self.windows = []
        for start in range(0, len(vectors) - window + 1):
            self.windows.append(vectors[start:start + window])

    def __len__(self):
        return len(self.windows)

    def __getitem__(self, index):
        return torch.from_numpy(self.windows[index].copy())


def collate(batch):
    longest = max(x.size(0) for x in batch)
    states = torch.zeros(len(batch), longest, STATE_DIM)
    valid = torch.zeros(len(batch), longest, dtype=torch.bool)
    for i, item in enumerate(batch):
        states[i, :item.size(0)] = item
        valid[i, :item.size(0)] = True
    return states, valid


def load_vectors(path):
    vectors = []
    with Path(path).open() as handle:
        for line in handle:
            line = line.strip()
            if not line:
                continue
            item = json.loads(line)
            if isinstance(item, dict) and "vector_9d" in item:
                vectors.append([float(x) for x in item["vector_9d"]])
    if len(vectors) < 2:
        raise RuntimeError(f"fewer than 2 usable records in {path}")
    return np.asarray(vectors, dtype=np.float32)


def evaluate(model, vectors, device, window):
    """One-step and recursive rollout error on held-out records."""
    model.eval()
    observed = torch.from_numpy(vectors).to(device)
    with torch.no_grad():
        prefix = observed[:window].unsqueeze(0)
        one_step = model(prefix)[0, window - 1].cpu().numpy()
        predicted = [observed[0].clone()]
        for _ in range(1, vectors.shape[0]):
            history = torch.stack(predicted[-window:]).unsqueeze(0).to(device)
            predicted.append(model(history)[0, -1].detach().cpu())
        predicted = torch.stack(predicted).cpu().numpy()
    target = vectors[1:]
    one_step_mse = float(((one_step - target[window - 1]) ** 2).mean())
    recursive_mse = float(((predicted[1:] - target) ** 2).mean())
    return {
        "one_step_mse": one_step_mse,
        "recursive_mse": recursive_mse,
        "first_window_last_state_prediction": one_step.tolist(),
        "actual_next_state": vectors[window].tolist(),
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--data", default="data/empirical_trajectories.jsonl")
    parser.add_argument("--output", default="artifacts/sfl_pi_windows")
    parser.add_argument("--epochs", type=int, default=25)
    trainer = parser.add_argument("--batch-size", type=int, default=16)
    parser.add_argument("--lr", type=float, default=3e-4)
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--d-model", type=int, default=128)
    parser.add_argument("--layers", type=int, default=4)
    parser.add_argument("--heads", type=int, default=4)
    parser.add_argument("--window", type=int, default=64)
    parser.add_argument("--holdout", type=float, default=0.2)
    args = parser.parse_args()

    random.seed(args.seed)
    np.random.seed(args.seed)
    torch.manual_seed(args.seed)
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

    vectors = load_vectors(args.data)
    split = int(len(vectors) * (1 - args.holdout))
    train_vectors = vectors[:split]
    heldout_vectors = vectors[split:]
    train_set = WindowDataset(train_vectors, args.window)
    loader = DataLoader(train_set, batch_size=args.batch_size, shuffle=True, collate_fn=collate)

    cfg = SFLPiConfig(d_model=args.d_model, n_layers=args.layers, n_heads=args.heads, max_seq_len=args.window)
    model = SFLPi(cfg).to(device)
    optimiser = torch.optim.AdamW(model.parameters(), lr=args.lr, weight_decay=0.01)
    criterion = nn.MSELoss(reduction="none")
    output = Path(args.output)
    output.mkdir(parents=True, exist_ok=True)

    manifest = {
        "data_path": str(Path(args.data)),
        "total_records": int(len(vectors)),
        "train_records": int(split),
        "heldout_records": int(len(vectors) - split),
        "train_windows": len(train_set),
        "window": args.window,
        "seed": args.seed,
        "device": str(device),
        "config": vars(args),
        "model_config": cfg.__dict__,
        "parameter_count": model.parameter_count(),
        "objective": "next meaning state from state history (as in train_sfl_pi.py)",
        "data_note": "one uninterrupted block; document boundaries unknown",
    }
    (output / "run_manifest.json").write_text(json.dumps(manifest, indent=2))

    history = []
    for epoch in range(1, args.epochs + 1):
        model.train()
        total = 0.0
        count = 0
        for states, valid in loader:
            states, valid = states.to(device), valid.to(device)
            prediction = model(states[:, :-1])
            target = states[:, 1:]
            mask = valid[:, 1:].unsqueeze(-1)
            squared = criterion(prediction, target) * mask
            loss = squared.sum() / mask.sum().clamp_min(1).float() / STATE_DIM
            optimiser.zero_grad(set_to_none=True)
            loss.backward()
            torch.nn.utils.clip_grad_norm_(model.parameters(), 1.0)
            optimiser.step()
            total += float(loss.item())
            count += 1
        epoch_loss = total / max(count, 1)
        history.append({"epoch": epoch, "mean_coordinate_mse": epoch_loss})
        print(json.dumps(history[-1]))

    delta_baseline = float((np.diff(heldout_vectors, axis=0) ** 2).mean())
    evaluation = evaluate(model, heldout_vectors, device, args.window)
    evaluation["no_change_baseline_mse"] = delta_baseline
    metrics = {"history": history, "heldout": evaluation}
    (output / "metrics.json").write_text(json.dumps(metrics, indent=2))

    report = [
        "# Windowed SFL-pi run",
        "",
        f"- Records: {manifest['total_records']} (train {manifest['train_records']}, held-out {manifest['heldout_records']})",
        f"- Training windows: {manifest['train_windows']} of length {args.window}",
        f"- Objective: next meaning state from state history",
        f"- Final training loss (mean coordinate MSE): {history[-1]['mean_coordinate_mse']:.8f}",
        f"- Held-out one-step MSE: {evaluation['one_step_mse']:.8f}",
        f"- Held-out recursive rollout MSE: {evaluation['recursive_mse']:.8f}",
        f"- No-change baseline MSE (held-out): {delta_baseline:.8f}",
        "",
        "The model is only informative if its held-out errors beat the no-change baseline.",
        "",
    ]
    (output / "run_report.md").write_text("\n".join(report))
    torch.save({"model_state": model.state_dict(), "config": cfg.__dict__, "manifest": manifest, "history": history}, output / "sfl_pi_windows.pt")
    print(f"checkpoint and report written to {output}")


if __name__ == "__main__":
    main()
