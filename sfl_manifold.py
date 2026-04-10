#!/usr/bin/env python3
"""
sfl_manifold.py
Semiotic Path Geometry Engine.

For each step in a MeaningTrajectory, computes:

  ||delta_t||   displacement magnitude  -- how far the meaning moved
  kappa_t       local curvature         -- whether the path turned
  v_t           momentum vector         -- which direction it is heading
  L_sp          semiotic path loss      -- total geometric coherence
  phi_t         dominant driver         -- which metafunctional dimension
                                           drove the move (the why)

Reference: MANIFOLD.md, sections 3 and 5.
"""

import numpy as np
from dataclasses import dataclass, field
from typing import List

DIM_NAMES = ["ideational", "field", "interpersonal", "tenor", "textual", "mode"]


@dataclass
class StepGeometry:
    t: int
    label: str
    displacement: float        # ||delta_t||
    curvature: float           # kappa_t in radians (nan for first step)
    momentum: np.ndarray       # v_t, shape (6,)
    dominant_driver: str       # phi_t: name of dominant dimension
    dominant_index: int        # phi_t: index of dominant dimension
    delta_vector: np.ndarray   # raw displacement vector, shape (6,)


@dataclass
class ManifoldAnalysis:
    lang: str
    steps: List[StepGeometry]
    path_loss: float           # L_sp
    lambda1: float
    lambda2: float


def compute_manifold(trajectory,
                     lambda1: float = 0.5,
                     lambda2: float = 0.5,
                     alpha: float = 0.7) -> ManifoldAnalysis:
    """
    Compute full path geometry for a MeaningTrajectory.

    Parameters
    ----------
    trajectory : MeaningTrajectory
    lambda1    : weight on displacement term in L_sp
    lambda2    : weight on curvature term in L_sp
    alpha      : momentum decay factor in [0, 1]

    Returns
    -------
    ManifoldAnalysis
    """
    states = [s.to_vector() for s in trajectory.states]
    deltas = [states[t] - states[t - 1] for t in range(1, len(states))]

    steps = []
    momentum = np.zeros(6)
    path_loss = 0.0

    for i, delta in enumerate(deltas):
        t = i + 1
        disp = float(np.linalg.norm(delta))

        if i > 0:
            prev = deltas[i - 1]
            denom = np.linalg.norm(prev) * np.linalg.norm(delta) + 1e-9
            cos_angle = np.dot(prev, delta) / denom
            kappa = float(np.arccos(np.clip(cos_angle, -1.0, 1.0)))
        else:
            kappa = float("nan")

        momentum = alpha * delta + (1 - alpha) * momentum

        dom_idx = int(np.argmax(np.abs(delta)))
        dom_name = DIM_NAMES[dom_idx]

        kappa_term = 0.0 if np.isnan(kappa) else kappa ** 2
        path_loss += lambda1 * disp ** 2 + lambda2 * kappa_term

        steps.append(StepGeometry(
            t=t,
            label=trajectory.states[t].label,
            displacement=disp,
            curvature=kappa,
            momentum=momentum.copy(),
            dominant_driver=dom_name,
            dominant_index=dom_idx,
            delta_vector=delta.copy(),
        ))

    return ManifoldAnalysis(
        lang=trajectory.lang,
        steps=steps,
        path_loss=path_loss,
        lambda1=lambda1,
        lambda2=lambda2,
    )


def print_manifold(analysis: ManifoldAnalysis):
    print("\n=== Semiotic Manifold Analysis [" + analysis.lang + "] ===\n")
    header = ("t".ljust(3) + " " + "label".ljust(34) +
              "||d||".rjust(7) + "  kappa(r)".rjust(10) +
              "  phi (driver)".ljust(18) + "  momentum dir")
    print(header)
    print("-" * 90)
    for s in analysis.steps:
        kap = f"{s.curvature:.3f}" if not np.isnan(s.curvature) else "   -  "
        mom_dir = DIM_NAMES[int(np.argmax(np.abs(s.momentum)))]
        print(
            str(s.t).ljust(3) + " " +
            s.label[:33].ljust(34) +
            f"{s.displacement:>7.3f}" +
            f"{kap:>10}" +
            ("  " + s.dominant_driver).ljust(20) +
            "  " + mom_dir
        )
    print(
        "\n  Semiotic Path Loss L_sp"
        " (lambda1=" + str(analysis.lambda1) +
        ", lambda2=" + str(analysis.lambda2) + "): " +
        f"{analysis.path_loss:.4f}"
    )


if __name__ == "__main__":
    from sfl_matrix_engine import encode_en, encode_es

    for fn in [encode_en, encode_es]:
        traj = fn()
        analysis = compute_manifold(traj)
        print_manifold(analysis)
        print("=" * 90)
