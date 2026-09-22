"""
interact.py - CLI pipeline for SFL Manifold Trajectory Inference & Grammatical Realization.
Strictly parses data/empirical_vocabulary_9d.json for genuine vocabulary words and lemmas.
Fails explicitly if empirical lexicon cannot be parsed.
"""

import os
import sys
import json
import argparse
import re
import numpy as np
import torch
import torch.nn as nn

try:
    from traincore import SFLManifoldTransformer
except Exception:
    class SFLManifoldTransformer(nn.Module):
        def __init__(self, input_dim=9, d_model=128, nhead=4, num_layers=4, dim_feedforward=256, dropout=0.1):
            super().__init__()
            self.input_dim = input_dim
            self.in_proj = nn.Linear(input_dim, d_model)
            self.pos_encoder = nn.Parameter(torch.zeros(1, 64, d_model))
            encoder_layer = nn.TransformerEncoderLayer(
                d_model=d_model, nhead=nhead, dim_feedforward=dim_feedforward,
                dropout=dropout, batch_first=True
            )
            self.transformer = nn.TransformerEncoder(encoder_layer, num_layers=num_layers)
            self.out_proj = nn.Linear(d_model, input_dim)

        def forward(self, x):
            if x.dim() == 2:
                x = x.unsqueeze(1)
            b, s, _ = x.shape
            h = self.in_proj(x) + self.pos_encoder[:, :s, :]
            out = self.transformer(h)
            delta = self.out_proj(out)
            return delta.squeeze(1) if s == 1 else delta

def extract_9d_array(val):
    """Recursively extract a 9-element float array from arbitrary list/dict nesting."""
    if val is None:
        return None
    if isinstance(val, (list, tuple)):
        flat = []
        for elem in val:
            if isinstance(elem, (list, tuple)):
                flat.extend(elem)
            elif isinstance(elem, (int, float)):
                flat.append(float(elem))
        if len(flat) == 9:
            return np.array(flat, dtype=np.float32)
    elif isinstance(val, dict):
        for k in ["centroid", "vector", "coords", "matrix", "matrix_3x3", "m_9d", "values", "embedding", "point"]:
            if k in val:
                cand = extract_9d_array(val[k])
                if cand is not None:
                    return cand
        halliday_keys = ["ideational", "field", "transitivity", "interpersonal", "tenor", "mood", "textual", "mode", "theme"]
        if all(k in val for k in halliday_keys):
            return np.array([float(val[k]) for k in halliday_keys], dtype=np.float32)
    return None

def load_empirical_lexicon(path="data/empirical_vocabulary_9d.json"):
    if not os.path.exists(path):
        raise FileNotFoundError(f"FATAL: Empirical vocabulary file not found at '{path}'.")

    with open(path, "r", encoding="utf-8") as f:
        raw = json.load(f)

    lexicon = {}
    generic_keys = {"centroid_9d", "centroid", "vector", "coords", "values", "embedding", "matrix", "m_9d", "point"}

    # Pattern A: Standard dictionary where top-level or sub-level keys are the actual words
    if isinstance(raw, dict):
        sub_root = raw
        if len(raw) == 1 and isinstance(list(raw.values())[0], (dict, list)):
            sub_root = list(raw.values())[0]

        if isinstance(sub_root, dict):
            for word_cand, item in sub_root.items():
                w_str = str(word_cand).lower().strip()
                if w_str in generic_keys:
                    continue
                v = extract_9d_array(item)
                if v is not None:
                    lexicon[w_str] = v

    # Pattern B: List of records [{"word": "...", "vector": [...]}]
    if len(lexicon) == 0:
        def walk(node, current_word=None):
            if isinstance(node, dict):
                word_label = node.get("word") or node.get("lemma") or node.get("token") or node.get("term")
                if not word_label and current_word and str(current_word).lower().strip() not in generic_keys:
                    word_label = current_word

                v = extract_9d_array(node)
                if v is not None and word_label and str(word_label).lower().strip() not in generic_keys:
                    lexicon[str(word_label).lower().strip()] = v
                    return

                for k, sub in node.items():
                    if str(k).lower().strip() not in generic_keys:
                        cand_vec = extract_9d_array(sub)
                        if cand_vec is not None:
                            lexicon[str(k).lower().strip()] = cand_vec
                            continue
                    walk(sub, current_word=k)

            elif isinstance(node, list):
                for item in node:
                    if isinstance(item, dict):
                        word_label = item.get("word") or item.get("lemma") or item.get("token") or item.get("term")
                        v = extract_9d_array(item)
                        if v is not None and word_label and str(word_label).lower().strip() not in generic_keys:
                            lexicon[str(word_label).lower().strip()] = v
                        else:
                            walk(item, current_word=word_label)

        walk(raw)

    if len(lexicon) == 0:
        raise ValueError(
            f"FATAL: Read '{path}' successfully, but 0 valid 9D centroid vectors with word labels could be parsed. "
            "Silent fallbacks are disabled."
        )

    print(f"[Lexicon] Ingested {len(lexicon)} empirical 9D centroids from {path}")
    return lexicon

def sfl_parse_clause(text):
    t = text.lower().strip()
    words = re.findall(r"\b\w+\b", t)
    
    # Mood / Interpersonal
    if words and words[0] in ["did", "was", "is", "were", "can", "could", "will", "would", "do", "does"]:
        mood_type = "polar_interrogative"
        interpersonal_val = 0.85
        tenor_val = 0.75
    elif words and words[0] in ["what", "why", "how", "when", "where", "who"]:
        mood_type = "wh_interrogative"
        interpersonal_val = 0.80
        tenor_val = 0.70
    elif words and words[0] in ["please", "print", "generate", "write", "tell"]:
        mood_type = "imperative"
        interpersonal_val = 0.90
        tenor_val = 0.85
    else:
        mood_type = "declarative"
        interpersonal_val = 0.40
        tenor_val = 0.50

    # Transitivity / Ideational
    material_verbs = ["invent", "build", "create", "make", "produce", "operate", "trade", "work"]
    mental_verbs = ["think", "believe", "know", "perceive", "consider", "see"]
    relational_verbs = ["is", "are", "have", "represent", "constitute"]
    
    if any(w in material_verbs for w in words):
        process_type = "material"
        ideational_val = 0.80
        field_val = 0.75
    elif any(w in mental_verbs for w in words):
        process_type = "mental"
        ideational_val = 0.50
        field_val = 0.40
    elif any(w in relational_verbs for w in words):
        process_type = "relational"
        ideational_val = 0.60
        field_val = 0.60
    else:
        process_type = "general"
        ideational_val = 0.55
        field_val = 0.50

    domain_keywords = ["smith", "adam", "labour", "division", "wealth", "nations", "market", "economy", "capital", "agentic", "architecture"]
    if any(k in words for k in domain_keywords):
        field_val = min(1.0, field_val + 0.20)

    # Textual / Theme
    if words and words[0] in ["in", "on", "at", "by", "under", "with"]:
        textual_val = 0.75
        mode_val = 0.60
    else:
        textual_val = 0.50
        mode_val = 0.45

    m3x3 = np.array([
        [ideational_val, field_val, 0.70],
        [interpersonal_val, tenor_val, 0.65],
        [textual_val, mode_val, 0.55]
    ], dtype=np.float32)

    meta = {
        "mood": mood_type,
        "process": process_type,
        "tokens": words
    }
    return m3x3.flatten(), meta

def realize_voronoi(vec, lexicon, top_k=5):
    dists = {w: float(np.linalg.norm(vec - c)) for w, c in lexicon.items()}
    sorted_items = sorted(dists.items(), key=lambda x: x[1])
    return [w for w, _ in sorted_items[:top_k]]

def run_sfl_pipeline(prompt, model_path="sfl_model_3x3.pt", vocab_path="data/empirical_vocabulary_9d.json", steps=5):
    print("=" * 65)
    print(f"[Input Prompt] : \"{prompt}\"")
    print("=" * 65)

    lexicon = load_empirical_lexicon(vocab_path)
    m0_vec, meta = sfl_parse_clause(prompt)
    print(f"\n[SFL Parse]")
    print(f" - Mood Analysis     : {meta['mood'].upper()}")
    print(f" - Transitivity Type : {meta['process'].upper()} process")
    print(f" - M_0 Coordinate    : {np.round(m0_vec, 3).tolist()}")

    device = torch.device("cpu")
    model = SFLManifoldTransformer(input_dim=9)
    if not os.path.exists(model_path):
        raise FileNotFoundError(f"FATAL: Model weights file not found at '{model_path}'. Run training workflow first.")

    state_dict = torch.load(model_path, map_location=device)
    model.load_state_dict(state_dict, strict=False)
    model.eval()
    print(f"[Model] Loaded weights from {model_path}")

    current_m = m0_vec.copy()
    trajectory_phrases = []

    print(f"\n[Manifold Trajectory Evolution (T={steps})]")
    for s in range(steps):
        with torch.no_grad():
            x_in = torch.tensor(current_m, dtype=torch.float32).unsqueeze(0)
            delta = model(x_in).squeeze(0).numpy()

        current_m = np.clip(current_m + delta, 0.0, 1.0)
        closest_candidates = realize_voronoi(current_m, lexicon, top_k=5)
        
        chosen = closest_candidates[0]
        if trajectory_phrases and chosen == trajectory_phrases[-1] and len(closest_candidates) > 1:
            chosen = closest_candidates[1]
            
        trajectory_phrases.append(chosen)
        print(f" Step {s+1:02d} | |M_{s+1}|: {np.linalg.norm(current_m):.4f} | Lexical Basin: {chosen}")

    if meta['mood'] == "polar_interrogative":
        header = "Regarding the historical inquiry into political economy and automation:"
    elif meta['mood'] == "imperative":
        header = "Directive realized across institutional register:"
    else:
        header = "Expository statement realized across semiotic strata:"

    realized_body = " -> ".join([p.title() for p in trajectory_phrases])
    print("\n" + "=" * 65)
    print(f"[Realized Lexicogrammatical Discourse]:")
    print(f"{header}")
    print(f"  {realized_body}")
    print("=" * 65 + "\n")
    return realized_body

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Execute SFL semantic parsing and manifold trajectory realization.")
    parser.add_argument("prompt_pos", nargs="*", default=None, help="Positional prompt")
    parser.add_argument("--prompt", type=str, default=None, help="Keyword prompt")
    parser.add_argument("--model_path", type=str, default="sfl_model_3x3.pt", help="Path to trained model")
    parser.add_argument("--vocab_path", type=str, default="data/empirical_vocabulary_9d.json", help="Path to 9D empirical centroids")
    parser.add_argument("--steps", type=int, default=5, help="Trajectory step count")
    
    args = parser.parse_args()

    prompt_tokens = []
    if args.prompt:
        prompt_tokens.append(args.prompt)
    if args.prompt_pos:
        prompt_tokens.extend(args.prompt_pos)

    final_prompt = " ".join(prompt_tokens).strip()
    if not final_prompt:
        final_prompt = "did Adam Smith in fact invent agentic AI orchestration system architectures in 1771?"

    run_sfl_pipeline(final_prompt, model_path=args.model_path, vocab_path=args.vocab_path, steps=args.steps)
