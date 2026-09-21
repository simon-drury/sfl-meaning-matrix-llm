"""
download_and_ingest_treebank.py — Automated Universal Treebank to SFL 3x3 Ingestion
Architecture: Language As Social Semiotic Model (LASSM)
Source: Universal Dependencies English Treebank (EWT - CoNLL-U format)

Automates:
1. Downloading real annotated linguistic corpus (Universal Dependencies English Web Treebank).
2. Parsing syntactic relations (nsubj, obj, obl, csubj, advmod, mark).
3. Mapping dependency structures into Hallidayan SFL 3x3 continuous states:
   - Ideational: Transitivity process classification (Material, Mental, Relational) and participant roles.
   - Interpersonal: Mood (Declarative, Interrogative, Imperative) and modality polarity.
   - Textual: Marked vs. unmarked Theme identification.
4. Outputting empirical trajectories (data/empirical_trajectories.jsonl) and vocabulary centroids (data/empirical_vocabulary_9d.json).
"""

import os
import json
import urllib.request
import re
from collections import defaultdict
from typing import List, Dict, Any, Tuple
import numpy as np


UD_EWT_URL = "https://raw.githubusercontent.com/UniversalDependencies/UD_English-EWT/master/en_ewt-ud-train.conllu"
DATA_DIR = "data"
RAW_CONLLU_PATH = os.path.join(DATA_DIR, "en_ewt-ud-train.conllu")


def download_corpus():
    os.makedirs(DATA_DIR, exist_ok=True)
    if not os.path.exists(RAW_CONLLU_PATH):
        print(f"Downloading real Universal Dependencies English Web Treebank from {UD_EWT_URL}...")
        urllib.request.urlretrieve(UD_EWT_URL, RAW_CONLLU_PATH)
        print(f"Downloaded successfully: {RAW_CONLLU_PATH} ({os.path.getsize(RAW_CONLLU_PATH)} bytes)")
    else:
        print(f"Using cached corpus at {RAW_CONLLU_PATH}")


def parse_conllu_sentences(filepath: str, max_sentences: int = 1000) -> List[List[Dict[str, str]]]:
    sentences = []
    current_tokens = []

    with open(filepath, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                if current_tokens:
                    sentences.append(current_tokens)
                    current_tokens = []
                    if len(sentences) >= max_sentences:
                        break
                continue
            if line.startswith("#"):
                continue

            parts = line.split("\t")
            if len(parts) >= 8 and parts[0].isdigit():
                current_tokens.append({
                    "id": int(parts[0]),
                    "form": parts[1],
                    "lemma": parts[2].lower(),
                    "upos": parts[3],
                    "deprel": parts[7]
                })

    if current_tokens and len(sentences) < max_sentences:
        sentences.append(current_tokens)

    return sentences


class UniversalDependencySFLMapper:
    def __init__(self):
        self.mental_lemmas = {"think", "know", "believe", "understand", "see", "hear", "feel", "remember", "consider", "want", "like"}
        self.relational_lemmas = {"be", "become", "seem", "appear", "have", "remain", "represent", "include"}

    def map_sentence_to_matrix(self, tokens: List[Dict[str, str]]) -> Tuple[np.ndarray, str]:
        m = np.zeros((3, 3), dtype=np.float32)
        words = [t["form"] for t in tokens]
        sentence_text = " ".join(words)
        lemmas = [t["lemma"] for t in tokens]
        deprels = [t["deprel"] for t in tokens]
        pos_tags = [t["upos"] for t in tokens]

        # 1. Ideational Row [0, :]
        verbs = [t for t in tokens if t["upos"] == "VERB" or t["upos"] == "AUX"]
        is_mental = any(t["lemma"] in self.mental_lemmas for t in verbs)
        is_relational = any(t["lemma"] in self.relational_lemmas for t in verbs)
        
        if is_mental:
            m[0, 0] = 0.60
        elif is_relational:
            m[0, 0] = 0.40
        elif verbs:
            m[0, 0] = 0.80
        else:
            m[0, 0] = 0.20

        participants = sum(1 for d in deprels if d in {"nsubj", "obj", "iobj", "obl", "csubj"})
        m[0, 1] = float(np.clip(participants / 6.0, 0.1, 0.9))
        m[0, 2] = 0.50

        # 2. Interpersonal Row [1, :]
        has_question_mark = "?" in words
        has_modal = any(t["upos"] == "AUX" and t["lemma"] in {"could", "would", "may", "might", "can", "should", "must", "shall"} for t in tokens)
        
        if has_question_mark or (tokens and tokens[0]["upos"] == "AUX"):
            m[1, 0] = 0.35
            m[1, 1] = 0.60 if has_modal else 0.40
            m[1, 2] = 0.40
        elif tokens and tokens[0]["upos"] == "VERB" and "nsubj" not in deprels[:2]:
            m[1, 0] = 0.30
            m[1, 1] = -0.60
            m[1, 2] = -0.30
        else:
            m[1, 0] = 0.20
            m[1, 1] = 0.10
            m[1, 2] = 0.15

        # 3. Textual Row [2, :]
        first_tok = tokens[0]
        if first_tok["deprel"] in {"advmod", "mark", "prep", "obl"}:
            m[2, 0] = 0.65
            m[2, 1] = 0.40
            m[2, 2] = 0.85
        elif first_tok["deprel"] == "nsubj":
            m[2, 0] = 0.40
            m[2, 1] = 0.20
            m[2, 2] = 0.40
        else:
            m[2, 0] = 0.30
            m[2, 1] = 0.15
            m[2, 2] = 0.30

        return np.clip(m, -1.0, 1.0), sentence_text


def build_real_dataset(num_sentences: int = 500):
    download_corpus()
    print(f"Parsing real annotated sentences from {RAW_CONLLU_PATH}...")
    sentences = parse_conllu_sentences(RAW_CONLLU_PATH, max_sentences=num_sentences)
    print(f"Extracted {len(sentences)} parsed sentences.")

    mapper = UniversalDependencySFLMapper()
    trajectories = []
    word_coordinates = defaultdict(list)

    for idx, sent in enumerate(sentences):
        matrix, text = mapper.map_sentence_to_matrix(sent)
        vec_9d = matrix.flatten().tolist()
        
        trajectories.append({
            "step": idx,
            "text": text,
            "vector_9d": vec_9d,
            "matrix_3x3": matrix.tolist()
        })

        for t in sent:
            clean_word = re.sub(r'[^\w\s]', '', t["lemma"])
            if clean_word and len(clean_word) > 1:
                word_coordinates[clean_word].append(vec_9d)

    out_traj = os.path.join(DATA_DIR, "empirical_trajectories.jsonl")
    with open(out_traj, "w", encoding="utf-8") as f:
        for t in trajectories:
            f.write(json.dumps(t) + "\n")
    print(f"Successfully generated {len(trajectories)} empirical 9D training states at {out_traj}")

    out_vocab = os.path.join(DATA_DIR, "empirical_vocabulary_9d.json")
    vocab_centroids = {}
    for word, coords_list in word_coordinates.items():
        arr = np.array(coords_list, dtype=np.float32)
        mean_coord = np.mean(arr, axis=0).round(4).tolist()
        vocab_centroids[word] = {
            "frequency": len(coords_list),
            "centroid_9d": mean_coord
        }

    with open(out_vocab, "w", encoding="utf-8") as f:
        json.dump(vocab_centroids, f, indent=2)
    print(f"Successfully generated empirical 9D centroids for {len(vocab_centroids)} real vocabulary items at {out_vocab}")


if __name__ == "__main__":
    build_real_dataset(num_sentences=500)
