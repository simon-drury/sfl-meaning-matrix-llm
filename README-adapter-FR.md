# Adaptateur SFL : Projection vers le Manifold 6D

## Rôle

`sfl_adapter.py` implémente la projection initiale vers l'espace sémantique 6D.

### Mathématique

Soit $\mathbf{x} \in \mathbb{R}^d$ une représentation d'entrée.

**Projection linéaire** :
$$\mathbf{M}_0 = \text{tanh}(\mathbf{W}_{\text{adapt}} \mathbf{x})$$

où $\mathbf{W}_{\text{adapt}} \in \mathbb{R}^{6 \times d}$.

**Normalisation** : chaque dimension à [-1, +1].

## Utilisation

```python
from sfl_adapter import SFLAdapter
adapter = SFLAdapter(input_dim=256, output_dim=6)
M0 = adapter.project(x)
```

## Configurabilité

Paramètre `ndim` configurable pour extension future.