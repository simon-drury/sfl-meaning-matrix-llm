# Modèle Sémiotique Social (LASSM) — FR

**Language As Social Semiotic Model (LASSM)** : modélisation neuronale continue du langage, fondée sur la Linguistique Systémique Fonctionnelle de Halliday, opérant sur des matrices d’état sémiotique 3×3 et des trajectoires continues en 9 dimensions.

## Principes Fondamentaux

La linguistique systémique fonctionnelle (LSF) pose que la signification réside dans la **fonction en contexte**, pas dans la structure. LASSM applique ce principe au calcul :

- **Métafonctions (lignes)** : idéationnelle (construire l’expérience), interpersonnelle (enacter les relations), textuelle (organiser le texte)
- **Variables de registre (colonnes)** : champ (domaine d’activité), tenor (distance sociale, pouvoir), mode (canal, médium)
- **Matrice d’état** : chaque instant sémiotique $M_t \in [-1, 1]^{3 \times 3}$ capture la position dans le manifold
- **Trajectoire** : les deltas $\Delta_t$ encodent la transformation de sens d’un instant au suivant

## Pipeline : Forme → Sens → Forme

```
entrée (surface linguistique)
    ↓
projection M₀ (adapter SFL)
    ↓
traitement (SFLMeaningTransformer, trajectoire 9D)
    ↓
réalisation (k-NN dans vocabulaire empirique 9D)
    ↓
sortie (surface linguistique)
```

Le réseau de neurones est un **calculateur de trajectoire**. La théorie est SFL.

## La Matrice d’État $M_t$

$$
M_t = \begin{bmatrix}
m_{\text{id, champ}} & m_{\text{id, tenor}} & m_{\text{id, mode}} \\
m_{\text{int, champ}} & m_{\text{int, tenor}} & m_{\text{int, mode}} \\
m_{\text{txt, champ}} & m_{\text{txt, tenor}} & m_{\text{txt, mode}}
\end{bmatrix}_t \in [-1.0, 1.0]^{3 \times 3}
$$

Déroulée : vecteur 9D $\mathbf{m}_t = \operatorname{vec}(M_t) \in [-1.0, 1.0]^9$.

## Dimensions du Manifold (9D)

| Dimension | Plage | Signification LSF |
|-----------|-------|-------------------|
| idéationnelle × champ | [-1, +1] | type de processus dans le domaine d’activité |
| idéationnelle × tenor | [-1, +1] | charge expérientielle selon le rôle social |
| idéationnelle × mode | [-1, +1] | structuration de l’expérience selon le canal |
| interpersonnelle × champ | [-1, +1] | modalité et appréciation dans le domaine |
| interpersonnelle × tenor | [-1, +1] | distance sociale, solidarité, hiérarchie |
| interpersonnelle × mode | [-1, +1] | posture interactionnelle selon le médium |
| textuelle × champ | [-1, +1] | organisation de l’information dans le domaine |
| textuelle × tenor | [-1, +1] | cohésion et thème selon les rôles sociaux |
| textuelle × mode | [-1, +1] | structure thème–rhème, oralité vs planification |

## Démarrage Rapide

```bash
pip install -r requirements.txt
python app.py  # lance l’API FastAPI sur :8000
curl -X POST http://localhost:8000/pipeline \
  -H "Content-Type: application/json" \
  -d '{"prompt": "Salut peux-tu m\'imprimer bonjour monde s\'il te plaît merci", "lang": "FR"}'
```

## Carte du Référentiel

| Fichier | Rôle |
|---------|------|
| `traincore.py` | Pipeline d’entraînement, SFLMeaningTransformer 2,37M paramètres |
| `sfl_matrix_engine_v3.py` | Moteur matriciel 3×3, opérateurs de covariance |
| `sfl_realize.py` | Réalisation lexicale : k-NN dans vocabulaire 9D empirique |
| `sfl_manifold.py` | Géométrie riemannienne : Δt, κ, énergie géodésique |
| `sfl_visualise.py` | Plots 3D, barres, animations |
| `api.py` | API FastAPI : endpoints /analyze /pipeline /realize |
| `data/empirical_vocabulary_9d.json` | 32 580 items lexicaux, centroïdes 9D empiriques |
| `data/empirical_trajectories.jsonl` | 500 trajectoires continues parsées |

## Grondage Théorique

- **Halliday & Matthiessen** (2014) : *Halliday’s Introduction to Functional Grammar*. La stratification fonde notre manifold.
- **Martin & White** (2005) : *The Language of Evaluation*. Dimensions interpersonnelles.
- **Van Leeuwen** (2005) : *Introducing Social Semiotics*. Potentiel de sens et affordances.

---

**Repo** : https://github.com/simon-drury/sfl-meaning-matrix-llm
