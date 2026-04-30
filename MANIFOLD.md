# MANIFOLD.md
# SFL Meaning Matrix: Formal Specification

> Language as social semiotic (Halliday, 1978)

This document is the mathematical ground truth for the architecture.
All module implementations are derived from the definitions here.

---

## 1. The semiotic manifold M

Let M be a smooth Riemannian manifold of dimension n = 6,
parameterised by the six SFL metafunctions and register variables:

    M = [-1, 1]^6

with coordinates:

    x = (x_1, x_2, x_3, x_4, x_5, x_6)
      = (ideational, field, interpersonal, tenor, textual, mode)

A **meaning state** M_t is a point in M.
A **meaning trajectory** T is an ordered sequence M_0, M_1, ..., M_T.

**Note on SFL mapping.**
In Halliday's canonical tripartite model, the three metafunctions are
ideational, interpersonal, and textual, with register variables field,
tenor, and mode mapping onto them respectively.
This architecture treats all six as independent dimensions of M,
allowing finer-grained geometric discrimination.
The canonical mapping (field -> ideational, tenor -> interpersonal,
mode -> textual) is preserved as a constraint on the pilot encoders
but relaxed at the manifold level.

---

## 2. Semiotic units

A **semiotic unit** (SFL: Halliday 1985; Martin 1992) is the minimal
unit of meaning-making. In this architecture, each semiotic unit u_t
is assigned a meaning state M_t in M.

The process of moving from semiotic potential to instance is
**instantiation** (SFL canonical term). In the pilot, instantiation
is approximated by the hand-encoded encoder functions.
In production, instantiation will be learned from SFL-annotated corpora.

---

## 3. Displacement and geodesic energy

At each step t, the displacement vector is:

    delta_t = M_t - M_{t-1}       in R^6

The displacement magnitude is:

    ||delta_t|| = sqrt( sum_i (delta_t_i)^2 )

The **arc length** of the trajectory is:

    L(gamma) = sum_{t=1}^{T} ||delta_t||

The **geodesic energy** (energy functional on path space) is:

    E(gamma) = sum_{t=1}^{T} [ lambda_1 * ||delta_t||^2
                              + lambda_2 * kappa_t^2 ]

where lambda_1, lambda_2 > 0 are weighting parameters.

This is the discrete analogue of the continuous energy functional:

    E(gamma) = integral_0^T g(gamma'(t), gamma'(t)) dt

where g is the Riemannian metric on M. In the pilot, g is the
standard Euclidean metric on [-1,1]^6. In production, g may be
replaced by the Fisher-Rao metric (Rao 1945; Amari 1985) derived
from the statistical manifold of meaning distributions.

**Geodesic paths** (paths of minimal energy) correspond to coherent,
low-curvature meaning development. High E(gamma) signals semantic
turbulence: register shifts, evaluative moves, field changes.

---

## 4. Curvature

The local curvature at step t is:

    kappa_t = arccos( <delta_{t-1}, delta_t> /
                      (||delta_{t-1}|| * ||delta_t||) )

kappa_t in [0, pi] radians.
kappa_t = 0: trajectory continues in the same direction (coherent).
kappa_t = pi: full reversal (semantic contradiction or register shift).

A sharp kappa peak is a **semantic event**: a point where the
trajectory changes direction significantly. These are interpretively
significant -- register shifts, topic changes, evaluative moves.

---

## 5. Dominant driver

The **dominant driver** phi_t at step t is the dimension that
contributes most to the displacement:

    phi_t = argmax_i |delta_t_i|

This identifies *which* metafunction or register variable drove
the meaning move at each step.

---

## 6. Momentum

The momentum vector v_t tracks the running direction of the trajectory
with exponential decay:

    v_t = alpha * delta_t + (1 - alpha) * v_{t-1}

alpha in [0, 1] controls the decay rate (pilot: alpha = 0.7).

---

## 7. The adapter projection

The adapter layer W_adapt projects from the manifold M into the
transformer's model dimension d_model:

    W_adapt: R^6 -> R^{d_model}

specifically:

    h_0 = W_adapt * vec(M_t) + b_adapt

where vec(M_t) in R^6 is the flattened meaning state.
This h_0 replaces the standard token embedding as the first
hidden state passed to the transformer.

---

## 8. Lexical realization

Given a meaning state M_out in M and a vocabulary space V_L
for language L, the **realization** w* is:

    w* = argmin_{w in V_L} || f_w - M_out ||_2

where f_w in R^6 is the semiotic fingerprint of lexical item w.

In production, distances may be computed under the Fisher-Rao metric
rather than the Euclidean metric, giving:

    w* = argmin_{w in V_L} d_FR(f_w, M_out)

The same M_out presented to V_EN and V_ES independently yields
two co-equal realizations with no translation step.

---

## 9. M0 as reference state

M_0 is not required to be derived from the first token of the input.
It may be a **reference meaning state** -- a pre-loaded context
encoding the domain vocabulary, interaction tenor, and channel mode
of the current process. This reference state is carried as structured
metadata across processes.

Session memory is then the cumulative delta from the reference state:

    Delta_session(t) = M_t - M_0

This is lightweight, inspectable, and portable. It does not require
persistent neural memory or fine-tuning.

---

## References

- Amari, S. (1985). *Differential-Geometrical Methods in Statistics*. Springer.
- Halliday, M.A.K. (1985). *An Introduction to Functional Grammar*. Arnold.
- Halliday, M.A.K. & Matthiessen, C. (2014). *Halliday's Introduction to
  Functional Grammar* (4th ed.). Routledge.
- Martin, J.R. (1992). *English Text: System and Structure*. Benjamins.
- Rao, C.R. (1945). Information and the accuracy attainable in the
  estimation of statistical parameters. *Bulletin of the Calcutta
  Mathematical Society*, 37, 81-91.
