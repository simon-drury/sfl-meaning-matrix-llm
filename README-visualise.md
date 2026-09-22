# sfl_visualise.py — Trajectory Visualisation

Visualises semiotic meaning-state trajectories in the 9D manifold.

## Run

```bash
python sfl_visualise.py --no-anim    # static PNGs only
python sfl_visualise.py              # + MP4 animation (requires ffmpeg)
python sfl_visualise.py --compete    # competitive mode (Tier 2)
```

Outputs written to `output/`.

## Output files

| File | What it shows |
|------|---------------|
| `output/manifold_3d.png` | EN and ES trajectories as paths through the ideational×tenor×textual subspace |
| `output/manifold_steps.png` | Displacement and curvature per step, coloured by driving dimension |
| `output/manifold_gaussians.png` | Gaussian profiles across the 9 dimensions at final state |
| `output/manifold_anim.mp4` | Animated trajectory, one frame per semiotic unit |

## Notes

- 3D projection uses ideational×field, interpersonal×tenor, textual×mode axes by default
- Curvature spikes (κ) mark semantic events: register shifts, evaluative moves, field changes
- All visualisation operates on the 9D state vector; no information is discarded in projection
