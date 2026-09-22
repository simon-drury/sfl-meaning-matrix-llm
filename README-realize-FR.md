# sfl_realize.py — Réalisation Lexicale (FR)

Mappe un état de sortie 9D $M_{\text{out}} \in [-1,1]^9$ vers l’élément lexical le plus proche dans le vocabulaire empirique.

## Comment ça fonctionne

$$w^* = \arg\min_{w \in \mathcal{V}} \|\hat{\mathbf{m}}_{\text{out}} - \mathbf{f}_w\|_2$$

où $\mathbf{f}_w$ est le centroide 9D empirique de l’élément lexical $w$.

- **Entrée** : vecteur 9D $\mathbf{m}_{\text{out}} \in [-1,1]^9$
- **Vocabulaire** : `data/empirical_vocabulary_9d.json` — 32 580 items avec centroides empiriques
- **Sortie** : meilleure correspondance + candidats classés avec distances euclidiennes
- **Multilingue** : même M_out présenté indépendamment aux vocabulaires EN, ES, FR — sans traduction

## Exécuter

```bash
python sfl_realize.py
```
