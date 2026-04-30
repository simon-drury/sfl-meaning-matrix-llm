# Manifold Sémantique 6D : Géométrie SFL

Théorie formelle de l'espace et des dynamiques.

## Espace d'État

**Manifold** : $\mathcal{M} = \mathbb{R}^6$ où chaque point encode un instant de sens.

| Dim | Interprétation LSF |
|-----|-------------------|
| 1 | idéationnelle : construction de l'expérience |
| 2 | interpersonnelle : énaction des relations |
| 3 | textuelle : organisation du discours |
| 4 | champ : domaine, technicité |
| 5 | tenor : hiérarchie, distance |
| 6 | mode : canal, oralité |

## Trajectoires et Deltas

Une trajectoire : $\mathbf{T} = (\mathbf{M}_0, \mathbf{M}_1, \ldots, \mathbf{M}_T)$

Un delta : $\Delta_t = \mathbf{M}_t - \mathbf{M}_{t-1}$

## Quantités Géométriques

**Déplacement** : $\delta_t = \|\Delta_t\|$

**Courbure** : $\kappa_t = \angle(\Delta_t, \Delta_{t+1})$

**Direction dominante** : $\phi_t = \arg\max_i |\Delta_t|_i$

**Longueur de chemin** : $L_{sp} = \sum_{t=1}^T \delta_t$

## Distance SFL Pondérée

$$d_{\text{SFL}}(\mathbf{M}, \mathbf{M}') = \sqrt{\sum_{i=1}^6 w_i (M_i - M'_i)^2}$$

Poids : idéat=1.0, interp=1.2, text=1.1, champ=0.8, tenor=1.0, mode=0.9.