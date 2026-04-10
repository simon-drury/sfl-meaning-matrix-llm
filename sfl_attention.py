#!/usr/bin/env python3
"""
sfl_attention.py
SFL Metafunctional Attention Cluster Engine.

Input:  MeaningTrajectory  (sequence of 3x2 meaning matrices)
Output: per-cluster attention weights + activated semiotic region

No token sequences. No positional embeddings.
Attention operates over positions in semiotic space,
not over positions in a lexical string.

Four metafunctional clusters:
  field_stability   -- watches field dimension: is the domain holding or shifting?
  tenor_trajectory  -- watches interpersonal + tenor: how is power/solidarity moving?
  mode_register     -- watches mode: planned or spontaneous channel?
  ideational_load   -- watches ideational: is experiential content increasing or plateauing?
"""

import numpy as np
from typing import Dict, List

# Dimension indices in the flattened 6-vector
# [ideational, field, interpersonal, tenor, textual, mode]
DIM = {"ideational": 0, "field": 1, "interpersonal": 2, "tenor": 3, "textual": 4, "mode": 5}
DIM_NAMES = ["ideational", "field", "interpersonal", "tenor", "textual", "mode"]

CLUSTERS = {
    "field_stability":   [1],      # field
    "tenor_trajectory":  [2, 3],   # interpersonal + tenor
    "mode_register":     [5],      # mode
    "ideational_load":   [0],      # ideational
}


def softmax(x: np.ndarray) -> np.ndarray:
    e = np.exp(x - np.max(x))
    return e / e.sum()


def cluster_attention(trajectory) -> Dict[str, np.ndarray]:
    """
    For each metafunctional cluster, compute attention weights
    across the trajectory steps.

    Relevance score at each step = L2 norm of cluster dimensions
    at that state. Weights are softmax-normalized.

    Returns: dict of cluster_name -> np.ndarray of shape (T,)
    """
    vectors = np.array([s.to_vector() for s in trajectory.states])  # (T, 6)
    attention = {}
    for name, dims in CLUSTERS.items():
        scores = np.linalg.norm(vectors[:, dims], axis=1)  # (T,)
        attention[name] = softmax(scores)
    return attention


def activated_region(trajectory, attention: Dict[str, np.ndarray]) -> np.ndarray:
    """
    Compute the attention-weighted centroid of the trajectory
    in semiotic space.

    Mean attention weights across all clusters are used to
    produce a single 6-dimensional vector: the activated
    semiotic region that the realization engine operates on.

    Returns: np.ndarray of shape (6,)
    """
    vectors = np.array([s.to_vector() for s in trajectory.states])  # (T, 6)
    all_weights = np.stack(list(attention.values()), axis=0)         # (C, T)
    mean_weights = all_weights.mean(axis=0)                          # (T,)
    region = (mean_weights[:, None] * vectors).sum(axis=0)           # (6,)
    return region


def print_attention(trajectory, attention: Dict[str, np.ndarray], region: np.ndarray):
    """Render attention weights and activated region to stdout."""
    labels = [s.label for s in trajectory.states]
    cluster_names = list(CLUSTERS.keys())

    print("\n=== SFL Attention [" + trajectory.lang + "] ===")
    header = "Step" + " " * 31
    for c in cluster_names:
        header += c[:10].rjust(11)
    print(header)
    print("-" * 75)
    for i, lbl in enumerate(labels):
        row = lbl[:34].ljust(35)
        for c in cluster_names:
            row += str(round(attention[c][i], 3)).rjust(11)
        print(row)

    print("\n  Activated semiotic region (attention-weighted centroid):")
    for name, val in zip(DIM_NAMES, region):
        bar = "+" * int(abs(val) * 20) if val >= 0 else "-" * int(abs(val) * 20)
        print("    " + name.ljust(15) + str(round(val, 3)).rjust(7) + "  " + bar)


# ---------------------------------------------------------------------------
# Run standalone with iconic test prompts
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    from sfl_matrix_engine import encode_en, encode_es

    for fn in [encode_en, encode_es]:
        traj = fn()
        attn = cluster_attention(traj)
        region = activated_region(traj, attn)
        print_attention(traj, attn, region)
        print("=" * 75)
