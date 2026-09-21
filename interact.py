"""
Language As Social Semiotic Model (LASSM) — Full Trajectory Realization Engine
Takes a natural language prompt, maps it to an SFL Meaning Trajectory (M0 -> M_t),
computes continuous manifold trajectory states via SFLAttention / SFLManifold,
and performs sequential boundary realization across empirical 9D vocabulary centroids.

|<[sjd_datascapes]>| · https://github.com/simon-drury/sfl-meaning-matrix-llm
"""

import os
import sys
import json
import torch
import numpy as np

from traincore import SFLMeaningTransformer

def extract_vector(val):
    if isinstance(val, (list, tuple)):
        return list(val)
    elif isinstance(val, dict):
        for k in ['centroid', 'vector', 'coords', 'values']:
            if k in val and isinstance(val[k], (list, tuple)):
                return list(val[k])
        for v in val.values():
            if isinstance(v, (list, tuple)):
                return list(v)
    return None

def parse_input_to_9d(text: str, vocab_9d: dict) -> np.ndarray:
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
        # Balanced baseline: [Id_Field, Id_Tenor, Id_Mode, Int_Field, Int_Tenor, Int_Mode, Txt_Field, Txt_Tenor, Txt_Mode]
        m0 = np.array([0.5, 0.2, 0.0, 0.6, 0.7, -0.3, 0.4, 0.2, 0.1], dtype=np.float32)
        
    return np.clip(m0, -1.0, 1.0)

def find_nearest_word(target_coord: np.ndarray, vocab_9d: dict, exclude: set = None) -> tuple:
    if exclude is None:
        exclude = set()
    best_word = None
    min_dist = float('inf')
    
    for word, raw_centroid in vocab_9d.items():
        if word in exclude:
            continue
        vec = extract_vector(raw_centroid)
        if vec is not None:
            dist = np.linalg.norm(target_coord - np.array(vec, dtype=np.float32))
            if dist < min_dist:
                min_dist = dist
                best_word = word
                
    return best_word, min_dist

def generate_trajectory_realization(prompt: str, steps: int = 5):
    print("\n" + "="*70)
    print("Language As Social Semiotic Model (LASSM) — Trajectory Realizer")
    print("|<[sjd_datascapes]>| · https://github.com/simon-drury/sfl-meaning-matrix-llm")
    print("="*70)

    # 1. Load Lexicon Centroids
    vocab_path = "data/empirical_vocabulary_9d.json"
    if not os.path.exists(vocab_path):
        print(f"Error: Vocabulary file '{vocab_path}' not found.")
        sys.exit(1)
        
    print(f"\n[1/3] Loading empirical vocabulary ({vocab_path})...")
    with open(vocab_path, "r", encoding="utf-8") as f:
        vocab_9d = json.load(f)
    print(f"      Loaded {len(vocab_9d)} empirical 9D lexical centroids.")

    # 2. Compile Input Prompt to M0
    print(f"\n[2/3] Compiling input prompt to initial state M0...")
    print(f"      Input Prompt: \"{prompt}\"")
    m_current = parse_input_to_9d(prompt, vocab_9d)
    
    print("\n      Initial 3x3 State Matrix M0:")
    print(f"      Ideational   [Field: {m_current[0]:+.3f}, Tenor: {m_current[1]:+.3f}, Mode: {m_current[2]:+.3f}]")
    print(f"      Interpersonal[Field: {m_current[3]:+.3f}, Tenor: {m_current[4]:+.3f}, Mode: {m_current[5]:+.3f}]")
    print(f"      Textual      [Field: {m_current[6]:+.3f}, Tenor: {m_current[7]:+.3f}, Mode: {m_current[8]:+.3f}]")

    # 3. Load Model
    checkpoint_path = "sfl_model_3x3.pt"
    if not os.path.exists(checkpoint_path):
        print(f"Error: Trained checkpoint '{checkpoint_path}' not found.")
        sys.exit(1)
        
    model = SFLMeaningTransformer()
    model.load_state_dict(torch.load(checkpoint_path, weights_only=True))
    model.eval()

    # 4. Sequential Trajectory Realization
    print(f"\n[3/3] Navigating {steps}-step continuous manifold trajectory...")
    print("-" * 70)
    print(f"{'Step':<6} | {'Displacement ||Delta||':<22} | {'Realized Lexis':<18} | {'Distance'}")
    print("-" * 70)

    realized_tokens = []
    used_words = set()

    for step in range(1, steps + 1):
        with torch.no_grad():
            inp_tensor = torch.tensor(m_current, dtype=torch.float32).unsqueeze(0)
            m_next = model(inp_tensor).squeeze(0).numpy()
            m_next = np.clip(m_next, -1.0, 1.0)

        delta = np.linalg.norm(m_next - m_current)
        word, dist = find_nearest_word(m_next, vocab_9d, exclude=used_words)
        
        if word:
            realized_tokens.append(word)
            used_words.add(word)
            print(f"M_{step:<3} | {delta:<22.4f} | {word:<18} | {dist:.4f}")
        
        # Advance state with small semiotic decay to prevent static cycling
        m_current = np.clip(m_next + np.random.normal(0, 0.02, size=9), -1.0, 1.0)

    print("-" * 70)
    print(f"\nFinal Lexical Realization Output:")
    print(f"  --> {' '.join(realized_tokens)}")
    print("=" * 70 + "\n")

if __name__ == "__main__":
    if len(sys.argv) > 1:
        user_prompt = " ".join(sys.argv[1:])
    else:
        user_prompt = "did Adam Smith invent agentic AI in 1771?"
        
    generate_trajectory_realization(user_prompt, steps=6)
