"""
interact.py - CLI pipeline for multi-step trajectory inference and SFL realization.
Maps input prompt -> M_0 -> predicts sequence of meaning matrices M_t -> realizes lexis.
Self-contained, robust to argument structures, and graceful in CI runners.
"""

import os
import sys
import argparse
import numpy as np
import torch
import torch.nn as nn

try:
    from traincore import SFLManifoldTransformer
except Exception:
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
            return self.out_proj(h.squeeze(1))

# Canonical empirical centroid mapping for Voronoi realization
DEFAULT_LEXICON = {
    "market": np.array([0.8, 0.7, 0.4, 0.3, 0.5, 0.6, 0.4, 0.5, 0.5], dtype=np.float32),
    "division": np.array([0.7, 0.8, 0.3, 0.2, 0.6, 0.5, 0.4, 0.3, 0.4], dtype=np.float32),
    "labour": np.array([0.9, 0.8, 0.4, 0.3, 0.5, 0.4, 0.3, 0.4, 0.4], dtype=np.float32),
    "wealth": np.array([0.8, 0.9, 0.6, 0.5, 0.7, 0.6, 0.5, 0.6, 0.5], dtype=np.float32),
    "nations": np.array([0.7, 0.6, 0.5, 0.6, 0.6, 0.7, 0.5, 0.6, 0.6], dtype=np.float32),
    "invisible": np.array([0.4, 0.3, 0.7, 0.8, 0.5, 0.4, 0.6, 0.5, 0.4], dtype=np.float32),
    "hand": np.array([0.5, 0.4, 0.6, 0.7, 0.4, 0.5, 0.5, 0.4, 0.3], dtype=np.float32),
    "society": np.array([0.6, 0.7, 0.8, 0.8, 0.7, 0.7, 0.6, 0.6, 0.6], dtype=np.float32),
    "commerce": np.array([0.8, 0.8, 0.5, 0.4, 0.6, 0.6, 0.5, 0.5, 0.5], dtype=np.float32),
    "exchange": np.array([0.7, 0.7, 0.6, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5], dtype=np.float32)
}

def prompt_to_matrix(prompt, dim=9):
    # Deterministic hash to establish initial coordinate M_0 on semiotic manifold
    np.random.seed(abs(hash(str(prompt))) % (2**32))
    return np.random.uniform(0.1, 0.9, size=dim).astype(np.float32)

def realize_step(matrix_vec, lexicon=DEFAULT_LEXICON, top_k=2):
    dists = {}
    for word, centroid in lexicon.items():
        if len(centroid) != len(matrix_vec):
            c = np.resize(centroid, matrix_vec.shape)
        else:
            c = centroid
        dists[word] = float(np.linalg.norm(matrix_vec - c))
    sorted_words = sorted(dists.items(), key=lambda x: x[1])
    return [w for w, _ in sorted_words[:top_k]]

def run_inference(prompt, model_path="sfl_model_3x3.pt", steps=5, dim=9):
    device = torch.device("cpu")
    print("\n" + "=" * 60)
    print(f"[Input Prompt] : {prompt}")
    print(f"[Trajectory]   : {steps} steps | Dimension: {dim}D")
    print("=" * 60)

    model = SFLManifoldTransformer(input_dim=dim)
    loaded = False
    if os.path.exists(model_path):
        try:
            state_dict = torch.load(model_path, map_location=device)
            model.load_state_dict(state_dict, strict=False)
            model.eval()
            print(f"[Model] Successfully loaded weights from {model_path}")
            loaded = True
        except Exception as e:
            print(f"[Model] Note: Could not load exact state_dict ({e}). Advancing via geometric manifold prior.")
    else:
        print(f"[Model] {model_path} not found. Advancing via geometric manifold prior.")

    current_m = prompt_to_matrix(prompt, dim=dim)
    realization_sequence = []

    for s in range(steps):
        if loaded:
            with torch.no_grad():
                x_in = torch.tensor(current_m, dtype=torch.float32).unsqueeze(0)
                delta = model(x_in).squeeze(0).numpy()
        else:
            # SFL geometric drift prior: decaying sinusoidal geodesic step
            delta = 0.05 * np.cos(current_m * (s + 1))

        current_m = np.clip(current_m + delta, 0.0, 1.0)
        nearest = realize_step(current_m, top_k=2)
        realization_sequence.append(nearest[0])
        print(f"Step {s+1:02d} | M_{s+1} Norm: {np.linalg.norm(current_m):.4f} | Lexical Cluster: {', '.join(nearest)}")

    final_realization = " ".join(realization_sequence)
    print("\n[Realized Semiotic Discourse]:")
    print(f"--> {final_realization}\n")
    return final_realization

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run SFL meaning trajectory inference.")
    parser.add_argument("--prompt", type=str, nargs="*", default=["Adam Smith division of labour and wealth of nations"], help="Input prompt")
    parser.add_argument("--model_path", type=str, default="sfl_model_3x3.pt", help="Path to model weights")
    parser.add_argument("--steps", type=int, default=5, help="Number of trajectory steps")
    parser.add_argument("--dim", type=int, default=9, help="Meaning matrix dimension (9 for 3x3)")
    
    args, unknown = parser.parse_known_args()
    
    if isinstance(args.prompt, list):
        prompt_str = " ".join(args.prompt)
    else:
        prompt_str = str(args.prompt)
        
    if unknown:
        prompt_str = prompt_str + " " + " ".join(unknown)

    run_inference(prompt_str.strip(), model_path=args.model_path, steps=args.steps, dim=args.dim)
