"""
sfl_matrix_engine_v3.py — 3x3 Continuous Semiotic Manifold Engine
Architecture: Language As Social Semiotic Model (LASSM)
Formal Specification: 3x3 Functional-Semantic Meaning Matrix (M_t in R^{3x3})

Rows: Metafunctional Strata (Ideational, Interpersonal, Textual)
Cols: Situational Register Dimensions (Field, Tenor, Mode)

Author: sjd (Simon Drury) / LASSM Framework
"""

from dataclasses import dataclass
from typing import List, Optional, Tuple, Dict, Any
import numpy as np


METAFUNCTIONS = ["ideational", "interpersonal", "textual"]
REGISTERS = ["field", "tenor", "mode"]


@dataclass
class SemioticMatrix3x3:
    """
    Native 3x3 Meaning Matrix representation M_t.
    Holds 9 scalar expectation coordinates bounded in [-1.0, 1.0].
    
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
    def zeros(cls) -> "SemioticMatrix3x3":
        return cls(np.zeros((3, 3), dtype=np.float32))

    @classmethod
    def from_vector_9d(cls, vec: np.ndarray) -> "SemioticMatrix3x3":
        v = np.asarray(vec, dtype=np.float32).reshape((3, 3))
        return cls(v)

    def to_vector_9d(self) -> np.ndarray:
        """
        Unrolled 9D vector m in [-1.0, 1.0]^9.
        Compatible with downstream neural adapters (W_adapt).
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

    def apply_delta(self, delta: np.ndarray) -> "SemioticMatrix3x3":
        """
        M_t = clip(M_{t-1} + Delta_t, -1.0, 1.0)
        """
        delta = np.asarray(delta, dtype=np.float32)
        if delta.shape != (3, 3):
            raise ValueError(f"Delta shape must be (3, 3), got {delta.shape}")
        updated = np.clip(self.matrix + delta, -1.0, 1.0)
        return SemioticMatrix3x3(updated)


class SemioticManifold3x3:
    """
    Trajectory geometry and metric tensor calculations across 3x3 semiotic manifolds.
    """
    def __init__(self, metric_weights: Optional[np.ndarray] = None):
        if metric_weights is None:
            self.weights = np.ones(9, dtype=np.float32)
        else:
            self.weights = np.asarray(metric_weights, dtype=np.float32).flatten()
            if self.weights.shape != (9,):
                raise ValueError("Metric weights must be length 9")

    def step_displacement(self, m_prev: SemioticMatrix3x3, m_curr: SemioticMatrix3x3) -> float:
        """
        ||delta_t||_2 = ||m_curr - m_prev||_2
        """
        v_diff = m_curr.to_vector_9d() - m_prev.to_vector_9d()
        weighted_diff = v_diff * np.sqrt(self.weights)
        return float(np.linalg.norm(weighted_diff))

    def step_curvature(
        self,
        m_prev: SemioticMatrix3x3,
        m_curr: SemioticMatrix3x3,
        m_next: SemioticMatrix3x3
    ) -> float:
        """
        Local trajectory curvature:
        kappa_t = 1.0 - (delta_t . delta_{t-1}) / (||delta_t|| * ||delta_{t-1}||)
        """
        d1 = m_curr.to_vector_9d() - m_prev.to_vector_9d()
        d2 = m_next.to_vector_9d() - m_curr.to_vector_9d()
        
        norm1 = np.linalg.norm(d1)
        norm2 = np.linalg.norm(d2)
        
        if norm1 < 1e-8 or norm2 < 1e-8:
            return 0.0
        
        cosine = np.dot(d1, d2) / (norm1 * norm2)
        cosine = np.clip(cosine, -1.0, 1.0)
        return float(1.0 - cosine)

    def trajectory_path_loss(self, states: List[SemioticMatrix3x3]) -> float:
        """
        Path loss L_sp across an ordered sequence of matrices:
        L_sp = sum_{t=1}^{T} ||delta_t||_2^2
        """
        if len(states) < 2:
            return 0.0
        
        total_loss = 0.0
        for t in range(1, len(states)):
            disp = self.step_displacement(states[t-1], states[t])
            total_loss += disp ** 2
        return float(total_loss)
