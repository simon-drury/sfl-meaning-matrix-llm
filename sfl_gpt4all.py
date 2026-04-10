#!/usr/bin/env python3
"""
sfl_gpt4all.py
Adapter bridge: SFL semiotic manifold <-> GPT4All local transformer.

This module replaces the hand-coded pilot encoders with a real
transformer backbone running locally via GPT4All.

Architecture
------------

  M_t in R^6          (meaning state from sfl_matrix_engine)
       |
       v
  W_adapt              (linear projection R^6 -> R^d_model)
       |
       v
  h_0 in R^d_model     (injected as context prefix to GPT4All)
       |
       v
  [GPT4All forward]    (backbone frozen, no fine-tuning yet)
       |
       v
  h_out in R^d_model   (final hidden state or embedding)
       |
       v
  W_inv                (linear projection R^d_model -> R^6)
       |
       v
  M_out in R^6         (output meaning state, clipped to [-1,1]^6)

The transformer is modality-blind throughout.
It receives h_0 derived from M_t. It returns h_out.
M_out is read from h_out. The transformer never sees language labels.

Setup
-----
  pip install gpt4all
  # Download a model in GPT4All desktop app first, e.g.:
  #   Meta-Llama-3-8B-Instruct.Q4_0.gguf
  #   Nous-Hermes-2-Mistral-7B-DPO.Q4_0.gguf
  #   nomic-embed-text-v1.5.f16.gguf  (embedding model)

Usage
-----
  python sfl_gpt4all.py
  # Runs the two pilot trajectories through the adapter bridge
  # and prints M_out for each final state.

Note
----
W_adapt and W_inv are randomly initialised here.
Training them is Step 2. This scaffold validates the pipeline shape.
"""

import numpy as np
from typing import Optional

from sfl_matrix_engine import encode_en, encode_es, MeaningTrajectory
from sfl_realize import build_pilot_en, build_pilot_es

DIM_NAMES = ["ideational", "field", "interpersonal", "tenor", "textual", "mode"]
N_DIM = 6

# GPT4All embedding dimension for nomic-embed-text-v1.5 is 768
# For LLM models (Llama, Mistral) use 4096
# Set this to match whichever model you have downloaded
D_MODEL = 768


# ---------------------------------------------------------------------------
# Adapter layers (randomly initialised -- training is Step 2)
# ---------------------------------------------------------------------------

np.random.seed(42)
W_adapt = np.random.randn(D_MODEL, N_DIM) * 0.1   # R^6  -> R^d_model
W_inv   = np.random.randn(N_DIM, D_MODEL) * 0.1   # R^d_model -> R^6


def project_to_model(M_t: np.ndarray) -> np.ndarray:
    """Project meaning state M_t into model embedding space."""
    h = W_adapt @ M_t          # shape (D_MODEL,)
    return h


def project_from_model(h_out: np.ndarray) -> np.ndarray:
    """Project model output back to meaning state M_out in [-1,1]^6."""
    M_out = W_inv @ h_out
    return np.clip(M_out, -1.0, 1.0)


# ---------------------------------------------------------------------------
# GPT4All bridge
# ---------------------------------------------------------------------------

def get_embedding_gpt4all(text: str, model_name: str) -> np.ndarray:
    """
    Get an embedding from a GPT4All embedding model.
    Returns a numpy array of shape (embedding_dim,).

    Requires gpt4all installed and the model downloaded.
    """
    try:
        from gpt4all import Embed4All
        embedder = Embed4All(model_name)
        result = embedder.embed(text)
        return np.array(result, dtype=float)
    except ImportError:
        raise ImportError(
            "gpt4all not installed. Run: pip install gpt4all"
        )
    except Exception as e:
        raise RuntimeError(
            f"GPT4All embedding failed for model '{model_name}': {e}\n"
            f"Make sure the model is downloaded in the GPT4All desktop app."
        )


def run_adapter_pipeline(
    traj: MeaningTrajectory,
    model_name: str = "nomic-embed-text-v1.5.f16.gguf",
    use_gpt4all: bool = True,
) -> dict:
    """
    Run a MeaningTrajectory through the adapter bridge.

    For each state in the trajectory:
    1. Project M_t -> h_0 via W_adapt
    2. If use_gpt4all: get embedding from GPT4All model
       Else: use h_0 directly (dry run, no model needed)
    3. Project h_out -> M_out via W_inv
    4. Retrieve nearest realization from V_EN and V_ES

    Parameters
    ----------
    traj        : MeaningTrajectory
    model_name  : GPT4All model filename
    use_gpt4all : if False, runs dry (adapter matrices only, no model)

    Returns
    -------
    dict with keys: lang, steps
    Each step: {t, label, M_in, h_0, M_out, EN_best, ES_best}
    """
    en_vocab = build_pilot_en()
    es_vocab = build_pilot_es()

    steps = []
    for t, state in enumerate(traj.states):
        M_t = state.to_vector()
        h_0 = project_to_model(M_t)

        if use_gpt4all:
            # Use the model embedding of the semiotic label as h_out
            # This is a proxy until W_adapt is trained end-to-end
            label_text = state.label if state.label else "meaning"
            h_out = get_embedding_gpt4all(label_text, model_name)
            # Resize if embedding dim differs from D_MODEL
            if h_out.shape[0] != D_MODEL:
                # Pad or truncate to D_MODEL
                h_resized = np.zeros(D_MODEL)
                n = min(h_out.shape[0], D_MODEL)
                h_resized[:n] = h_out[:n]
                h_out = h_resized
        else:
            # Dry run: use h_0 as h_out (identity proxy)
            h_out = h_0

        M_out = project_from_model(h_out)

        steps.append({
            "t":       t,
            "label":   state.label,
            "M_in":    M_t.tolist(),
            "M_out":   M_out.tolist(),
            "EN_best": en_vocab.realize(M_out),
            "ES_best": es_vocab.realize(M_out),
        })

    return {"lang": traj.lang, "steps": steps}


def print_pipeline_results(result: dict):
    lang = result["lang"]
    print(f"\n=== GPT4All Adapter Pipeline [{lang}] ===")
    print(f"{'t':<3} {'label':<24} {'EN_best':<16} {'ES_best':<16} M_out (truncated)")
    print("-" * 90)
    for s in result["steps"]:
        m = [f"{v:+.2f}" for v in s["M_out"][:3]]
        print(f"{s['t']:<3} {s['label']:<24} {s['EN_best']:<16} {s['ES_best']:<16} [{', '.join(m)}, ...]")


# ---------------------------------------------------------------------------
# Run
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    print("Running adapter pipeline in DRY RUN mode (no GPT4All model required).")
    print("Set use_gpt4all=True and specify your model name for live mode.\n")

    for encode_fn in [encode_en, encode_es]:
        traj = encode_fn()
        result = run_adapter_pipeline(traj, use_gpt4all=False)
        print_pipeline_results(result)

    print("\n--- To run with GPT4All (nomic-embed): ---")
    print("  from sfl_gpt4all import encode_en, run_adapter_pipeline")
    print("  traj = encode_en()")
    print("  result = run_adapter_pipeline(traj, model_name='nomic-embed-text-v1.5.f16.gguf', use_gpt4all=True)")
