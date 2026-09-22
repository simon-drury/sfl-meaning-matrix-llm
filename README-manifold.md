# sfl_manifold.py — Semiotic Manifold Geometry

Implements the Riemannian geometry of the continuous semiotic manifold M.

## Quantities

| Symbol | Name | What it measures |
|--------|------|------------------|
| $\Delta_t$ | displacement | how far the meaning state moved at step t |
| $\kappa_t$ | curvature | how sharply the trajectory turned at step t |
| $\phi_t$ | driving dimension | which of the 9 dimensions drove the movement |
| $E(\gamma)$ | geodesic energy | total semantic distance travelled (formally: path energy functional) |

## The state space

Each meaning state is a point in $M \subset [-1,1]^{3 \times 3}$, unrolled to a 9D coordinate vector:

$$\mathbf{m}_t = \operatorname{vec}(M_t) \in [-1.0, 1.0]^9$$

Rows: Ideational, Interpersonal, Textual metafunctions.  
Columns: Field, Tenor, Mode register dimensions.

## Trajectory mechanics

Discourse progression follows continuous state transitions:

$$M_t = \operatorname{clip}(M_{t-1} + \Delta_t, -1.0, 1.0)$$

constrained by geodesic energy and curvature loss.

## Dual covariance operators

- **Metafunctional covariance**: $\Sigma_{\text{meta}} = M_t M_t^T \in \mathbb{R}^{3 \times 3}$ — load distribution across Ideational, Interpersonal, Textual strata
- **Register covariance**: $\Sigma_{\text{register}} = M_t^T M_t \in \mathbb{R}^{3 \times 3}$ — contextual variance across Field, Tenor, Mode

## Run

```bash
python sfl_manifold.py
```

See `MANIFOLD.md` for the full formal specification.
