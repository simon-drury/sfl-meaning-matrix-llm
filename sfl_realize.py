"""
sfl_realize.py — 9D Boundary Surface Realization
Architecture: Language As Social Semiotic Model (LASSM)
Executes Euclidean nearest-neighbor lookup across 9D coordinate fingerprints f_w in R^9.
"""

from typing import Dict, List, Tuple
import numpy as np


class BoundaryRealizer9D:
    """
    Terminal system boundary realization.
    Selects surface items w in V via w* = argmin ||m_out - f_w||_2.
    """
    def __init__(self):
        # Initial 9D coordinate fingerprints across target vocabulary
        self.lexicon_9d: Dict[str, np.ndarray] = {
            "hey": np.array([0.2, 0.1, 0.2, -0.4, -0.8, -0.5, 0.1, -0.3, -0.6], dtype=np.float32),
            "please": np.array([0.3, 0.2, 0.3, 0.5, 0.7, 0.3, 0.3, 0.2, 0.2], dtype=np.float32),
            "print": np.array([0.8, 0.3, 0.4, 0.0, -0.2, -0.3, 0.4, 0.2, 0.4], dtype=np.float32),
            "report": np.array([0.7, 0.4, 0.5, 0.1, 0.2, 0.2, 0.5, 0.3, 0.5], dtype=np.float32),
            "server": np.array([0.8, 0.3, 0.4, 0.0, 0.1, 0.1, 0.5, 0.4, 0.7], dtype=np.float32),
            "operational": np.array([0.7, 0.2, 0.3, 0.1, 0.4, 0.5, 0.4, 0.3, 0.6], dtype=np.float32),
            "immediately": np.array([0.5, 0.5, 0.5, 0.8, 0.9, 0.7, 0.7, 0.8, 0.8], dtype=np.float32)
        }

    def realize(self, m_out: np.ndarray, top_k: int = 1) -> List[Tuple[str, float]]:
        m_vec = np.asarray(m_out, dtype=np.float32).flatten()
        if len(m_vec) != 9:
            raise ValueError(f"Expected 9D vector for realization, got {len(m_vec)}")

        distances = []
        for word, fw in self.lexicon_9d.items():
            dist = float(np.linalg.norm(m_vec - fw))
            distances.append((word, dist))

        distances.sort(key=lambda x: x[1])
        return distances[:top_k]
