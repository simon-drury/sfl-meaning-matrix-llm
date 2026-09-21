"""
sfl_manifold.py — 9D Semiotic Manifold Geometry & Trajectory Metrics
Architecture: Language As Social Semiotic Model (LASSM)
Calculates displacement, local curvature, metric tensors, and geodesic path loss across R^{3x3} (9D).
"""

from typing import List, Optional
import numpy as np
from sfl_matrix_engine import MeaningMatrix


class SemioticManifold:
    """
    Riemannian-inspired geometry engine over 3x3 functional-semantic matrices.
    Operates over unrolled 9D coordinates bounded in [-1.0, 1.0].
    """
    def __init__(self, metric_weights: Optional[np.ndarray] = None):
        if metric_weights is None:
            self.weights = np.ones(9, dtype=np.float32)
        else:
            self.weights = np.asarray(metric_weights, dtype=np.float32).flatten()
            if self.weights.shape != (9,):
                raise ValueError("Metric weights must be of length 9")

    def step_displacement(self, m_prev: MeaningMatrix, m_curr: MeaningMatrix) -> float:
        """
        Calculates weighted Euclidean step displacement:
        ||Delta_t||_2 = sqrt( sum( w_i * (m_curr_i - m_prev_i)^2 ) )
        """
        diff = m_curr.to_vector() - m_prev.to_vector()
        weighted = diff * np.sqrt(self.weights)
        return float(np.linalg.norm(weighted))

    def step_curvature(
        self,
        m_prev: MeaningMatrix,
        m_curr: MeaningMatrix,
        m_next: MeaningMatrix
    ) -> float:
        """
        Local trajectory curvature:
        kappa_t = 1.0 - (Delta_t . Delta_{t-1}) / (||Delta_t|| * ||Delta_{t-1}||)
        """
        d1 = m_curr.to_vector() - m_prev.to_vector()
        d2 = m_next.to_vector() - m_curr.to_vector()

        norm1 = np.linalg.norm(d1)
        norm2 = np.linalg.norm(d2)

        if norm1 < 1e-8 or norm2 < 1e-8:
            return 0.0

        cosine = float(np.dot(d1, d2) / (norm1 * norm2))
        cosine = max(min(cosine, 1.0), -1.0)
        return float(1.0 - cosine)

    def trajectory_path_loss(self, states: List[MeaningMatrix]) -> float:
        """
        Discourse path loss L_sp across an ordered sequence of states:
        L_sp = sum_{t=1}^{T} ||Delta_t||_2^2
        """
        if len(states) < 2:
            return 0.0

        total_loss = 0.0
        for t in range(1, len(states)):
            disp = self.step_displacement(states[t-1], states[t])
            total_loss += disp ** 2
        return float(total_loss)
