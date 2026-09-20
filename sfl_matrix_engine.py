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
import numpy as np


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
        return MeaningMatrix(updated)


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
