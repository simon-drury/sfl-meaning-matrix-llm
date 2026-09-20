"""
sfl_attention.py — Decoupled Metafunctional Attention Engine
Architecture: Language As Social Semiotic Model (LASSM)
Evaluates clustered attention across 3x3 semiotic dimensions (Ideational, Interpersonal, Textual).
"""

import torch
import torch.nn as nn
import torch.nn.functional as F


class ClusteredMetafunctionalAttention(nn.Module):
    """
    Decoupled Functional Attention Engine operating over 9D semiotic states.
    Dedicated attention heads for Ideational, Interpersonal, and Textual strata.
    """
    def __init__(self, d_model: int = 768, n_strata: int = 3):
        super().__init__()
        self.d_model = d_model
        self.n_strata = n_strata
        self.head_dim = d_model // n_strata

        self.q_proj = nn.Linear(d_model, d_model)
        self.k_proj = nn.Linear(d_model, d_model)
        self.v_proj = nn.Linear(d_model, d_model)
        self.out_proj = nn.Linear(d_model, d_model)

    def forward(self, x: torch.Tensor, mask: torch.Tensor = None) -> torch.Tensor:
        batch_size, seq_len, _ = x.shape
        
        q = self.q_proj(x).view(batch_size, seq_len, self.n_strata, self.head_dim).transpose(1, 2)
        k = self.k_proj(x).view(batch_size, seq_len, self.n_strata, self.head_dim).transpose(1, 2)
        v = self.v_proj(x).view(batch_size, seq_len, self.n_strata, self.head_dim).transpose(1, 2)

        scores = torch.matmul(q, k.transpose(-2, -1)) / (self.head_dim ** 0.5)
        if mask is not None:
            scores = scores.masked_fill(mask == 0, -1e9)
            
        attn = F.softmax(scores, dim=-1)
        context = torch.matmul(attn, v).transpose(1, 2).contiguous().view(batch_size, seq_len, self.d_model)
        return self.out_proj(context)
