#!/usr/bin/env python3
"""
sfl_realize.py
De-matrixising: meaning state -> lexical realization in language L.

The transformer outputs a meaning state M_out in the semiotic manifold M.
This module retrieves the lexical items whose semiotic fingerprints
f_w in M are closest to M_out, within the vocabulary space V_L
of a specified language L.

    w* = argmin_{w in V_L} || f_w - M_out ||_2

The same M_out presented to V_EN and V_ES produces two independent,
co-equal realizations. There is no translation step.

Vocabulary fingerprints
-----------------------
Each lexical item w in V_L is assigned a 6-dimensional semiotic
fingerprint f_w in [-1, 1]^6. In production these are learned from
SFL-annotated corpora. The pilot vocabulary below is hand-encoded
for validation using the two iconic prompts.

Scalability
-----------
n_dim is a parameter. As the manifold grows beyond 6 dimensions,
fingerprints grow with it. VocabularySpace accepts any n_dim.
"""

import numpy as np
from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Optional

DIM = ["ideational", "field", "interpersonal", "tenor", "textual", "mode"]
DEFAULT_N_DIM = 6


@dataclass
class LexicalItem:
    form: str                    # surface form, e.g. "print"
    lang: str                    # ISO 639-1, e.g. "EN"
    fingerprint: np.ndarray      # shape (n_dim,), values in [-1, 1]


class VocabularySpace:
    """
    A language-specific vocabulary: a set of lexical items
    each with a semiotic fingerprint in the manifold.
    """

    def __init__(self, lang: str, n_dim: int = DEFAULT_N_DIM):
        self.lang = lang
        self.n_dim = n_dim
        self._items: List[LexicalItem] = []

    def add(self, form: str, fingerprint: List[float]):
        fp = np.array(fingerprint, dtype=float)
        assert fp.shape == (self.n_dim,), (
            f"Fingerprint for '{form}' has shape {fp.shape}, "
            f"expected ({self.n_dim},)."
        )
        self._items.append(LexicalItem(form=form, lang=self.lang, fingerprint=fp))

    def nearest(self, M_out: np.ndarray, k: int = 5) -> List[Tuple[str, float]]:
        """
        Return the k lexical items closest to M_out by Euclidean distance.

        w* = argmin_{w in V_L} || f_w - M_out ||_2

        Parameters
        ----------
        M_out : np.ndarray, shape (n_dim,)
        k     : number of candidates to return

        Returns
        -------
        List of (form, distance) sorted ascending by distance.
        """
        assert M_out.shape == (self.n_dim,), (
            f"M_out shape {M_out.shape} does not match n_dim={self.n_dim}."
        )
        dists = [
            (item.form, float(np.linalg.norm(item.fingerprint - M_out)))
            for item in self._items
        ]
        return sorted(dists, key=lambda x: x[1])[:k]

    def realize(self, M_out: np.ndarray) -> str:
        """Return the single best-matching lexical item for M_out."""
        return self.nearest(M_out, k=1)[0][0]

    def __len__(self):
        return len(self._items)

    def __repr__(self):
        return f"VocabularySpace(lang={self.lang}, n_dim={self.n_dim}, items={len(self)})"


# ---------------------------------------------------------------------------
# Pilot vocabularies -- hand-encoded semiotic fingerprints
# Format: [ideational, field, interpersonal, tenor, textual, mode]
#
# In production: fingerprints are learned from SFL-annotated corpora.
# The values below are derived from the iconic prompt analysis.
# ---------------------------------------------------------------------------

def build_pilot_en() -> VocabularySpace:
    v = VocabularySpace(lang="EN")
    # Interpersonal / phatic
    v.add("hey",           [-0.7, -0.5,  0.8,  0.9,  0.6, -0.6])
    v.add("hello",         [-0.6, -0.4,  0.7,  0.8,  0.5, -0.5])
    v.add("please",        [-0.2,  0.0,  0.9,  1.0,  0.4, -0.4])
    v.add("thank you",     [ 0.1,  0.2,  1.0,  1.0,  0.5, -0.5])
    v.add("sorry",         [-0.1,  0.0,  0.9,  1.0,  0.3, -0.5])
    # Instrumental / directive
    v.add("print",         [ 0.6,  0.8,  0.5,  0.6,  0.9, -0.6])
    v.add("run",           [ 0.5,  0.7,  0.4,  0.5,  0.8, -0.6])
    v.add("write",         [ 0.6,  0.7,  0.4,  0.6,  0.9, -0.5])
    v.add("show",          [ 0.4,  0.6,  0.5,  0.6,  0.8, -0.5])
    v.add("for me",        [ 0.4,  0.6,  0.9,  0.9,  1.0, -0.6])
    # Ideational content
    v.add("hello world",   [ 0.8,  0.9,  0.3,  0.4,  0.9, -0.6])
    v.add("code",          [ 0.7,  0.9,  0.2,  0.3,  0.8, -0.7])
    v.add("function",      [ 0.8,  1.0,  0.1,  0.2,  0.9, -0.7])
    v.add("output",        [ 0.6,  0.8,  0.2,  0.3,  0.8, -0.6])
    return v


def build_pilot_es() -> VocabularySpace:
    v = VocabularySpace(lang="ES")
    # Interpersonal / phatic
    v.add("buenos dias",   [-0.6, -0.3,  0.8,  0.7,  0.7,  0.4])
    v.add("hola",          [-0.5, -0.4,  0.7,  0.8,  0.5,  0.3])
    v.add("por favor",     [-0.2,  0.0,  0.9,  1.0,  0.4,  0.3])
    v.add("gracias",       [ 0.1,  0.2,  1.0,  1.0,  0.5,  0.3])
    v.add("perdon",        [-0.1,  0.0,  0.9,  1.0,  0.3,  0.3])
    # Temporal / factual
    v.add("hoy",           [-0.1,  0.2,  0.3,  0.4,  0.6,  0.4])
    v.add("viernes",       [ 0.2,  0.3,  0.2,  0.3,  0.7,  0.4])
    v.add("manana",        [ 0.1,  0.2,  0.2,  0.3,  0.6,  0.4])
    # Institutional / broadcast
    v.add("CNN",           [ 0.5,  1.0,  0.6,  0.2,  0.9,  0.8])
    v.add("noticias",      [ 0.4,  0.9,  0.4,  0.3,  0.8,  0.7])
    v.add("importante",    [ 0.6,  0.7,  0.7,  0.8,  0.8,  0.6])
    # Personal / evaluative
    v.add("para mi",       [ 0.5,  0.6,  0.8,  0.9,  0.7,  0.5])
    v.add("para muchos",   [ 0.7,  0.8,  0.8,  0.8,  0.9,  0.6])
    v.add("dia",           [ 0.3,  0.4,  0.4,  0.5,  0.6,  0.4])
    return v


def realize_trajectory(states: np.ndarray,
                       vocab: VocabularySpace,
                       k: int = 3) -> List[Dict]:
    """
    For each meaning state in a trajectory, retrieve the k nearest
    lexical items from vocab.

    Parameters
    ----------
    states : np.ndarray, shape (T, n_dim)
    vocab  : VocabularySpace
    k      : candidates per state

    Returns
    -------
    List of dicts with keys: step, state, candidates
    """
    results = []
    for t, state in enumerate(states):
        candidates = vocab.nearest(state, k=k)
        results.append({
            "step": t,
            "state": state.tolist(),
            "best": candidates[0][0],
            "candidates": candidates,
        })
    return results


def print_realization(results: List[Dict], lang: str, step_labels: List[str]):
    print(f"\n=== Realization [{lang}] ===\n")
    print(f"{'t':<3} {'source unit':<22} {'best match':<16} candidates")
    print("-" * 75)
    for r, lbl in zip(results, step_labels):
        cands = "  ".join(f"{w}({d:.2f})" for w, d in r["candidates"])
        print(f"{r['step']:<3} {lbl:<22} {r['best']:<16} {cands}")


if __name__ == "__main__":
    en_labels = ["hey", "why dont you", "print hello world", "for me", "please thank you"]
    en_states = np.array([
        [-0.7, -0.5,  0.8,  0.9,  0.6, -0.6],
        [-0.6, -0.3,  0.9,  0.9,  0.8, -0.6],
        [ 0.3,  0.6,  1.0,  0.8,  1.0, -0.6],
        [ 0.4,  0.6,  0.9,  0.9,  1.0, -0.6],
        [ 0.1,  0.6,  1.0,  1.0,  0.8, -0.6],
    ])
    es_labels = ["buenos dias", "hoy es viernes", "Esto es CNN", "dia importante", "y para muchos"]
    es_states = np.array([
        [-0.6, -0.3,  0.8,  0.7,  0.7,  0.4],
        [-0.2,  0.1,  0.8,  0.7,  0.9,  0.4],
        [ 0.3,  0.9,  1.0,  0.4,  1.0,  0.7],
        [ 0.5,  0.8,  0.9,  0.7,  1.0,  0.6],
        [ 0.7,  0.9,  1.0,  0.9,  1.0,  0.6],
    ])

    en_vocab = build_pilot_en()
    es_vocab = build_pilot_es()

    print(en_vocab)
    print(es_vocab)

    en_results = realize_trajectory(en_states, en_vocab)
    print_realization(en_results, "EN", en_labels)

    es_results = realize_trajectory(es_states, es_vocab)
    print_realization(es_results, "ES", es_labels)

    # Cross-language demo: same final state, two vocabularies
    final = en_states[-1]
    print("\n=== Cross-language realization: EN final state ===\n")
    print(f"  EN best match : {en_vocab.realize(final)}")
    print(f"  ES best match : {es_vocab.realize(final)}")
    print("  (same M_out, different V_L -- no translation)")
