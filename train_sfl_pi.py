"""Train SFL-pi from random initialisation on empirical 9D trajectories and record inspectable run evidence."""
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


class TrajectoryDataset(Dataset):
    def __init__(self, path: Path, max_seq_len: int):
        self.items = []
        self.source_lines = []
        trajectory_states = []
        trajectory_start_line = None

        def finish_trajectory():
            nonlocal trajectory_states, trajectory_start_line
            if len(trajectory_states) >= 2:
                array = np.stack(trajectory_states)[:max_seq_len]
                if array.shape[0] >= 2:
                    self.items.append(array)
                    self.source_lines.append(trajectory_start_line)
            trajectory_states = []
            trajectory_start_line = None

        with path.open() as handle:
            for line_number, line in enumerate(handle, start=1):
                if not line.strip():
                    continue
                try:
                    item = json.loads(line)
                except json.JSONDecodeError:
                    finish_trajectory()
                    continue

                if isinstance(item, dict):
                    explicit_key = next((key for key in ("states", "trajectory") if key in item), None)
                    if explicit_key is not None:
                        finish_trajectory()
                        explicit_states = item[explicit_key]
                        try:
                            array = np.asarray(explicit_states, dtype=np.float32)
                        except (TypeError, ValueError):
                            continue
                        if array.ndim == 2 and array.shape[1] == STATE_DIM and array.shape[0] >= 2:
                            array = array[:max_seq_len]
                            if array.shape[0] >= 2:
                                self.items.append(array)
                                self.source_lines.append(line_number)
                        continue

                    vector = item.get("vector_9d")
                    if (
                        not isinstance(vector, list)
                        or len(vector) != STATE_DIM
                        or any(isinstance(value, bool) or not isinstance(value, (int, float)) for value in vector)
                    ):
                        finish_trajectory()
                        continue
                    try:
                        state = np.asarray(vector, dtype=np.float32)
                    except (OverflowError, TypeError, ValueError):
                        finish_trajectory()
                        continue
                    if not np.isfinite(state).all():
                        finish_trajectory()
                        continue
                    if trajectory_start_line is None:
                        trajectory_start_line = line_number
                    trajectory_states.append(state)
                    continue

                finish_trajectory()
                array = np.asarray(item, dtype=np.float32)
                if array.ndim == 2 and array.shape[1] == STATE_DIM and array.shape[0] >= 2:
                    array = array[:max_seq_len]
                    if array.shape[0] >= 2:
                        self.items.append(array)
                        self.source_lines.append(line_number)

        finish_trajectory()
        ordered = sorted(zip(self.source_lines, self.items), key=lambda entry: entry[0])
        self.source_lines = [line_number for line_number, _ in ordered]
        self.items = [array for _, array in ordered]
        if not self.items:
            raise RuntimeError(f"no 9D trajectories of length >=2 in {path}")

    def __len__(self):
        return len(self.items)

    def __getitem__(self, index):
        return torch.from_numpy(self.items[index])


def collate(batch):
    longest = max(x.size(0) for x in batch)
    states = torch.zeros(len(batch), longest, STATE_DIM)
    valid = torch.zeros(len(batch), longest, dtype=torch.bool)
    for i, item in enumerate(batch):
        states[i, :item.size(0)] = item
        valid[i, :item.size(0)] = True
    return states, valid


def finite_list(value):
    return np.nan_to_num(value, nan=0.0, posinf=0.0, neginf=0.0).tolist()


def rollout(model, observed, device):
    model.eval()
    predicted = [observed[0].clone()]
    with torch.no_grad():
        for _ in range(1, observed.size(0)):
            prefix = torch.stack(predicted).unsqueeze(0).to(device)
            next_state = model(prefix)[0, -1].detach().cpu()
            predicted.append(next_state)
    return torch.stack(predicted)


def inspect_trajectories(model, dataset, device, sample_count):
    indices = np.linspace(0, len(dataset) - 1, num=min(sample_count, len(dataset)), dtype=int)
    inspections = []
    model.eval()
    for index in indices.tolist():
        observed = dataset[index]
        with torch.no_grad():
            teacher_forced = model(observed[:-1].unsqueeze(0).to(device))[0].detach().cpu()
        generated = rollout(model, observed, device)
        target = observed[1:]
        one_step_error = (teacher_forced - target).pow(2).mean(dim=0)
        rollout_error = (generated[1:] - target).pow(2).mean(dim=0)
        inspections.append({
            "dataset_index": index,
            "source_line": dataset.source_lines[index],
            "length": int(observed.size(0)),
            "observed_states": finite_list(observed.numpy()),
            "next_state_targets": finite_list(target.numpy()),
            "teacher_forced_predictions": finite_list(teacher_forced.numpy()),
            "autoregressive_rollout": finite_list(generated.numpy()),
            "one_step_mse_by_coordinate": finite_list(one_step_error.numpy()),
            "rollout_mse_by_coordinate": finite_list(rollout_error.numpy()),
            "rollout_mse_by_step": finite_list((generated[1:] - target).pow(2).mean(dim=1).numpy()),
            "teacher_forced_finite": bool(torch.isfinite(teacher_forced).all()),
            "rollout_finite": bool(torch.isfinite(generated).all()),
            "observed_coordinate_min": finite_list(observed.min(dim=0).values.numpy()),
            "observed_coordinate_max": finite_list(observed.max(dim=0).values.numpy()),
            "rollout_coordinate_min": finite_list(generated.min(dim=0).values.numpy()),
            "rollout_coordinate_max": finite_list(generated.max(dim=0).values.numpy()),
        })
    return inspections


def write_report(path, manifest, metrics, inspections):
    final = metrics["history"][-1] if metrics["history"] else {}
    lines = [
        "# SFL-pi Full-Run Inspection",
        "",
        "## Run",
        "",
        f"- Device: `{manifest['device']}`",
        f"- Seed: `{manifest['seed']}`",
        f"- Dataset: `{manifest['data_path']}`",
        f"- Accepted trajectories: {manifest['accepted_trajectories']}",
        f"- Sequence lengths: min={manifest['sequence_lengths']['min']}, max={manifest['sequence_lengths']['max']}, mean={manifest['sequence_lengths']['mean']:.2f}",
        f"- Model parameters: {manifest['parameter_count']}",
        "",
        "## Final epoch",
        "",
        f"- Next-state MSE: {final.get('next_state_mse', float('nan')):.8f}",
        f"- Non-finite predictions observed during training: {final.get('non_finite_predictions', 0)}",
        "",
        "## Inspection artifacts",
        "",
        f"- `{len(inspections)}` real trajectories were inspected; their source JSONL lines are recorded in `trajectory_inspection.json`.",
        "- Each inspection contains observed states, teacher-forced next-state predictions, autoregressive rollouts, coordinate-level MSE, step-level rollout MSE, and coordinate ranges.",
        "- Read the recorded trajectories before selecting the next architectural intervention; do not treat this report as a pass/fail result.",
    ]
    path.write_text("\n".join(lines) + "\n")


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
    parser.add_argument("--inspect-trajectories", type=int, default=8)
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

    lengths = np.asarray([item.shape[0] for item in dataset.items], dtype=np.int64)
    manifest = {
        "data_path": str(Path(args.data)),
        "seed": args.seed,
        "device": str(device),
        "config": vars(args),
        "model_config": cfg.__dict__,
        "parameter_count": model.parameter_count(),
        "accepted_trajectories": len(dataset),
        "sequence_lengths": {"min": int(lengths.min()), "max": int(lengths.max()), "mean": float(lengths.mean())},
    }
    (output / "run_manifest.json").write_text(json.dumps(manifest, indent=2))

    for epoch in range(1, args.epochs + 1):
        model.train()
        total_squared_error = torch.zeros(STATE_DIM, device=device)
        total_valid_states = 0
        non_finite_predictions = 0
        for states, valid in loader:
            states, valid = states.to(device), valid.to(device)
            prediction = model(states[:, :-1])
            target = states[:, 1:]
            mask = valid[:, 1:].unsqueeze(-1)
            non_finite_predictions += int((~torch.isfinite(prediction)).sum().item())
            if not torch.isfinite(prediction).all():
                raise RuntimeError(f"non-finite prediction at epoch {epoch}")
            squared_error = criterion(prediction, target)
            masked_error = squared_error * mask
            loss = masked_error.sum() / mask.sum().clamp_min(1).float()
            optimiser.zero_grad(set_to_none=True)
            loss.backward()
            torch.nn.utils.clip_grad_norm_(model.parameters(), 1.0)
            optimiser.step()
            total_squared_error += masked_error.sum(dim=(0, 1))
            total_valid_states += int(mask.sum().item())
        coordinate_mse = total_squared_error / max(total_valid_states, 1)
        history.append({
            "epoch": epoch,
            "next_state_mse": float(coordinate_mse.mean().item()),
            "next_state_mse_by_coordinate": finite_list(coordinate_mse.detach().cpu().numpy()),
            "non_finite_predictions": non_finite_predictions,
        })
        print(json.dumps(history[-1]))

    inspections = inspect_trajectories(model, dataset, device, args.inspect_trajectories)
    metrics = {"history": history}
    (output / "metrics.json").write_text(json.dumps(metrics, indent=2))
    (output / "trajectory_inspection.json").write_text(json.dumps(inspections, indent=2))
    write_report(output / "run_report.md", manifest, metrics, inspections)
    torch.save({"model_state": model.state_dict(), "config": cfg.__dict__, "manifest": manifest, "history": history}, output / "sfl_pi_random_init.pt")


if __name__ == "__main__":
    main()
