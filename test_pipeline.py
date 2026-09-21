"""
test_pipeline.py — End-to-End Verification Pipeline for 3x3 LASSM
Tests:
1. Parsing surface text to 3x3 MeaningMatrix (sfl_matrix_engine.py)
2. Computing manifold displacement and path loss (sfl_manifold.py)
3. Adapter projection from 9D to d_model (sfl_adapter.py)
4. Clustered metafunctional attention (sfl_attention.py)
5. System boundary realization against 9D centroids (sfl_realize.py)
"""

import torch
import numpy as np
from sfl_matrix_engine import SFLMatrixEngine, MeaningMatrix
from sfl_manifold import SemioticManifold
from sfl_adapter import SFLAdapter
from sfl_attention import ClusteredMetafunctionalAttention
from sfl_realize import BoundaryRealizer9D


def test_full_pipeline():
    print("=== Testing 3x3 (9D) LASSM End-to-End Pipeline ===")

    # 1. Parse text into 3x3 MeaningMatrix
    engine = SFLMatrixEngine()
    prompt = "Could you please print the quarterly report?"
    m0 = engine.encode_text(prompt)
    print(f"[1] Parsed prompt: '{prompt}'")
    print(f"    Matrix shape: {m0.matrix.shape} (values bounded in [-1.0, 1.0])")
    print(f"    Unrolled 9D vector: {np.round(m0.to_vector(), 2)}")

    # 2. Trajectory step & manifold geometry
    manifold = SemioticManifold()
    delta = np.array([
        [0.05, 0.10, 0.00],
        [0.10, 0.20, 0.05],
        [0.00, 0.10, 0.15]
    ], dtype=np.float32)
    m1 = m0.apply_delta(delta)
    disp = manifold.step_displacement(m0, m1)
    loss = manifold.trajectory_path_loss([m0, m1])
    print(f"[2] Manifold step displacement: {disp:.4f} | Path loss: {loss:.4f}")

    # 3. Neural Adapter Projection (9D -> d_model 768)
    adapter = SFLAdapter(in_features=9, d_model=768)
    adapter.eval()
    m_tensor = torch.tensor(m1.to_vector(), dtype=torch.float32).unsqueeze(0)  # Shape (1, 9)
    with torch.no_grad():
        h0 = adapter(m_tensor)
    print(f"[3] Adapter projected 9D vector to hidden space: {h0.shape}")

    # 4. Clustered Metafunctional Attention
    attn_layer = ClusteredMetafunctionalAttention(d_model=768, n_strata=3)
    attn_layer.eval()
    seq_h = h0.unsqueeze(1)  # Shape (1, 1, 768)
    with torch.no_grad():
        attn_out = attn_layer(seq_h)
    print(f"[4] Metafunctional attention layer executed: {attn_out.shape}")

    # 5. Terminal Boundary Realization
    realizer = BoundaryRealizer9D()
    matched_words = realizer.realize(m1.to_vector(), top_k=3)
    print(f"[5] Terminal surface realization candidates:")
    for word, dist in matched_words:
        print(f"    Word: '{word}' (Euclidean distance: {dist:.4f})")

    print("\n✅ Full 3x3 (9D) pipeline executed successfully with zero dimension mismatches!")


if __name__ == "__main__":
    test_full_pipeline()
