# Adaptateur SFL : Projection depuis le Manifold 9D

## Rôle

`sfl_adapter.py` implémente la projection de l'espace sémantique 9D (matrice 3x3 dépliée) vers l'espace d'embedding du transformeur.

### Mathématique

Soit $\mathbf{m} \in [-1, +1]^9$ l'état de sens déplié.

**Projection linéaire** :
$$\mathbf{e} = \mathbf{W}_{\text{adapt}} \mathbf{m} + \mathbf{b}$$

où $\mathbf{W}_{\text{adapt}} \in \mathbb{R}^{d \times 9}$.

## Utilisation

```python
from sfl_adapter import SFLAdapter
adapter = SFLAdapter(in_features=9, d_model=768)
e = adapter(m)
```
