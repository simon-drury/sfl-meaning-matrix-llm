# sfl_adapter.py — Adaptador Lineal (ES)

Proyecta estados ocultos del transformer al espacio semiótico 9D.

## Arquitectura

$$W_{\text{adapt}} \in \mathbb{R}^{d_{\text{model}} \times 9}$$

Mapea desde $d_{\text{model}}$ al espacio de coordenadas 9D $[-1,1]^9$.

Las 9 dimensiones de salida corresponden a la matriz 3×3:

| | Campo | Tenor | Modo |
|---|---|---|---|
| **Ideacional** | (0) | (1) | (2) |
| **Interpersonal** | (3) | (4) | (5) |
| **Textual** | (6) | (7) | (8) |

## Notas

- Modular e intercambiable: el backbone no cambia cuando se actualiza el adaptador
- Tier 2: entrenamiento LoRA completo hacia Llama-3.2 en curso
- Ver `wadapt_lora_training_sketch.ipynb`
