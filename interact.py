"""
SFL Meaning Matrix LLM - Interactive Pipeline CLI
Accepts text input, parses to 9D meaning state, computes manifold trajectory,
and realizes output text via empirical nearest-neighbor vocabulary centroids.

|<[sjd_datascapes]>| · https://github.com/simon-drury/sfl-meaning-matrix-llm
"""

import os
import sys
import json
import torch
import numpy as np

from traincore import SFLMeaningTransformer

def extract_vector(val):
    """
    Extracts a raw 9D list/array whether the vocabulary entry is:
    - a list of 9 floats: [v1, ..., v9]
    - a dict: {'centroid': [...]} or {'vector': [...]} or {'coords': [...]}
    """
    if isinstance(val, (list, tuple)):
        return list(val)
    elif isinstance(val, dict):
        for k in ['centroid', 'vector', 'coords', 'values']:
            if k in val and isinstance(val[k], (list, tuple)):
                return list(val[k])
        # If it's a dict of coordinate pairs, take values
        for v in val.values():
            if isinstance(v, (list, tuple)):
                return list(v)
    return None

def parse_input_to_9d(text: str, vocab_9d: dict) -> np.ndarray:
    """
    Projects raw user input text into a continuous 9D SFL meaning vector
    by aggregating the empirical 9D centroids of recognized words.
    Falls back to a default neutral state if words are out-of-vocabulary.
    """
    words = [w.strip(".,!?;:\"'()").lower() for w in text.split()]
    coords = []
    for w in words:
        if w in vocab_9d:
            vec = extract_vector(vocab_9d[w])
            if vec is not None:
                coords.append(vec)
    
    if coords:
        coords_arr = np.array(coords, dtype=np.float32)
        m0 = np.mean(coords_arr, axis=0)
    else:
        # Default conversational baseline: moderate interpersonal, balanced ideational/textual
        m0 = np.array([0.5, 0.2, 0.0, 0.6, 0.7, -0.3, 0.4, 0.2, 0.1], dtype=np.float32)
        
    return np.clip(m0, -1.0, 1.0)

def realize_text(m_out: np.ndarray, vocab_9d: dict, top_k: int = 5) -> list:
    """
    Selects surface words via Euclidean distance minimization against
    learned empirical 9D centroids in meaning space.
    """
    candidates = []
    for word, raw_centroid in vocab_9d.items():
        vec = extract_vector(raw_centroid)
        if vec is not None:
            dist = np.linalg.norm(m_out - np.array(vec, dtype=np.float32))
            candidates.append((dist, word))
        
    candidates.sort(key=lambda x: x[0])
    return candidates[:top_k]

def run_pipeline(prompt: str):
    print("\n" + "="*60)
    print("Language As Social Semiotic Model (LASSM) — Inference Engine")
    print("|<[sjd_datascapes]>| · https://github.com/simon-drury/sfl-meaning-matrix-llm")
    print("="*60)
    
    # 1. Load Vocabulary
    vocab_path = "data/empirical_vocabulary_9d.json"
    if not os.path.exists(vocab_path):
        print(f"Error: Vocabulary file '{vocab_path}' not found.")
        sys.exit(1)
        
    print(f"\n[1/3] Loading empirical vocabulary ({vocab_path})...")
    with open(vocab_path, "r", encoding="utf-8") as f:
        vocab_9d = json.load(f)
    print(f"      Loaded {len(vocab_9d)} empirical 9D lexical centroids.")

    # 2. Compile Input Text to Meaning State M0
    print(f"\n[2/3] Compiling input prompt to SFL meaning state M0...")
    print(f"      Input Prompt: \"{prompt}\"")
    m0 = parse_input_to_9d(prompt, vocab_9d)
    
    print("\n      Compiled 3x3 State Matrix M0:")
    matrix_str = [
        f"      Ideational   [Field: {m0[0]:+.3f}, Tenor: {m0[1]:+.3f}, Mode: {m0[2]:+.3f}]",
        f"      Interpersonal[Field: {m0[3]:+.3f}, Tenor: {m0[4]:+.3f}, Mode: {m0[5]:+.3f}]",
        f"      Textual      [Field: {m0[6]:+.3f}, Tenor: {m0[7]:+.3f}, Mode: {m0[8]:+.3f}]",
    ]
    print("\n".join(matrix_str))

    # 3. Model Trajectory Computation
    print("\n[3/3] Navigating semiotic manifold trajectory (SFLMeaningTransformer)...")
    checkpoint_path = "sfl_model_3x3.pt"
    if not os.path.exists(checkpoint_path):
        print(f"Error: Trained checkpoint '{checkpoint_path}' not found.")
        sys.exit(1)
        
    model = SFLMeaningTransformer()
    model.load_state_dict(torch.load(checkpoint_path, weights_only=True))
    model.eval()
    
    with torch.no_grad():
        m0_tensor = torch.tensor(m0, dtype=torch.float32).unsqueeze(0)
        m_out_tensor = model(m0_tensor)
        m_out = m_out_tensor.squeeze(0).numpy()
        m_out = np.clip(m_out, -1.0, 1.0)
        
    displacement = np.linalg.norm(m_out - m0)
    print(f"      Trajectory step displacement ||Delta||: {displacement:.4f}")
    print("\n      Predicted 3x3 Output State Matrix M_out:")
    matrix_out_str = [
        f"      Ideational   [Field: {m_out[0]:+.3f}, Tenor: {m_out[1]:+.3f}, Mode: {m_out[2]:+.3f}]",
        f"      Interpersonal[Field: {m_out[3]:+.3f}, Tenor: {m_out[4]:+.3f}, Mode: {m_out[5]:+.3f}]",
        f"      Textual      [Field: {m_out[6]:+.3f}, Tenor: {m_out[7]:+.3f}, Mode: {m_out[8]:+.3f}]",
    ]
    print("\n".join(matrix_out_str))

    # 4. Surface Realization
    print("\n" + "-"*60)
    print("Surface Realization (Euclidean Distance Minimization)")
    print("-"*60)
    nearest = realize_text(m_out, vocab_9d, top_k=8)
    for rank, (dist, word) in enumerate(nearest, 1):
        print(f"  {rank}. {word:<16} (Euclidean distance: {dist:.4f})")
        
    realized_words = [w for _, w in nearest[:5]]
    print("\n" + "="*60)
    print(f"Realized Lexical Output: {' '.join(realized_words)}")
    print("="*60 + "\n")

if __name__ == "__main__":
    if len(sys.argv) > 1:
        user_prompt = " ".join(sys.argv[1:])
    else:
        user_prompt = "Could you please explain what happened? Thank you."
        
    run_pipeline(user_prompt)
