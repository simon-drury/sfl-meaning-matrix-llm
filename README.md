# SFL Meaning Matrix Architecture (LASSM)

> **Language As Social Semiotic Model (LASSM)**  
> Continuous neural language modeling grounded in Systemic Functional Linguistics and semiotic manifold geometry.

[![Train and Generate 3x3 LASSM](https://github.com/simon-drury/sfl-meaning-matrix-llm/actions/workflows/train.yml/badge.svg)](https://github.com/simon-drury/sfl-meaning-matrix-llm/actions/workflows/train.yml)
[![License: CC BY-NC 4.0](https://img.shields.io/badge/License-CC%20BY--NC%204.0-lightgrey.svg)](https://creativecommons.org/licenses/by-nc/4.0/)

---

## System Architecture

The Language As Social Semiotic Model (LASSM) implements a Form $\to$ Meaning $\to$ Form pipeline operating over a continuous coordinate manifold (Halliday, 1978).

1. **Continuous Meaning Representation**: Input sequences map into continuous state matrices $M_t \in [-1.0, 1.0]^{3 \times 3}$, evaluating Ideational, Interpersonal, and Textual metafunctional strata across Field, Tenor, and Mode situational register dimensions.
2. **Trajectory Mechanics**: Discourse progression follows continuous state transitions $M_t = \operatorname{clip}(M_{t-1} + \Delta_t, -1.0, 1.0)$ constrained by path displacement and curvature loss.
3. **Boundary Realization**: The output semiotic state $\hat{\mathbf{m}}_{\text{out}}$ selects surface lexical items via Euclidean distance minimization against empirical 9D coordinate centroids: $w^* = \arg\min_{w \in \mathcal{V}} \|\hat{\mathbf{m}}_{\text{out}} - \mathbf{f}_w\|_2$.

---

## Mathematical Specification

### 1. State Matrix $M_t$

The semantic state matrix $M_t \in \mathbb{R}^{3 \times 3}$ is defined as:

$$
M_t = \begin{bmatrix}
m_{\text{id, field}} & m_{\text{id, tenor}} & m_{\text{id, mode}} \\
m_{\text{int, field}} & m_{\text{int, tenor}} & m_{\text{int, mode}} \\
m_{\text{txt, field}} & m_{\text{txt, tenor}} & m_{\text{txt, mode}}
\end{bmatrix}_t \in [-1.0, 1.0]^{3 \times 3}
$$

- **Rows (Metafunctional Strata)**:
  - **Ideational**: Experiential processes, participant roles, and logical relations.
  - **Interpersonal**: Speech act posture, social distance, and modality.
  - **Textual**: Information structure, Theme–Rheme organization, and cohesion.
- **Columns (Situational Register Dimensions)**:
  - **Field**: Institutional setting and domain of activity.
  - **Tenor**: Agent status, power asymmetry, and formality.
  - **Mode**: Medium channel and rhetorical distance.

Unrolling $M_t$ yields a continuous 9-dimensional state coordinate vector:

$$
\mathbf{m}_t = \operatorname{vec}(M_t) \in [-1.0, 1.0]^9
$$

### 2. Dual Covariance Operators

- **Metafunctional Covariance**:
  $$\Sigma_{\text{meta}} = M_t M_t^T \in \mathbb{R}^{3 \times 3}$$
  Measures load distribution across Ideational, Interpersonal, and Textual strata.
- **Register Covariance**:
  $$\Sigma_{\text{register}} = M_t^T M_t \in \mathbb{R}^{3 \times 3}$$
  Measures contextual variance across Field, Tenor, and Mode dimensions.

### 3. Optimization Objective

The feedforward core (`SFLMeaningTransformer`) optimizes a joint objective:

$$\mathcal{L}_{\text{total}} = \mathcal{L}_{\text{SFL}} + \lambda_{\text{sp}} \mathcal{L}_{\text{sp}}$$

Where:
- Coordinate Mean Squared Error:
  $$\mathcal{L}_{\text{SFL}} = \frac{1}{9} \sum_{i=1}^9 (\hat{\mathbf{m}}_{\text{out}, i} - \mathbf{m}_{\text{target}, i})^2$$
- Trajectory path smoothness:
  $$\mathcal{L}_{\text{sp}} = \sum_{t=2}^T \|\Delta_t\|_2^2 + \kappa_t$$

---

## Repository Implementation

- **`traincore.py`**: Standalone training pipeline implementing the 2.37M-parameter `SFLMeaningTransformer` and linear adapter $W_{\text{adapt}} \in \mathbb{R}^{d_{\text{model}} \times 9}$.
- **`download_and_ingest_treebank.py`**: Automated pipeline parsing syntactic dependency relations (Universal Dependencies EWT) into continuous 9D trajectories.
- **`sfl_model_3x3.pt`**: Neural model checkpoint trained over empirical treebank trajectories.
- **`data/empirical_vocabulary_9d.json`**: 32,580 lexical items mapped to empirical 9D coordinate centroids.
- **`data/empirical_trajectories.jsonl`**: 500 parsed continuous sentence trajectories.
- **`.github/workflows/train.yml`**: Automated GitHub Actions CI workflow executing data ingestion, 10-epoch training, and validation.

---

## Citation & Attribution

```bibtex
@software{drury2026lassm,
  author = {Drury, Simon},
  title = {Language As Social Semiotic Model (LASSM): Continuous Semiotic Manifold Trajectories in Language Modeling},
  year = {2026},
  url = {https://github.com/simon-drury/sfl-meaning-matrix-llm}
}
```

---

|<[sjd_datascapes]>| · https://github.com/simon-drury/sfl-meaning-matrix-llm
