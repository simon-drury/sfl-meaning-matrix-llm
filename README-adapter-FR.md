# sfl_adapter.py — Adaptateur Linéaire (FR)

Projecte les états cachés du transformer dans l’espace sémiotique 9D.

## Architecture

$$W_{\text{adapt}} \in \mathbb{R}^{d_{\text{model}} \times 9}$$

Mappie depuis $d_{\text{model}}$ vers l’espace de coordonnées 9D $[-1,1]^9$.

Les 9 dimensions de sortie correspondent à la matrice 3×3 :

| | Champ | Tenor | Mode |
|---|---|---|---|
| **Idéationnelle** | (0) | (1) | (2) |
| **Interpersonnelle** | (3) | (4) | (5) |
| **Textuelle** | (6) | (7) | (8) |

## Notes

- Modulaire et interchangeable : le backbone ne change pas lorsque l’adaptateur est mis à jour
- Tier 2 : entraînement LoRA complet vers Llama-3.2 en cours
- Voir `wadapt_lora_training_sketch.ipynb`
