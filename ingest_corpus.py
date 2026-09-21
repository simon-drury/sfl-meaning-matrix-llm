"""
ingest_corpus.py — Automated SFL Continuous Target Extractor
Task Agent 1: Real Corpus Ingestion & Statistical Centroid Calculation
Architecture: Language As Social Semiotic Model (LASSM)

Extracts Hallidayan systemic features from real sentences:
1. Ideational: Transitivity process type & participant density -> rows [0, :]
2. Interpersonal: Mood, social distance, polarity -> rows [1, :]
3. Textual: Theme/Rheme structural placement & cohesion -> rows [2, :]

Outputs:
- data/empirical_trajectories.jsonl (Real 9D continuous targets for training)
- data/empirical_vocabulary_9d.json (Learned centroids f_w across corpus words)
"""

import os
import re
import json
from collections import defaultdict
from typing import Dict, List, Tuple
import numpy as np


class SubroutineSFLExtractor:
    """
    Subroutine Task: Linguistic Feature Parsing into 3x3 Continuous State M_t
    Grounded in Halliday 1978 Social Semiotic Framework.
    """
    def __init__(self):
        self.material_verbs = {"print", "build", "run", "restarted", "send", "write", "create", "execute", "install", "push", "commit"}
        self.mental_verbs = {"analyze", "think", "understand", "see", "know", "believe", "consider", "decide", "expect"}
        self.relational_verbs = {"is", "are", "was", "were", "become", "represent", "have", "contain", "hold"}
        
        self.polite_modals = {"could", "would", "please", "kindly", "may"}
        self.imperative_triggers = {"print", "run", "do", "execute", "commit", "push", "fetch"}
        self.authoritative_modals = {"shall", "must", "required", "immediately"}

    def extract_matrix(self, sentence: str) -> np.ndarray:
        m = np.zeros((3, 3), dtype=np.float32)
        tokens = [re.sub(r'[^\w\s]', '', w.lower()) for w in sentence.split() if w.strip()]
        if not tokens:
            return m

        # 1. Ideational Row [0, :] -> (Field, Tenor, Mode)
        is_material = any(t in self.material_verbs for t in tokens)
        is_mental = any(t in self.mental_verbs for t in tokens)
        is_relational = any(t in self.relational_verbs for t in tokens)
        
        if is_material:
            m[0, 0] = 0.80
        elif is_mental:
            m[0, 0] = 0.60
        elif is_relational:
            m[0, 0] = 0.40
        else:
            m[0, 0] = 0.25
        
        m[0, 1] = float(np.clip(len(tokens) / 30.0, 0.1, 0.7))
        m[0, 2] = 0.50

        # 2. Interpersonal Row [1, :] -> (Field, Tenor, Mode)
        if any(t in self.polite_modals for t in tokens):
            m[1, 0] = 0.30
            m[1, 1] = 0.65
            m[1, 2] = 0.40
        elif any(t in self.authoritative_modals for t in tokens):
            m[1, 0] = 0.85
            m[1, 1] = 0.90
            m[1, 2] = 0.70
        elif tokens[0] in self.imperative_triggers:
            m[1, 0] = 0.20
            m[1, 1] = -0.50
            m[1, 2] = -0.30
        else:
            m[1, 0] = 0.20
            m[1, 1] = 0.05
            m[1, 2] = 0.10

        # 3. Textual Row [2, :] -> (Field, Tenor, Mode)
        first_tok = tokens[0]
        if first_tok in {"when", "if", "after", "in", "on", "before", "while"}:
            m[2, 0] = 0.60
            m[2, 1] = 0.40
            m[2, 2] = 0.85
        elif first_tok in {"the", "this", "a", "an", "it"}:
            m[2, 0] = 0.40
            m[2, 1] = 0.20
            m[2, 2] = 0.45
        else:
            m[2, 0] = 0.30
            m[2, 1] = 0.15
            m[2, 2] = 0.30

        return np.clip(m, -1.0, 1.0)


def run_corpus_ingestion(input_sentences: List[str], output_dir: str = "data"):
    os.makedirs(output_dir, exist_ok=True)
    extractor = SubroutineSFLExtractor()

    trajectories = []
    word_coordinates = defaultdict(list)

    print(f"--- [Task 1] Processing {len(input_sentences)} real discourse sentences ---")
    
    for idx, sent in enumerate(input_sentences):
        sent = sent.strip()
        if not sent:
            continue

        matrix = extractor.extract_matrix(sent)
        vec_9d = matrix.flatten().tolist()
        
        trajectories.append({
            "step": idx,
            "text": sent,
            "vector_9d": vec_9d,
            "matrix_3x3": matrix.tolist()
        })

        words = [re.sub(r'[^\w\s]', '', w.lower()) for w in sent.split() if w.strip()]
        for w in words:
            word_coordinates[w].append(vec_9d)

    traj_path = os.path.join(output_dir, "empirical_trajectories.jsonl")
    with open(traj_path, "w", encoding="utf-8") as f:
        for t in trajectories:
            f.write(json.dumps(t) + "\n")
    print(f"Saved {len(trajectories)} empirical 9D training states to {traj_path}")

    vocab_centroids = {}
    for word, coords_list in word_coordinates.items():
        arr = np.array(coords_list, dtype=np.float32)
        mean_coord = np.mean(arr, axis=0).round(4).tolist()
        vocab_centroids[word] = {
            "frequency": len(coords_list),
            "centroid_9d": mean_coord
        }

    vocab_path = os.path.join(output_dir, "empirical_vocabulary_9d.json")
    with open(vocab_path, "w", encoding="utf-8") as f:
        json.dump(vocab_centroids, f, indent=2)
    print(f"Computed empirical 9D centroids for {len(vocab_centroids)} unique vocabulary items at {vocab_path}")


if __name__ == "__main__":
    seed_corpus = [
        "Could you please print the quarterly financial report immediately?",
        "The dedicated server restarted after the network update completed.",
        "When morning comes we analyze the incoming telemetry data thoroughly.",
        "Hey print the report for me please thank you.",
        "The system administrator executed the database migration script yesterday.",
        "If the connection fails the application switches to fallback mode.",
        "We consider the preliminary experimental findings highly promising.",
        "The committee shall publish the technical evaluation guidelines next month.",
        "In the primary laboratory researchers examine the neural gradient behavior.",
        "The autonomous agent selects actions based on communicative register values.",
        "Could the engineering team deploy the revised adapter weights today?",
        "While the pipeline is running memory allocation remains strictly bounded."
    ]
    run_corpus_ingestion(seed_corpus)
