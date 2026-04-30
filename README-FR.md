# Matrice de Sens SFL pour LLM

**Une architecture basée sur la linguistique systémique fonctionnelle** : au lieu de tokeniser lexicalement, on compile directement en trajectoires sémantiques dans un manifold 6D.

## Principes Fondamentaux

La linguistique systémique fonctionnelle (LSF) de Halliday pose que la signification réside dans la **fonction en contexte**, pas dans la structure. Notre système applique ce principe au calcul :

- **Métafonctions** : idéationnelle (construire l'expérience), interpersonnelle (enacter les relations), textuelle (organiser le texte)
- **Variables contextuelles** : champ (ce qui se passe), tenor (rôles sociaux), mode (canal de communication)
- **Instantiation dynamique** : chaque matrice Mₜ capture un moment du sens, les deltas Δt encodent comment le sens évolue, pas quels mots viennent après

## Pipeline : Forme → Sens → Forme

```
entrée (lexique) 
    ↓ 
projection M₀ (adapter SFL)
    ↓ 
traitement (attention clusters, deltas)
    ↓ 
réalisation (nearest-neighbor dans vocabulaire LSF)
    ↓ 
sortie (lexique)
```

Le réseau de neurones est un **calculateur**, pas la théorie. La théorie est SFL.

## Pilot Iconique Français

**Entrée** : "Salut, peux-tu m'imprimer bonjour monde s'il te plaît merci"

**État initial M₀** (idéationnelle, interpersonnelle, textuelle, champ, tenor, mode) :
- idéat : +0.1 (action simple : demande)
- interp : +0.8 (politesse forte : s'il te plaît, merci)
- text : +0.2 (thème marqué : tu)
- champ : +0.3 (technique/informatique)
- tenor : +0.6 (asymétrique : demandeur → exécuteur)
- mode : +0.4 (semi-formel, écrit planifié)

**État final Mₜ₌₁** (après traitement) :
- idéat : +0.2 (action confirmer)
- interp : +0.9 (pic politesse)
- text : +0.3 (thème confirmé)
- champ : +0.3 (stable)
- tenor : +0.6 (stable)
- mode : +0.4 (stable)

**Réalisation** : le vecteur (0.2, 0.9, 0.3, 0.3, 0.6, 0.4) sélectionne **merci** (distance SFL minimale au vocabulaire).

## Démarrage Rapide

```bash
pip install -r requirements.txt
python app.py  # lance l'API FastAPI sur :8000
curl -X POST http://localhost:8000/pipeline \
  -H "Content-Type: application/json" \
  -d '{"prompt": "Salut peux-tu m\'imprimer bonjour monde s\'il te plaît merci", "lang": "FR"}'
```

Réponse :
```json
{
  "lang": "FR",
  "trajectory": [
    {"t": 0, "state": [0.1, 0.8, 0.2, 0.3, 0.6, 0.4], "label": "Salut"},
    {"t": 1, "state": [0.2, 0.9, 0.3, 0.3, 0.6, 0.4], "delta": 0.18, "phi": "interpersonal"}
  ],
  "realization": {"best": "merci", "candidates": [["merci", 0.18], ["s'il te plaît", 0.42]]}
}
```

## Carte du Référentiel

| Fichier | Rôle |
|---------|------|
| MANIFOLD.md | Théorie formelle en LaTeX : manifold continu, distances SFL, deltas |
| sfl_manifold.py | Moteur géométrique : Δt, κ, φ, L_sp |
| sfl_adapter.py | Projection W_adapt : ℝᵈ → ℝ⁶ configurable |
| sfl_realize.py | Réalisation lexique : voisinage pondéré |
| sfl_visualise.py | Plots 3D, barres, animations MP4 |
| app.py | Wrapper FastAPI : stateless, endpoints /analyze /pipeline /realize |

## Dimensions du Manifold (6D)

| Dimension | Plage | Signification LSF |
|-----------|-------|-------------------|
| idéationnelle | [-1, +1] | type de processus (matériel/mental/relationnel) et richesse participante |
| interpersonnelle | [-1, +1] | modalité, appréciation, solidarité |
| textuelle | [-1, +1] | structure thème-rhème, information donnée/nouvelle, cohésion |
| champ | [-1, +1] | domaine technicité (abstrait ↔ concret, spécialisé ↔ commun) |
| tenor | [-1, +1] | distance sociale (égalitaire ↔ hiérarchique) et solidarité |
| mode | [-1, +1] | oralité (spontané ↔ planifié), monologue ↔ dialogue |

## Formalisme : Trajectoires et Deltas

Une **trajectoire sémantique** est une séquence d'états :
$$\mathbf{T} = (\mathbf{M}_0, \mathbf{M}_1, \ldots, \mathbf{M}_T)$$

où chaque $\mathbf{M}_t \in \mathbb{R}^6$.

Un **delta** $\Delta_t = \mathbf{M}_t - \mathbf{M}_{t-1}$ encode la **transformation de sens** d'un instant au suivant.

La **distance SFL** (pondérée par l'importance systémique) :
$$d_{\text{SFL}}(\mathbf{M}, \mathbf{M}') = \sqrt{\sum_i w_i (M_i - M'_i)^2}$$

où les poids $w_i$ reflètent l'importance de chaque métafonction/variable contexuelle.

## État du Projet

| Composant | Statut | Notes |
|-----------|--------|-------|
| Théorie SFL | ✓ formalisée | Halliday, Martin, grounded |
| Adapter | ✓ codé | configurable ndim |
| Manifold | ✓ géométrie | Δt, κ, φ, L_sp |
| Visualisation | ✓ plots 3D + MP4 | matplotlib, Plotly |
| Réalisation | ✓ lexique pilot | 15 mots EN/ES, 8 FR |
| API | ✓ FastAPI | stateless, 4 endpoints |
| Multilingue | ✓ EN/ES/FR | analyses natives, pas traductions |

## Grondage Théorique

- **Halliday & Matthiessen** (2014) : *Halliday's Introduction to Functional Grammar*. La stratification (contexte réalise sémantique réalise lexicogramaire) fonde notre manifold.
- **Martin & White** (2005) : *The Language of Evaluation*. Les dimensions interpersonnelles (appréciation, jugement, affect) structurent notre axe interpersonnel.
- **Van Leeuwen** (2005) : *Introducing Social Semiotics*. Les ressources sémiotiques ont potentiel de sens et affordances—exactement ce que notre manifold continu modélise.

## Politique Linguistique

- Chaque langue (EN, ES, FR) a sa propre analyse et réalisation
- Pas de traductions automatiques entre répertoires linguistiques
- Chaque manifold 6D est interprété dans les catégories LSF de la langue cible
- Les concepts théoriques (métafonctions, deltas, distances) sont **langage-agnostiques**

## Prochaines Étapes

1. **Adapter multi-langue** : entraîner W_adapt pour chaque (langue × domaine)
2. **Corpus SFL annoté** : Bank of English + LSF parses pour calibrer distances w_i
3. **Délicatesse accrue** : subdiviser chaque dimension
4. **Couplage métafonctionnel** : modéliser l'interdépendance
5. **Évaluation** : préservation fonctionnelle vs perplexité

---

**Repo** : https://github.com/simon-drury/sfl-meaning-matrix-llm