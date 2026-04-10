#!/usr/bin/env python3
"""
sfl_adapter.py
Linear projection layer: meaning vector -> transformer embedding space.

Maps an n_dim-dimensional meaning vector (default n_dim=6) into the
embedding dimension of a target transformer model.

    e_t = W_adapt @ m_t + b

    W_adapt : shape (d_model, n_dim)
    b       : shape (d_model,)

n_dim is a parameter, not a constant. The current value of 6 reflects
the minimum viable SFL metafunctional decomposition. It will grow as
the theory demands: additional register variables, appraisal dimensions,
genre, modality, or richer internal structure within each dimension.

Supported target models (local, GPT4All / llama.cpp):
    deepseek-r1-distill-qwen-1.5b   d_model = 2048   n_params = 2048*n_dim + 2048
    llama-3.2-3b-instruct            d_model = 3072   n_params = 3072*n_dim + 3072
"""

import numpy as np
from dataclasses import dataclass
from typing import Optional

MODEL_DIMS = {
    "deepseek-r1-distill-qwen-1.5b": 2048,
    "llama-3.2-3b-instruct": 3072,
}

DEFAULT_N_DIM = 6


@dataclass
class AdapterConfig:
    model_name: str
    d_model: int
    n_dim: int = DEFAULT_N_DIM

    @classmethod
    def for_model(cls, model_name: str, n_dim: int = DEFAULT_N_DIM):
        key = model_name.lower().strip()
        if key not in MODEL_DIMS:
            raise ValueError(
                f"Unknown model '{model_name}'. "
                f"Add its d_model to MODEL_DIMS or use AdapterConfig.custom()."
            )
        return cls(model_name=key, d_model=MODEL_DIMS[key], n_dim=n_dim)

    @classmethod
    def custom(cls, model_name: str, d_model: int, n_dim: int = DEFAULT_N_DIM):
        return cls(model_name=model_name, d_model=d_model, n_dim=n_dim)

    @property
    def n_params(self):
        return self.d_model * self.n_dim + self.d_model

    def __str__(self):
        return (
            f"AdapterConfig({self.model_name} | "
            f"d_model={self.d_model} | n_dim={self.n_dim} | "
            f"trainable params={self.n_params:,})"
        )


class SFLAdapter:
    """
    Learned linear projection from meaning space R^n_dim
    to transformer embedding space R^d_model.

    Initialised with Xavier uniform weights, zero bias.
    In production: weights learned via backprop on L_sp.
    """

    def __init__(self, config: AdapterConfig, seed: int = 42):
        self.config = config
        rng = np.random.default_rng(seed)
        limit = np.sqrt(6.0 / (config.n_dim + config.d_model))
        self.W = rng.uniform(-limit, limit, (config.d_model, config.n_dim))
        self.b = np.zeros(config.d_model)

    def project(self, m: np.ndarray) -> np.ndarray:
        """
        Project a single meaning vector m (shape: n_dim,)
        into transformer embedding space (shape: d_model,).
        """
        assert m.shape == (self.config.n_dim,), (
            f"Expected meaning vector of shape ({self.config.n_dim},), "
            f"got {m.shape}. "
            f"If n_dim has grown, update AdapterConfig.n_dim."
        )
        return self.W @ m + self.b

    def project_trajectory(self, trajectory_vectors: np.ndarray) -> np.ndarray:
        """
        Project a full trajectory of meaning vectors.

        Parameters
        ----------
        trajectory_vectors : np.ndarray, shape (T, n_dim)

        Returns
        -------
        np.ndarray, shape (T, d_model)
            Ready to pass as input sequence to the transformer.
        """
        return np.stack([self.project(v) for v in trajectory_vectors])

    def __repr__(self):
        return f"SFLAdapter({self.config})"


def validate_adapter(adapter: SFLAdapter, verbose: bool = True) -> bool:
    cfg = adapter.config
    T = 5
    fake_trajectory = np.random.randn(T, cfg.n_dim).astype(np.float32)
    output = adapter.project_trajectory(fake_trajectory)
    shape_ok = output.shape == (T, cfg.d_model)
    finite_ok = bool(np.all(np.isfinite(output)))
    if verbose:
        print(f"\nAdapter validation: {adapter}")
        print(f"  Input  shape : ({T}, {cfg.n_dim})")
        print(f"  Output shape : {output.shape}  {'OK' if shape_ok else 'FAIL'}")
        print(f"  All finite   : {finite_ok}")
        print(f"  Output norm  : {np.linalg.norm(output):.4f}")
        print(f"  Status       : {'PASS' if shape_ok and finite_ok else 'FAIL'}")
    return shape_ok and finite_ok


if __name__ == "__main__":
    for model in MODEL_DIMS:
        cfg = AdapterConfig.for_model(model)
        print(f"\n{cfg}")
        adapter = SFLAdapter(cfg)
        validate_adapter(adapter)

    print("\n--- Scalability demo: n_dim = 12 (future extension) ---")
    cfg_future = AdapterConfig.custom(
        "deepseek-r1-distill-qwen-1.5b", d_model=2048, n_dim=12
    )
    print(cfg_future)
    validate_adapter(SFLAdapter(cfg_future))
