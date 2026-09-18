"""Small reproducible LASSM transition experiment.
The included annotations are heuristic seed data, not a validated corpus.
Run: python experiments/lassm_baseline_comparison.py
"""
import csv
import json
import random
from pathlib import Path

import torch
from torch import nn
from torch.utils.data import DataLoader, TensorDataset

SEED = 42
ROOT = Path(__file__).resolve().parents[1]
DATA_PATH = ROOT / "data" / "seed_turn_transitions.csv"
OUT_PATH = ROOT / "experiments" / "results_seed_transition.json"
AXES = ["ideational", "field", "interpersonal", "tenor", "textual", "mode"]


def load_data(path):
    with path.open(newline="", encoding="utf-8") as handle:
        rows = list(csv.DictReader(handle))
    x = torch.tensor([[float(row[f"src_{axis}"]) for axis in AXES] for row in rows])
    y = torch.tensor([[float(row[f"tgt_{axis}"]) for axis in AXES] for row in rows])
    return x, y


class BaselineMLP(nn.Module):
    def __init__(self):
        super().__init__()
        self.net = nn.Sequential(nn.Linear(6, 32), nn.ReLU(), nn.Linear(32, 6))

    def forward(self, x):
        return self.net(x)


class StructuredLASSM(nn.Module):
    """Uses a 3x2 state plus intrinsic register/metafunction covariance features."""
    def __init__(self):
        super().__init__()
        self.adapter = nn.Sequential(nn.Linear(19, 32), nn.ReLU(), nn.Linear(32, 6))

    def forward(self, x):
        matrix = x.reshape(-1, 3, 2)
        c_reg = matrix.transpose(1, 2) @ matrix
        c_meta = matrix @ matrix.transpose(1, 2)
        features = torch.cat((x, c_reg.flatten(1), c_meta.flatten(1)), dim=1)
        return self.adapter(features)


def train_and_evaluate(factory, x_train, y_train, x_test, y_test):
    model = factory()
    optimizer = torch.optim.AdamW(model.parameters(), lr=1e-2, weight_decay=1e-4)
    loader = DataLoader(TensorDataset(x_train, y_train), batch_size=4, shuffle=True)
    for _ in range(300):
        for x_batch, y_batch in loader:
            loss = nn.functional.mse_loss(model(x_batch), y_batch)
            optimizer.zero_grad()
            loss.backward()
            optimizer.step()
    with torch.no_grad():
        prediction = model(x_test)
        axis_mse = ((prediction - y_test) ** 2).mean(dim=0)
        total_mse = axis_mse.mean()
        path_error = torch.linalg.vector_norm(prediction - y_test, dim=1).mean()
    return {"mse": float(total_mse), "mean_path_error": float(path_error),
            "mse_by_axis": dict(zip(AXES, map(float, axis_mse)))}


def main():
    random.seed(SEED)
    torch.manual_seed(SEED)
    x, y = load_data(DATA_PATH)
    indices = torch.randperm(len(x), generator=torch.Generator().manual_seed(SEED))
    split = int(0.75 * len(x))
    train_idx, test_idx = indices[:split], indices[split:]
    results = {
        "dataset": {"name": "seed_turn_transitions", "n_examples": len(x),
                    "train_examples": len(train_idx), "test_examples": len(test_idx),
                    "annotation_status": "heuristic seed annotations; not validated"},
        "baseline_mlp": train_and_evaluate(BaselineMLP, x[train_idx], y[train_idx], x[test_idx], y[test_idx]),
        "structured_lassm": train_and_evaluate(StructuredLASSM, x[train_idx], y[train_idx], x[test_idx], y[test_idx]),
    }
    OUT_PATH.write_text(json.dumps(results, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(results, indent=2))
    print(f"Saved results to {OUT_PATH.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
