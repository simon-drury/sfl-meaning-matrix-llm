# sfl_manifold.py — Semiotic Path Geometry Engine

## Purpose

Takes a `MeaningTrajectory` — the output of `sfl_matrix_engine.py` — and computes
the **geometry of the path** through the semiotic manifold \(\mathcal{M}\).

Vocabulary remains parked. This module operates entirely on meaning states.

---

## Five outputs per trajectory step

| Symbol | Name | Definition | What it tells us |
|---|---|---|---|
| \(\|\delta_t\|\) | Displacement magnitude | \(\|M_t - M_{t-1}\|_2\) | How far the meaning moved in one step |
| \(\kappa_t\) | Local curvature | \(\arccos\!\left(\frac{\delta_t \cdot \delta_{t+1}}{\|\delta_t\|\,\|\delta_{t+1}\|}\right)\) | Whether the path turned — high \(\kappa\) marks a semantic event |
| \(\mathbf{v}_t\) | Momentum vector | \(\alpha\,\delta_t + (1-\alpha)\,\mathbf{v}_{t-1}\) | Which direction the path is heading |
| \(\mathcal{L}_{\text{sp}}\) | Semiotic path loss | \(\sum_t \left(\lambda_1\|\delta_t\|^2 + \lambda_2\,\kappa_t^2\right)\) | Total geometric coherence of the trajectory |
| \(\phi_t\) | Dominant driver | \(\arg\max_i |\delta_t^{(i)}|\) | **Why** the path moved — which metafunctional dimension drove the step |

---

## The dominant driver \(\phi_t\)

Whereas standard transformer attention weights positions in a token sequence,
this architecture identifies the **metafunctional source** of each meaning shift.
At every step, the dimension with the largest absolute displacement is named.

This is not available in token-based architectures. It is a direct consequence
of operating on a semantically labelled manifold rather than a lexical embedding space.

---

## Semiotic Path Loss \(\mathcal{L}_{\text{sp}}\)

\[
\mathcal{L}_{\text{sp}} = \sum_{t=1}^{n}
\left( \lambda_1 \|\delta_t\|^2 + \lambda_2\,\kappa_t^2 \right)
\]

Whereas standard language model training minimises cross-entropy over token predictions,
this architecture minimises **geometric incoherence along a meaning path**.
The loss penalises large displacements and sharp turns — both indicate
a trajectory that is semantically strained.

Backpropagation applies normally: both terms are smooth and differentiable
with respect to the matrix values.

---

## Pilot results — iconic prompts

### EN: `hey why dont you print hello world for me please thank you`

| Step | Unit | \(\|\delta\|\) | \(\kappa\) | \(\phi\) driver |
|---|---|---|---|---|
| 1 | why dont you | 0.316 | — | textual |
| 2 | print hello world | 1.296 | 0.675 | field |
| 3 | for me | 0.173 | 1.254 | ideational |
| 4 | please thank you | 0.387 | 2.034 | ideational |

\(\mathcal{L}_{\text{sp}} = 4.063\)

The large displacement at step 2 reflects the sharp ideational and field
activation as the request becomes concrete. The high curvature at step 4
marks the turn back toward interpersonal work after the instrumental core.

---

### ES: `buenos días — hoy es viernes. Esto es CNN. Hoy es un día importante para mí y para muchos.`

| Paso | Unidad | \(\|\delta\|\) | \(\kappa\) | Driver \(\phi\) |
|---|---|---|---|---|
| 1 | hoy es viernes | 0.490 | — | ideacional |
| 2 | Esto es CNN | 1.058 | 0.748 | campo |
| 3 | día importante para mí | 0.400 | 1.858 | tenor |
| 4 | y para muchos | 0.316 | 0.886 | ideacional |

\(\mathcal{L}_{\text{sp}} = 3.209\)

The large displacement at step 2 reflects institutional field activation.
The high curvature at step 3 marks the turn from institutional authority
to personal voice — the evaluative and affective moment of the prompt.

---

## Scalability note

`compute_manifold()` is a pure function over a `MeaningTrajectory`.
No side effects, no model calls, no I/O.
Horizontally scalable at all three deployment tiers.

---

## Next step

`sfl_adapter.py` — projects the 6-dimensional meaning vector into the
embedding dimension of a local transformer (Llama 3.2 3B / DeepSeek 1.5B)
via a learned linear layer \(W_{\text{adapt}} \in \mathbb{R}^{d_{\text{model}} \times 6}\).
