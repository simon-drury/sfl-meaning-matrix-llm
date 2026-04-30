# Réalisation Lexique : Voisinage Pondéré SFL

Donné un état M, comment sélectionner les mots?

## Algorithme : Nearest-Neighbor SFL

Chaque mot $w$ a une signature $\mathbf{v}_w \in \mathbb{R}^6$.

**Score** : $\text{score}(w | \mathbf{M}) = -d_{\text{SFL}}(\mathbf{M}, \mathbf{v}_w)$

**Réalisation** : $w^* = \arg\max_w \text{score}(w | \mathbf{M})$

## Vocabulaire Pilot Français

| Mot | Signature 6D |
|-----|-----|
| merci | (0.0, 0.95, 0.2, 0.1, 0.5, 0.3) |
| s'il te plaît | (-0.1, 0.85, 0.0, 0.1, 0.6, 0.2) |
| bonjour | (0.1, 0.7, 0.3, 0.2, 0.3, 0.1) |
| oui | (0.3, 0.2, -0.1, 0.2, 0.4, -0.2) |
| non | (0.2, -0.4, 0.1, 0.2, 0.4, -0.3) |
| vraiment | (0.5, 0.3, -0.2, 0.3, 0.3, 0.2) |
| peut-être | (0.4, -0.1, 0.2, 0.4, 0.3, 0.1) |
| salut | (0.2, 0.5, 0.4, 0.0, 0.2, 0.3) |