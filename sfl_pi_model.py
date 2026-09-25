"""SFL-pi: causal transformer over 9D SFL meaning states.

Rows are ideational, interpersonal and textual metafunctions. Columns are
field, tenor and mode register variables. The flattened 9D state preserves
all cells; no fixed metafunction-register pairing is imposed.
"""
from dataclasses import dataclass
import torch
from torch import nn


@dataclass
class SFLPiConfig:
    state_dim: int = 9
    d_model: int = 128
    n_heads: int = 4
    n_layers: int = 4
    mlp_ratio: int = 4
    max_seq_len: int = 64
    dropout: float = 0.1


class CausalBlock(nn.Module):
    def __init__(self, cfg: SFLPiConfig):
        super().__init__()
        self.norm1 = nn.LayerNorm(cfg.d_model)
        self.attn = nn.MultiheadAttention(cfg.d_model, cfg.n_heads, dropout=cfg.dropout, batch_first=True)
        self.norm2 = nn.LayerNorm(cfg.d_model)
        self.mlp = nn.Sequential(
            nn.Linear(cfg.d_model, cfg.d_model * cfg.mlp_ratio),
            nn.GELU(),
            nn.Dropout(cfg.dropout),
            nn.Linear(cfg.d_model * cfg.mlp_ratio, cfg.d_model),
            nn.Dropout(cfg.dropout),
        )

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        length = x.size(1)
        mask = torch.triu(torch.ones(length, length, dtype=torch.bool, device=x.device), diagonal=1)
        y = self.norm1(x)
        y, _ = self.attn(y, y, y, attn_mask=mask, need_weights=False)
        x = x + y
        return x + self.mlp(self.norm2(x))


class SFLPi(nn.Module):
    def __init__(self, cfg: SFLPiConfig):
        super().__init__()
        self.cfg = cfg
        self.state_in = nn.Linear(cfg.state_dim, cfg.d_model)
        self.position = nn.Parameter(torch.zeros(1, cfg.max_seq_len, cfg.d_model))
        self.blocks = nn.ModuleList(CausalBlock(cfg) for _ in range(cfg.n_layers))
        self.norm = nn.LayerNorm(cfg.d_model)
        self.state_out = nn.Linear(cfg.d_model, cfg.state_dim)
        self.reset_parameters()

    def reset_parameters(self) -> None:
        nn.init.normal_(self.position, std=0.02)
        for module in self.modules():
            if isinstance(module, nn.Linear):
                nn.init.normal_(module.weight, mean=0.0, std=0.02)
                if module.bias is not None:
                    nn.init.zeros_(module.bias)

    def forward(self, states: torch.Tensor) -> torch.Tensor:
        if states.ndim != 3 or states.size(-1) != self.cfg.state_dim:
            raise ValueError(f"expected [batch, time, {self.cfg.state_dim}] states")
        if states.size(1) > self.cfg.max_seq_len:
            raise ValueError("sequence exceeds configured max_seq_len")
        x = self.state_in(states) + self.position[:, :states.size(1)]
        for block in self.blocks:
            x = block(x)
        return self.state_out(self.norm(x))

    def parameter_count(self) -> int:
        return sum(p.numel() for p in self.parameters())
