"""
sfl_adapter.py — 9D Semiotic Manifold Adapter Layer for Transformers
Architecture: Language As Social Semiotic Model (LASSM)
Maps 9D continuous semiotic states m in [-1.0, 1.0]^9 to transformer hidden space d_model.
"""

import torch
import torch.nn as nn
from typing import Optional


class SFLAdapter(nn.Module):
    """
    Linear and LoRA-style projection adapter: R^9 -> R^{d_model}.
    Initializes transformer hidden state from 3x3 semiotic matrix coordinates.
    """
    def __init__(self, in_features: int = 9, d_model: int = 768, bias: bool = True):
        super().__init__()
        self.in_features = in_features
        self.d_model = d_model
        self.w_adapt = nn.Linear(in_features, d_model, bias=bias)

    def forward(self, m_state: torch.Tensor) -> torch.Tensor:
        """
        m_state: Tensor of shape (batch_size, 9) or (batch_size, 3, 3)
        Returns: Tensor of shape (batch_size, d_model)
        """
        if m_state.dim() == 3 and m_state.shape[-2:] == (3, 3):
            m_state = m_state.flatten(start_dim=-2)
        elif m_state.shape[-1] != self.in_features:
            raise ValueError(f"Expected input last dim {self.in_features}, got {m_state.shape[-1]}")
            
        return self.w_adapt(m_state)
