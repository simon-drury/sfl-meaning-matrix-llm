"""
sfl_matrix_engine.py — Canonical 3x3 Systemic Functional Linguistics Manifold Engine
Architecture: Language As Social Semiotic Model (LASSM)
Formal Specification: 3x3 Functional-Semantic Meaning Matrix (M_t in R^{3x3})

Rows: Metafunctional Strata (Ideational, Interpersonal, Textual)
Cols: Situational Register Dimensions (Field, Tenor, Mode)

Author: Simon Drury (sjd) / LASSM Framework
"""

from dataclasses import dataclass
from typing import List, Optional, Tuple, Dict, Any
import re
import numpy as np

__all__ = [
    "METAFUNCTIONS",
    "REGISTERS",
    "MeaningMatrix",
    "SFLMatrixEngine",
    "MeaningTrajectory",
    "encode_en",
    "encode_es",
    "EN_PROMPT",
    "ES_PROMPT",
]


METAFUNCTIONS = ["ideational", "interpersonal", "textual"]
REGISTERS = ["field", "tenor", "mode"]


@dataclass
class MeaningMatrix:
    """
    Canonical 3x3 Meaning Matrix representation M_t.
    Holds 9 continuous expectation coordinates bounded in [-1.0, 1.0].
    
    Structure:
    [[m_id_field,  m_id_tenor,  m_id_mode],
     [m_int_field, m_int_tenor, m_int_mode],
     [m_txt_field, m_txt_tenor, m_txt_mode]]
    """
    matrix: np.ndarray  # Shape (3, 3)
    label: str = ""

    def __post_init__(self):
        self.matrix = np.asarray(self.matrix, dtype=np.float32)
        if self.matrix.shape != (3, 3):
            raise ValueError(f"Expected shape (3, 3), got {self.matrix.shape}")
        self.matrix = np.clip(self.matrix, -1.0, 1.0)

    @classmethod
    def zeros(cls) -> "MeaningMatrix":
        return cls(np.zeros((3, 3), dtype=np.float32))

    @classmethod
    def from_vector(cls, vec: np.ndarray) -> "MeaningMatrix":
        v = np.asarray(vec, dtype=np.float32).reshape((3, 3))
        return cls(v)

    def to_vector(self) -> np.ndarray:
        """
        Unrolled 9D vector m in [-1.0, 1.0]^9 for downstream neural adapters.
        """
        return self.matrix.flatten()

    def metafunctional_covariance(self) -> np.ndarray:
        """
        C_meta = M * M^T in R^{3x3}.
        Evaluates internal semantic coupling across functional strata.
        """
        return np.matmul(self.matrix, self.matrix.T)

    def register_covariance(self) -> np.ndarray:
        """
        C_register = M^T * M in R^{3x3}.
        Evaluates contextual coupling across register dimensions.
        """
        return np.matmul(self.matrix.T, self.matrix)

    def apply_delta(self, delta: np.ndarray) -> "MeaningMatrix":
        """
        M_t = clip(M_{t-1} + Delta_t, -1.0, 1.0)
        """
        delta = np.asarray(delta, dtype=np.float32)
        if delta.shape != (3, 3):
            raise ValueError(f"Delta shape must be (3, 3), got {delta.shape}")
        updated = np.clip(self.matrix + delta, -1.0, 1.0)
        return MeaningMatrix(updated, self.label)


class SFLMatrixEngine:
    """
    Canonical semantic parser and trajectory generator into continuous 3x3 semiotic space.
    """
    def __init__(self):
        pass

    def encode_text(self, text: str) -> MeaningMatrix:
        """
        Encodes surface discourse into initial 3x3 meaning matrix M_0.
        """
        m = np.zeros((3, 3), dtype=np.float32)
        text_lower = text.lower()

        # Ideational evaluation
        if any(w in text_lower for w in ["print", "analyze", "run", "restarted", "build"]):
            m[0, 0] = 0.75  # High field activity
            m[0, 1] = 0.30
            m[0, 2] = 0.40
        else:
            m[0, 0] = 0.20
            m[0, 1] = 0.10
            m[0, 2] = 0.20

        # Interpersonal evaluation
        if any(w in text_lower for w in ["please", "could", "would"]):
            m[1, 0] = 0.30
            m[1, 1] = 0.60  # Consultative/polite tenor
            m[1, 2] = 0.40
        elif any(w in text_lower for w in ["shall", "must", "immediately"]):
            m[1, 0] = 0.80
            m[1, 1] = 0.90  # High authority/frozen
            m[1, 2] = 0.70
        else:
            m[1, 0] = 0.10
            m[1, 1] = -0.50  # Informal/direct
            m[1, 2] = -0.20

        # Textual evaluation
        if text_lower.startswith(("in the", "when", "after", "if")):
            m[2, 0] = 0.60
            m[2, 1] = 0.40
            m[2, 2] = 0.85  # Marked structural theme
        else:
            m[2, 0] = 0.40
            m[2, 1] = 0.30
            m[2, 2] = 0.50

        return MeaningMatrix(m)


@dataclass
class MeaningTrajectory:
    """
    Ordered sequence of 3x3 meaning states M_0..M_T for one discourse.
    """
    lang: str
    states: List[MeaningMatrix]

    @property
    def final_state(self) -> MeaningMatrix:
        return self.states[-1]

    @property
    def labels(self) -> List[str]:
        return [s.label for s in self.states]

    def vectors(self) -> np.ndarray:
        """Stack of unrolled 9D vectors, shape (T+1, 9)."""
        return np.array([s.to_vector() for s in self.states])


EN_PROMPT = "hey why dont you print hello world for me please thank you"
ES_PROMPT = "buenos días, hoy es viernes. Esto es CNN. Hoy es un día importante para mí y para muchos."

_EN_UNITS = ["hey", "why dont you", "print hello world", "for me", "please thank you"]
_ES_UNITS = ["buenos días", "hoy es viernes", "Esto es CNN",
             "Hoy es un día importante para mí", "y para muchos"]

_ES_CUES = {
    "ideational": ["es", "hoy", "día", "viernes", "importante", "cnn"],
    "polite": ["por favor", "gracias", "buenos"],
    "imperative": ["debe", "inmediatamente"],
    "marked_theme": ["hoy", "buenos", "esto", "y para"],
}


def _encode_units(lang: str, units: List[str], engine: SFLMatrixEngine, encode_unit) -> MeaningTrajectory:
    """M_0 from the first unit; each later unit contributes a delta Delta_t."""
    states = [MeaningMatrix(encode_unit(units[0]).matrix, "M0")]
    for t, unit in enumerate(units[1:], start=1):
        target = encode_unit(unit).matrix
        delta = 0.5 * (target - states[-1].matrix)
        nxt = states[-1].apply_delta(delta)
        nxt.label = f"M{t}"
        states.append(nxt)
    return MeaningTrajectory(lang=lang, states=states)


def encode_en(prompt: Optional[str] = None) -> MeaningTrajectory:
    """Encode an English prompt (default: the iconic pilot prompt) into a MeaningTrajectory."""
    text = EN_PROMPT if prompt is None else prompt
    engine = SFLMatrixEngine()
    units = list(_EN_UNITS) if text.strip() == EN_PROMPT else [
        p.strip() for p in re.split(r"[,.;:!?]+", text) if p.strip()] or [text.strip()]
    return _encode_units("EN", units, engine, engine.encode_text)


def _encode_es_unit(engine: SFLMatrixEngine, unit: str) -> MeaningMatrix:
    lower = unit.lower()
    m = np.zeros((3, 3), dtype=np.float32)
    if any(w in lower.split() for w in _ES_CUES["ideational"]):
        m[0] = [0.50, 0.30, 0.40]
    else:
        m[0] = [0.20, 0.10, 0.20]
    if any(w in lower for w in _ES_CUES["polite"]):
        m[1] = [0.30, 0.60, 0.40]
    elif any(w in lower for w in _ES_CUES["imperative"]):
        m[1] = [0.80, 0.90, 0.70]
    else:
        m[1] = [0.10, 0.20, -0.20]
    if any(lower.startswith(w) for w in _ES_CUES["marked_theme"]):
        m[2] = [0.60, 0.40, 0.85]
    else:
        m[2] = [0.40, 0.30, 0.50]
    return MeaningMatrix(m)


def encode_es(prompt: Optional[str] = None) -> MeaningTrajectory:
    """Encode a Spanish prompt (default: the iconic pilot prompt) into a MeaningTrajectory."""
    text = ES_PROMPT if prompt is None else prompt
    engine = SFLMatrixEngine()
    units = list(_ES_UNITS) if text.strip() == ES_PROMPT else [
        p.strip() for p in re.split(r"[,.;:!?]+", text) if p.strip()] or [text.strip()]
    return _encode_units("ES", units, engine, lambda u: _encode_es_unit(engine, u))
