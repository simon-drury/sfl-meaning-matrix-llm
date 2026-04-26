#!/usr/bin/env python3
"""
sfl_matrix_engine.py
SFL Meaning-Matrix Engine — pilot implementation.

Primary representational architecture (three co-equal forms):

  FORM 1 — 3x2 matrix (primary, original design — sjd April 2026)
  Rows = metafunctions. Columns = left: metafunction, right: register variable.
  Adjacency (left→right) implies shared operational ground, NOT fixed coupling.

    [ ideational    field  ]
    [ interpersonal tenor  ]
    [ textual       mode   ]

  M^T M  → 2x2 covariance over register variables (field, tenor, mode)
  M M^T  → 3x3 covariance over metafunctions (ideational, interpersonal, textual)
  Eigenvectors of each reveal principal axes of semantic variation.

  FORM 2 — 2x3 matrix (transposed alternative)
  Rows = [metafunctions top / register variables bottom].
  Columns pair each metafunction with its register variable vertically.

    [ ideational  interpersonal  textual ]
    [ field        tenor          mode   ]

  M^T M  → 3x3 covariance over metafunctions
  M M^T  → 2x2 covariance over register variables
  NOT equivalent to Form 1 in operation despite holding identical values.

  FORM 3 — 6D flat vector (NLP-compatible compression)
  [ideational, field, interpersonal, tenor, textual, mode]
  Produced by to_vector(). Discards all structural relationships.
  Retained for compatibility with PyTorch, FAISS, and adapter layers.
  NOTE: This is a bastardised compression by the flat-vector convention
  of mainstream NLP pipelines. The primary forms are 3x2 and 2x3.
  — sjd / sonar, April 2026

Encodes prompts as sequences of meaning matrices and deltas.
No lexical items are stored after projection.
"""

import numpy as np
from dataclasses import dataclass, field
from typing import List

DIMENSIONS = ["ideational", "field", "interpersonal", "tenor", "textual", "mode"]


@dataclass
class MeaningMatrix:
    """
    3x2 meaning matrix — FORM 1 (primary representation).

    Layout:
      [ ideational    field  ]
      [ interpersonal tenor  ]
      [ textual       mode   ]

    Left column: metafunctions (what the meaning does).
    Right column: register variables (situational context).
    Adjacency left→right implies shared operational ground, NOT fixed pairing.
    Values: float in [-1.0, 1.0]

    See also:
      to_matrix_2x3() — FORM 2: transposed 2x3 representation
      to_vector()     — FORM 3: 6D flat vector (NLP compression only)
    """
    values: np.ndarray  # shape (3, 2)
    label: str = ""

    @classmethod
    def from_values(cls, ideational, field, interpersonal, tenor, textual, mode, label=""):
        v = np.array([[ideational, field],
                      [interpersonal, tenor],
                      [textual, mode]], dtype=float)
        return cls(values=v, label=label)

    def to_matrix_2x3(self) -> np.ndarray:
        """
        FORM 2 — 2x3 transposed representation.

        Layout:
          [ ideational  interpersonal  textual ]
          [ field        tenor          mode   ]

        Top row: all three metafunctions.
        Bottom row: all three register variables.
        Each column pairs a metafunction with its register variable vertically.

        NOT operationally equivalent to the 3x2 form:
          M^T M here → 3x3 over metafunctions
          M M^T here → 2x2 over register variables
        (Reversed from the 3x2 form.)
        """
        return self.values.T  # shape (2, 3)

    def to_vector(self) -> np.ndarray:
        """
        FORM 3 — 6D flat vector: [ideational, field, interpersonal, tenor, textual, mode]

        NLP-compatible compression only. Discards all structural relationships
        between the six values. Retained for compatibility with PyTorch, FAISS,
        and downstream adapter layers that require a 1D array.

        NOTE: This is a bastardised compression by the flat-vector convention
        of mainstream NLP pipelines. The primary representational forms are
        3x2 (Form 1) and 2x3 (Form 2). Use those for any operation that
        depends on the structural relationship between metafunctions and
        register variables. — sjd / sonar, April 2026
        """
        return self.values.flatten()

    def __add__(self, delta):
        combined = np.clip(self.values + delta.values, -1.0, 1.0)
        return MeaningMatrix(values=combined, label=self.label)

    def display(self):
        r = self.values
        lines = [
            "MeaningMatrix(" + self.label + ")",
            "  [ ideational: "   + f"{r[0,0]:+.2f}" + "  field: "  + f"{r[0,1]:+.2f}" + " ]",
            "  [ interpersonal: " + f"{r[1,0]:+.2f}" + "  tenor: " + f"{r[1,1]:+.2f}" + " ]",
            "  [ textual: "      + f"{r[2,0]:+.2f}" + "  mode: "  + f"{r[2,1]:+.2f}" + " ]",
        ]
        return "\n".join(lines)

    def display_2x3(self):
        """Display the 2x3 transposed form for inspection."""
        t = self.to_matrix_2x3()
        lines = [
            "MeaningMatrix 2x3 (" + self.label + ")",
            "  [ ideational: "  + f"{t[0,0]:+.2f}" + "  interpersonal: " + f"{t[0,1]:+.2f}" + "  textual: " + f"{t[0,2]:+.2f}" + " ]",
            "  [ field: "       + f"{t[1,0]:+.2f}" + "  tenor: "         + f"{t[1,1]:+.2f}" + "  mode: "    + f"{t[1,2]:+.2f}" + " ]",
        ]
        return "\n".join(lines)


@dataclass
class MeaningTrajectory:
    """
    Sequence of meaning states for a prompt.
    Stores M0 (full) + list of deltas.
    No lexical items retained after encoding.
    """
    lang: str
    M0: MeaningMatrix
    deltas: List[MeaningMatrix] = field(default_factory=list)

    def __post_init__(self):
        self._states = [self.M0]

    def add_delta(self, delta: MeaningMatrix):
        self.deltas.append(delta)
        new_state = self._states[-1] + delta
        new_state.label = delta.label
        self._states.append(new_state)

    @property
    def states(self) -> List[MeaningMatrix]:
        """Public accessor for the ordered list of meaning states M0..MT."""
        return self._states

    @property
    def final_state(self):
        return self._states[-1]

    def print_trajectory(self):
        print("\n=== Trajectory [" + self.lang + "] ===")
        for i, s in enumerate(self._states):
            tag = "M0" if i == 0 else "M" + str(i) + " (after delta" + str(i) + ")"
            print("\n  " + tag + ":")
            print("  " + s.display())
            print("  " + s.display_2x3())


# ---------------------------------------------------------------------------
# EN iconic prompt encoder
# ---------------------------------------------------------------------------
def encode_en() -> MeaningTrajectory:
    """hey why dont you print hello world for me please thank you"""
    traj = MeaningTrajectory(lang="EN", M0=MeaningMatrix.from_values(
        -0.7, -0.5, +0.8, +0.9, +0.6, -0.6, label="hey"))
    traj.add_delta(MeaningMatrix.from_values(+0.1, +0.2, +0.1,  0.0, +0.2,  0.0, label="why dont you"))
    traj.add_delta(MeaningMatrix.from_values(+0.9, +0.9, +0.1, -0.1, +0.3,  0.0, label="print hello world"))
    traj.add_delta(MeaningMatrix.from_values(+0.1,  0.0, -0.1, +0.1, +0.1,  0.0, label="for me"))
    traj.add_delta(MeaningMatrix.from_values(-0.3,  0.0, +0.1, +0.2, -0.2,  0.0, label="please thank you"))
    return traj


# ---------------------------------------------------------------------------
# ES iconic prompt encoder
# ---------------------------------------------------------------------------
def encode_es() -> MeaningTrajectory:
    """buenos dias, hoy es viernes. Esto es CNN. Hoy es un dia importante para mi y para muchos."""
    traj = MeaningTrajectory(lang="ES", M0=MeaningMatrix.from_values(
        -0.6, -0.3, +0.8, +0.7, +0.7, +0.4, label="buenos dias"))
    traj.add_delta(MeaningMatrix.from_values(+0.4, +0.2,  0.0,  0.0, +0.2,  0.0, label="hoy es viernes"))
    traj.add_delta(MeaningMatrix.from_values(+0.5, +0.8, +0.2, -0.3, +0.1, +0.3, label="Esto es CNN"))
    traj.add_delta(MeaningMatrix.from_values(+0.2, -0.1, -0.1, +0.3, +0.1, -0.1, label="dia importante para mi"))
    traj.add_delta(MeaningMatrix.from_values(+0.2, +0.1, +0.1, +0.2,  0.0,  0.0, label="y para muchos"))
    return traj


# ---------------------------------------------------------------------------
# Realization stub
# ---------------------------------------------------------------------------
def realize(traj: MeaningTrajectory) -> str:
    m = traj.final_state.values
    field_v = m[0, 1]
    mode = m[2, 1]
    if traj.lang == "EN" and field_v > 0.5 and mode < 0:
        return "Hello, World!"
    if traj.lang == "ES" and field_v > 0.7 and mode > 0.5:
        return "Buenos dias. Hoy es un dia importante para todos. Seguimos en CNN."
    return "[realization: no candidate matched]"


# ---------------------------------------------------------------------------
# Run
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    for encode_fn in [encode_en, encode_es]:
        t = encode_fn()
        t.print_trajectory()
        print("\n  Final state (3x2):")
        print("  " + t.final_state.display())
        print("\n  Final state (2x3):")
        print("  " + t.final_state.display_2x3())
        print("\n  Final state (6D vector — NLP compression):")
        print("  " + str(t.final_state.to_vector()))
        print("\n  Realization [" + t.lang + "]: " + realize(t))
        print()
