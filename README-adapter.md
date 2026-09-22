# sfl_adapter.py — Linear Adapter

Projects transformer hidden states into the 9D semiotic manifold.

## Architecture

$$W_{\text{adapt}} \in \mathbb{R}^{d_{\text{model}} \times 9}$$

Maps from transformer hidden dimension $d_{\text{model}}$ to the 9D meaning-state coordinate space $[-1,1]^9$.

The 9 output dimensions correspond to the 3×3 matrix:

| | Field | Tenor | Mode |
|---|---|---|---|
| **Ideational** | (0) | (1) | (2) |
| **Interpersonal** | (3) | (4) | (5) |
| **Textual** | (6) | (7) | (8) |

## Notes

- Modular and swappable: the transformer backbone does not change when the adapter is updated
- Tier 2: full LoRA training of $W_{\text{adapt}}$ toward a pretrained backbone (Llama-3.2) is in progress
- See `wadapt_lora_training_sketch.ipynb` for the training sketch
