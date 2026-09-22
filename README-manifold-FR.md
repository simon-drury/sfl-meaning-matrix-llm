# sfl_manifold.py — Géométrie du Manifold Sémiotique (FR)

Impémente la géométrie riemannienne du manifold sémiotique continu M.

## Quantités

| Symbole | Nom | Ce qu’il mesure |
|---------|-----|-----------------|
| $\Delta_t$ | déplacement | de combien l’état de signification s’est déplacé à l’étape t |
| $\kappa_t$ | courbure | à quel point la trajectoire a tourné brusquement |
| $\phi_t$ | dimension motrice | laquelle des 9 dimensions a piloté le mouvement |
| $E(\gamma)$ | énergie géodésique | distance sémantique totale parcourue |

## L’espace d’états

$$\mathbf{m}_t = \operatorname{vec}(M_t) \in [-1.0, 1.0]^9$$

Lignes : métafonctions Idéationnelle, Interpersonnelle, Textuelle.  
Colonnes : dimensions de registre Champ, Tenor, Mode.

## Exécuter

```bash
python sfl_manifold.py
```

Voir `MANIFOLD.md` pour la spécification formelle complète.
