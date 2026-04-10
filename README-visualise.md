# sfl_visualise.py — Semiotic Manifold Visualisation

## Purpose

Produces visual representations of the meaning trajectories computed by
`sfl_manifold.py`, using the two iconic prompts as pilot data.

---

## Requirements

```bash
pip install matplotlib numpy
# For MP4 animation export:
brew install ffmpeg       # macOS
sudo apt install ffmpeg   # Linux/WSL
# Windows: download from https://ffmpeg.org
```

---

## Usage

```bash
python sfl_visualise.py            # all four outputs
python sfl_visualise.py --no-anim  # skip MP4/GIF
```

---

## Four outputs

| File | What it shows |
|---|---|
| `output/manifold_3d.png` | Both trajectories as paths through ideational / field / textual space |
| `output/manifold_steps.png` | \(\|\delta_t\|\) per step (bar, coloured by \(\phi_t\)) + \(\kappa_t\) overlay (dotted white) |
| `output/manifold_gaussians.png` | All 6 Gaussian dimension profiles at final meaning state, EN solid / ES dashed |
| `output/manifold_anim.mp4` | Animated EN trajectory — one frame per meaning unit, camera rotates |

---

## Reading the charts

**3D trajectory** — each point is a meaning state \(M_t\). The path connecting them
is the trajectory \(\mathcal{T}\). A straight path = coherent, low-energy meaning development.
A sharp bend = semantic event (register shift, evaluative move, field change).

**Step geometry** — bar height is displacement magnitude \(\|\delta_t\|\).
Bar colour is the dominant metafunctional driver \(\phi_t\) — the *why* of the move.
The dotted white line is curvature \(\kappa_t\): peaks mark semantic events.

**Gaussian profiles** — each of the six SFL dimensions is shown as a probability
distribution centred on its final meaning state value. The spread (\(\sigma = 0.20\))
represents uncertainty — a meaning state is a region, not a point.

---

## Colour key

| Colour | Dimension |
|---|---|
| `#4f98a3` teal | ideational |
| `#da7101` orange | field |
| `#a12c7b` purple | interpersonal |
| `#437a22` green | tenor |
| `#006494` blue | textual |
| `#7a39bb` violet | mode |

---

## Next step

`sfl_realize.py` — de-matrixising: nearest-neighbour retrieval from
\(\mathcal{V}_L\) to produce lexical output in language \(L\).
