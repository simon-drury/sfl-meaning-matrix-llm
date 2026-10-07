"""
interact.py - CLI pipeline for SFL Manifold Trajectory Inference & Grammatical Realization.
Directly integrates repository realization anchors and empirical vocabulary.
"""

import argparse
import json
import sys
from pathlib import Path
from typing import List, Tuple, Optional

import numpy as np
import torch
import torch.nn as nn

# Repository modules
from sfl_matrix_engine import MeaningMatrix, MeaningTrajectory, encode_en, encode_es
from sfl_manifold import SemanticManifold
from sfl_realize import Realizer
from sfl_adapter import SFLAdapter


def parse_vector_any(val):
    if val is None:
        return None
    if isinstance(val, (list, tuple)):
        flat = []
        for x in val:
            if isinstance(x, (list, tuple)):
                flat.extend(x)
            elif isinstance(x, (int, float)):
                flat.append(float(x))
        if len(flat) == 9:
            return np.array(flat, dtype=np.float32)
    elif isinstance(val, dict):
        for k in ["centroid", "vector", "coords", "matrix", "matrix_3x3", "m_9d", "values", "embedding", "point"]:
            if k in val:
                cand = parse_vector_any(val[k])
                if cand is not None:
                    return cand
    return None


class SFLPiModel(nn.Module):
    """Minimal next-step predictor over 9D meaning states (matches train_sfl_pi.py)."""

    def __init__(self, state_dim: int = 9, d_model: int = 128, nhead: int = 4, nlayers: int = 3, max_seq_len: int = 64):
        super().__init__()
        self.state_dim = state_dim
        self.d_model = d_model
        self.max_seq_len = max_seq_len
        self.in_proj = nn.Linear(state_dim, d_model)
        self.pos_encoder = nn.Parameter(torch.zeros(1, max_seq_len, d_model))
        encoder_layer = nn.TransformerEncoderLayer(d_model, nhead, dim_feedforward=d_model * 4, batch_first=True)
        self.encoder = nn.TransformerEncoder(encoder_layer, num_layers=nlayers)
        self.out_proj = nn.Linear(d_model, state_dim)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        """x: (batch, seq_len, state_dim) -> predicted next state (batch, state_dim)"""
        if x.dim() == 2:
            x = x.unsqueeze(1)
        b, s, _ = x.shape
        h = self.in_proj(x) + self.pos_encoder[:, :s, :]
        h = self.encoder(h)
        out = h[:, -1, :]  # last step
        delta = self.out_proj(out)
        return delta.squeeze(1) if s == 1 else delta


def load_trajectories_from_jsonl(jsonl_path: Path, max_seq_len: int = 32) -> List[np.ndarray]:
    """Load trajectories from JSONL file (one trajectory per line)."""
    trajectories = []
    with open(jsonl_path, 'r') as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                item = json.loads(line)
                # Expecting {"trajectory": [[9], [9], ...]} or {"vector_9d": [9], ...}
                vecs = item.get("trajectory") or item.get("vectors")
                if vecs is None:
                    # Single vector per line format
                    vec = item.get("vector_9d")
                    if vec is not None:
                        vecs = [vec]
                if vecs is None:
                    continue
                array = np.asarray(vecs, dtype=np.float32)
                if array.ndim == 2 and array.shape[1] == 9 and array.shape[0] >= 2:
                    array = array[:max_seq_len]
                    if array.shape[0] >= 2:
                        trajectories.append(array)
            except (json.JSONDecodeError, KeyError, ValueError):
                continue
    return trajectories


def train_pi_model(
    data_dir: Path,
    epochs: int = 25,
    batch_size: int = 32,
    lr: float = 1e-3,
    device: str = "cpu",
    model_path: Path = Path("sfl_pi_model.pt"),
):
    """Train the pi model on trajectory data."""
    trajectories = []
    for jsonl_file in data_dir.glob("*.jsonl"):
        trajectories.extend(load_trajectories_from_jsonl(jsonl_file))

    if not trajectories:
        print("No trajectories found.")
        return

    print(f"Loaded {len(trajectories)} trajectories")

    # Create training pairs (state_t -> state_{t+1})
    X_list = []
    y_list = []
    for traj in trajectories:
        for i in range(len(traj) - 1):
            X_list.append(traj[i])
            y_list.append(traj[i + 1])

    X = torch.tensor(np.stack(X_list), dtype=torch.float32)
    y = torch.tensor(np.stack(y_list), dtype=torch.float32)

    model = SFLPiModel().to(device)
    optimizer = torch.optim.Adam(model.parameters(), lr=lr)
    loss_fn = nn.MSELoss()

    model.train()
    for epoch in range(epochs):
        perm = torch.randperm(len(X))
        epoch_loss = 0.0
        for i in range(0, len(X), batch_size):
            idx = perm[i:i + batch_size]
            xb = X[idx].to(device)
            yb = y[idx].to(device)
            optimizer.zero_grad()
            pred = model(xb.unsqueeze(1))  # (batch, 1, 9) -> (batch, 9)
            loss = loss_fn(pred, yb)
            loss.backward()
            optimizer.step()
            epoch_loss += loss.item() * xb.size(0)
        epoch_loss /= len(X)
        if (epoch + 1) % 5 == 0 or epoch == 0:
            print(f"Epoch {epoch + 1}/{epochs} - Loss: {epoch_loss:.6f}")

    torch.save(model.state_dict(), model_path)
    print(f"Model saved to {model_path}")


def run_inference(prompt: str, lang: str = "en", use_pi: bool = False) -> str:
    """Run the full pipeline: encode -> trajectory -> realize."""
    if lang == "en":
        traj = encode_en(prompt)
    elif lang == "es":
        traj = encode_es(prompt)
    else:
        raise ValueError(f"Unsupported language: {lang}")

    manifold = SemanticManifold()
    realizer = Realizer()

    print(f"Prompt: {prompt}")
    print(f"Trajectory steps: {len(traj.states)}")
    for i, state in enumerate(traj.states):
        vec = state.to_vector()
        print(f"  t={i}: {state.label:<20} {np.round(vec, 3)}")

    # Geometric analysis
    if len(traj.states) >= 2:
        total_energy = 0.0
        for i in range(1, len(traj.states)):
            energy = manifold.step_displacement(traj.states[i - 1], traj.states[i])
            total_energy += energy
            print(f"  Step {i} geodesic energy: {energy:.4f}")
        print(f"Total path energy: {total_energy:.4f}")

    # Realization
    m_out = traj.states[-1].to_vector()
    realized = realizer.realize(m_out, top_k=3)
    print(f"\nRealization ({lang}):")
    for word, score in realized:
        print(f"  {word:<20} {score:.4f}")
    realized_body = realized[0][0]
    print(f"\nOutput: {realized_body}")
    return realized_body


def main():
    parser = argparse.ArgumentParser(description="SFL Meaning Matrix CLI")
    subparsers = parser.add_subparsers(dest="command", required=True)

    # Inference
    inf = subparsers.add_parser("infer", help="Run inference on a prompt")
    inf.add_argument("prompt", type=str, help="Input prompt")
    inf.add_argument("--lang", type=str, default="en", choices=["en", "es"], help="Language")
    inf.add_argument("--use-pi", action="store_true", help="Use trained pi model for next-step prediction")

    # Training
    tr = subparsers.add_parser("train-pi", help="Train pi model on trajectory data")
    tr.add_argument("--data-dir", type=Path, default=Path("data"), help="Directory with JSONL trajectories")
    tr.add_argument("--epochs", type=int, default=25)
    tr.add_argument("--batch-size", type=int, default=32)
    tr.add_argument("--lr", type=float, default=1e-3)
    tr.add_argument("--device", type=str, default="cpu")
    tr.add_argument("--model-path", type=Path, default=Path("sfl_pi_model.pt"))

    # Interactive
    subparsers.add_parser("interactive", help="Interactive REPL")

    args = parser.parse_args()

    if args.command == "infer":
        run_inference(args.prompt, args.lang, args.use_pi)
    elif args.command == "train-pi":
        train_pi_model(args.data_dir, args.epochs, args.batch_size, args.lr, args.device, args.model_path)
    elif args.command == "interactive":
        print("SFL Interactive Mode (Ctrl+C to exit)")
        while True:
            try:
                prompt = input("\n> ").strip()
                if not prompt:
                    continue
                run_inference(prompt, "en")
            except KeyboardInterrupt:
                print("\nBye!")
                break
            except Exception as e:
                print(f"Error: {e}")


if __name__ == "__main__":
    main()
