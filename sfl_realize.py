#!/usr/bin/env python3
"""
sfl_realize.py
Instantiation: meaning state -> lexical realization in language L.

The transformer outputs a meaning state M_out in the semiotic manifold M.
This module retrieves the lexical items whose semiotic fingerprints
f_w in M are closest to M_out, within the vocabulary space V_L
of a specified language L.

    w* = argmin_{w in V_L} || f_w - M_out ||_2

The same M_out presented independently to V_EN, V_ES, V_PT, V_IT, V_ZH
produces five co-equal realizations. There is no translation step.
This is instantiation of semiotic potential into language-specific form.

Vocabulary fingerprints
-----------------------
Each lexical item w in V_L is assigned a 6-dimensional semiotic
fingerprint f_w in [-1, 1]^6. In production these are learned from
SFL-annotated corpora. The pilot vocabulary below is hand-encoded
for validation using the iconic prompts.

Languages: EN, ES, PT, IT, ZH

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
    form: str
    lang: str
    fingerprint: np.ndarray


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
        Return the k semiotic units closest to M_out by Euclidean distance.

        w* = argmin_{w in V_L} || f_w - M_out ||_2
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
        return self.nearest(M_out, k=1)[0][0]

    def __len__(self):
        return len(self._items)

    def __repr__(self):
        return f"VocabularySpace(lang={self.lang}, n_dim={self.n_dim}, items={len(self)})"


# ---------------------------------------------------------------------------
# Pilot vocabularies
# Format: [ideational, field, interpersonal, tenor, textual, mode]
# Fingerprints are hand-encoded from iconic prompt analysis.
# In production: learned from SFL-annotated corpora.
# ---------------------------------------------------------------------------

def build_pilot_en() -> VocabularySpace:
    v = VocabularySpace(lang="EN")
    v.add("hey",           [-0.7, -0.5,  0.8,  0.9,  0.6, -0.6])
    v.add("hello",         [-0.6, -0.4,  0.7,  0.8,  0.5, -0.5])
    v.add("please",        [-0.2,  0.0,  0.9,  1.0,  0.4, -0.4])
    v.add("thank you",     [ 0.1,  0.2,  1.0,  1.0,  0.5, -0.5])
    v.add("sorry",         [-0.1,  0.0,  0.9,  1.0,  0.3, -0.5])
    v.add("print",         [ 0.6,  0.8,  0.5,  0.6,  0.9, -0.6])
    v.add("run",           [ 0.5,  0.7,  0.4,  0.5,  0.8, -0.6])
    v.add("write",         [ 0.6,  0.7,  0.4,  0.6,  0.9, -0.5])
    v.add("show",          [ 0.4,  0.6,  0.5,  0.6,  0.8, -0.5])
    v.add("for me",        [ 0.4,  0.6,  0.9,  0.9,  1.0, -0.6])
    v.add("hello world",   [ 0.8,  0.9,  0.3,  0.4,  0.9, -0.6])
    v.add("code",          [ 0.7,  0.9,  0.2,  0.3,  0.8, -0.7])
    v.add("function",      [ 0.8,  1.0,  0.1,  0.2,  0.9, -0.7])
    v.add("output",        [ 0.6,  0.8,  0.2,  0.3,  0.8, -0.6])
    return v


def build_pilot_es() -> VocabularySpace:
    v = VocabularySpace(lang="ES")
    v.add("buenos dias",   [-0.6, -0.3,  0.8,  0.7,  0.7,  0.4])
    v.add("hola",          [-0.5, -0.4,  0.7,  0.8,  0.5,  0.3])
    v.add("por favor",     [-0.2,  0.0,  0.9,  1.0,  0.4,  0.3])
    v.add("gracias",       [ 0.1,  0.2,  1.0,  1.0,  0.5,  0.3])
    v.add("perdon",        [-0.1,  0.0,  0.9,  1.0,  0.3,  0.3])
    v.add("hoy",           [-0.1,  0.2,  0.3,  0.4,  0.6,  0.4])
    v.add("viernes",       [ 0.2,  0.3,  0.2,  0.3,  0.7,  0.4])
    v.add("manana",        [ 0.1,  0.2,  0.2,  0.3,  0.6,  0.4])
    v.add("CNN",           [ 0.5,  1.0,  0.6,  0.2,  0.9,  0.8])
    v.add("noticias",      [ 0.4,  0.9,  0.4,  0.3,  0.8,  0.7])
    v.add("importante",    [ 0.6,  0.7,  0.7,  0.8,  0.8,  0.6])
    v.add("para mi",       [ 0.5,  0.6,  0.8,  0.9,  0.7,  0.5])
    v.add("para muchos",   [ 0.7,  0.8,  0.8,  0.8,  0.9,  0.6])
    v.add("dia",           [ 0.3,  0.4,  0.4,  0.5,  0.6,  0.4])
    return v


def build_pilot_pt() -> VocabularySpace:
    """
    Portuguese pilot vocabulary.
    Fingerprints derived from ES by applying mode shift (+0.1 spoken
    channel weight) and minor tenor adjustments for BP register norms.
    """
    v = VocabularySpace(lang="PT")
    v.add("ola",            [-0.6, -0.4,  0.7,  0.8,  0.5,  0.4])
    v.add("bom dia",        [-0.6, -0.3,  0.8,  0.7,  0.7,  0.5])
    v.add("por favor",      [-0.2,  0.0,  0.9,  1.0,  0.4,  0.4])
    v.add("obrigado",       [ 0.1,  0.2,  1.0,  1.0,  0.5,  0.4])
    v.add("desculpe",       [-0.1,  0.0,  0.9,  1.0,  0.3,  0.4])
    v.add("hoje",           [-0.1,  0.2,  0.3,  0.4,  0.6,  0.5])
    v.add("sexta-feira",    [ 0.2,  0.3,  0.2,  0.3,  0.7,  0.5])
    v.add("imprimir",       [ 0.6,  0.8,  0.5,  0.6,  0.9, -0.5])
    v.add("codigo",         [ 0.7,  0.9,  0.2,  0.3,  0.8, -0.6])
    v.add("importante",     [ 0.6,  0.7,  0.7,  0.8,  0.8,  0.6])
    v.add("noticias",       [ 0.4,  0.9,  0.4,  0.3,  0.8,  0.7])
    v.add("para mim",       [ 0.5,  0.6,  0.8,  0.9,  0.7,  0.5])
    v.add("para muitos",    [ 0.7,  0.8,  0.8,  0.8,  0.9,  0.6])
    v.add("ola mundo",      [ 0.8,  0.9,  0.3,  0.4,  0.9, -0.5])
    return v


def build_pilot_it() -> VocabularySpace:
    """
    Italian pilot vocabulary.
    Italian register is closer to ES in tenor but has higher formality
    gradient in institutional contexts (mode shift toward written).
    """
    v = VocabularySpace(lang="IT")
    v.add("ciao",           [-0.6, -0.4,  0.8,  0.9,  0.5,  0.3])
    v.add("buongiorno",     [-0.6, -0.3,  0.7,  0.7,  0.7,  0.4])
    v.add("per favore",     [-0.2,  0.0,  0.9,  1.0,  0.4,  0.3])
    v.add("grazie",         [ 0.1,  0.2,  1.0,  1.0,  0.5,  0.3])
    v.add("scusa",          [-0.1,  0.0,  0.9,  1.0,  0.3,  0.3])
    v.add("oggi",           [-0.1,  0.2,  0.3,  0.4,  0.6,  0.4])
    v.add("venerdi",        [ 0.2,  0.3,  0.2,  0.3,  0.7,  0.4])
    v.add("stampa",         [ 0.6,  0.8,  0.5,  0.6,  0.9, -0.6])
    v.add("codice",         [ 0.7,  0.9,  0.2,  0.3,  0.8, -0.7])
    v.add("importante",     [ 0.6,  0.7,  0.7,  0.8,  0.8,  0.5])
    v.add("notizie",        [ 0.4,  0.9,  0.4,  0.3,  0.8,  0.7])
    v.add("per me",         [ 0.5,  0.6,  0.8,  0.9,  0.7,  0.4])
    v.add("per molti",      [ 0.7,  0.8,  0.8,  0.8,  0.9,  0.6])
    v.add("ciao mondo",     [ 0.8,  0.9,  0.3,  0.4,  0.9, -0.6])
    return v


def build_pilot_zh() -> VocabularySpace:
    """
    Mandarin Chinese pilot vocabulary.
    ZH register differs from Romance languages in two key dimensions:
    - mode: written Mandarin scores higher (more formal written channel)
    - tenor: institutional register has lower interpersonal weight
      (institutional distance is encoded lexically, not prosodically)
    Fingerprints adjusted accordingly.
    """
    v = VocabularySpace(lang="ZH")
    v.add("ni hao",         [-0.5, -0.3,  0.7,  0.7,  0.6,  0.2])  # hello
    v.add("zao shang hao",  [-0.5, -0.2,  0.7,  0.6,  0.7,  0.5])  # good morning
    v.add("qing",           [-0.2,  0.0,  0.8,  0.9,  0.5,  0.3])  # please
    v.add("xie xie",        [ 0.1,  0.2,  0.9,  0.9,  0.5,  0.3])  # thank you
    v.add("duibuqi",        [-0.1,  0.0,  0.8,  0.9,  0.3,  0.3])  # sorry
    v.add("jintian",        [-0.1,  0.2,  0.2,  0.3,  0.6,  0.6])  # today
    v.add("xingqiwu",       [ 0.2,  0.3,  0.1,  0.2,  0.7,  0.6])  # Friday
    v.add("dayin",          [ 0.6,  0.8,  0.4,  0.5,  0.9,  0.1])  # print
    v.add("daima",          [ 0.7,  0.9,  0.1,  0.2,  0.8, -0.2])  # code
    v.add("zhongyao",       [ 0.6,  0.7,  0.5,  0.6,  0.8,  0.6])  # important
    v.add("xinwen",         [ 0.4,  0.9,  0.3,  0.2,  0.8,  0.8])  # news
    v.add("dui wo lai shuo",[ 0.5,  0.6,  0.7,  0.8,  0.7,  0.5])  # for me
    v.add("ni hao shijie",  [ 0.8,  0.9,  0.2,  0.3,  0.9,  0.1])  # hello world
    v.add("dajia",          [ 0.7,  0.8,  0.7,  0.7,  0.9,  0.6])  # everyone
    return v


def realize_trajectory(states: np.ndarray,
                       vocab: VocabularySpace,
                       k: int = 3) -> List[Dict]:
    """
    For each meaning state in a trajectory, retrieve the k nearest
    semiotic units from vocab.
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
    print(f"\n=== Instantiation [{lang}] ===\n")
    print(f"{'t':<3} {'semiotic unit':<24} {'best match':<20} candidates")
    print("-" * 80)
    for r, lbl in zip(results, step_labels):
        cands = "  ".join(f"{w}({d:.2f})" for w, d in r["candidates"])
        print(f"{r['step']:<3} {lbl:<24} {r['best']:<20} {cands}")


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
    pt_vocab = build_pilot_pt()
    it_vocab = build_pilot_it()
    zh_vocab = build_pilot_zh()

    for vocab in [en_vocab, es_vocab, pt_vocab, it_vocab, zh_vocab]:
        print(vocab)

    en_results = realize_trajectory(en_states, en_vocab)
    print_realization(en_results, "EN", en_labels)

    es_results = realize_trajectory(es_states, es_vocab)
    print_realization(es_results, "ES", es_labels)

    # Five-language demo: EN final state -> all five vocabularies
    final = en_states[-1]
    print("\n=== Five-language instantiation: EN final state (please thank you) ===\n")
    print("  Same M_out. Five vocabulary spaces. No translation.\n")
    for vocab in [en_vocab, es_vocab, pt_vocab, it_vocab, zh_vocab]:
        best = vocab.realize(final)
        print(f"  {vocab.lang:<4} best match: {best}")

    # ES final state -> all five
    final_es = es_states[-1]
    print("\n=== Five-language instantiation: ES final state (y para muchos) ===\n")
    print("  Same M_out. Five vocabulary spaces. No translation.\n")
    for vocab in [en_vocab, es_vocab, pt_vocab, it_vocab, zh_vocab]:
        best = vocab.realize(final_es)
        print(f"  {vocab.lang:<4} best match: {best}")
