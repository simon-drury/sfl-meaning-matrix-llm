#!/usr/bin/env python3
"""
sfl_visualise.py
Semiotic Manifold Visualisation.

Produces three static charts and one animated MP4
from the two iconic prompt trajectories (EN and ES).

Outputs
-------
  output/manifold_3d.png        -- 3D path through ideational/field/textual
  output/manifold_steps.png     -- displacement ||delta|| and curvature kappa per step
  output/manifold_gaussians.png -- Gaussian profiles for all 6 dimensions, final state
  output/manifold_anim.mp4      -- animated EN trajectory (requires ffmpeg)

Requirements
------------
  pip install matplotlib numpy
  ffmpeg installed on PATH (for MP4 export only)

Usage
-----
  python sfl_visualise.py
  python sfl_visualise.py --no-anim   # skip MP4
"""
import sys
import os
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from mpl_toolkits.mplot3d import Axes3D  # noqa: F401

from sfl_matrix_engine import encode_en, encode_es

OUTDIR = "output"
DIMENSIONS = ["ideational", "field", "interpersonal", "tenor", "textual", "mode"]


def ensure_outdir():
    os.makedirs(OUTDIR, exist_ok=True)


def trajectory_vectors(traj):
    """Return (N, 6) array of flat vectors [ideational, field, interpersonal, tenor, textual, mode]
    for every state M0..MT in the trajectory, and the list of state labels.
    """
    vecs = np.array([s.to_vector() for s in traj.states])
    labels = [s.label if s.label else "M0" for s in traj.states]
    return vecs, labels


def plot_3d(traj_en, traj_es):
    """3D path through ideational/field/textual axes for EN and ES trajectories."""
    vecs_en, _ = trajectory_vectors(traj_en)
    vecs_es, _ = trajectory_vectors(traj_es)

    fig = plt.figure(figsize=(8, 6))
    ax = fig.add_subplot(111, projection='3d')

    ax.plot(vecs_en[:, 0], vecs_en[:, 1], vecs_en[:, 4], marker='o', color='tab:blue', label='EN')
    ax.plot(vecs_es[:, 0], vecs_es[:, 1], vecs_es[:, 4], marker='o', color='tab:red', label='ES')

    ax.set_xlabel('ideational')
    ax.set_ylabel('field')
    ax.set_zlabel('textual')
    ax.set_title('Semiotic manifold path (ideational / field / textual)')
    ax.legend()

    fig.tight_layout()
    fig.savefig(os.path.join(OUTDIR, "manifold_3d.png"), dpi=150)
    plt.close(fig)


def compute_steps(vecs):
    """Per-step displacement ||delta|| and simple discrete curvature kappa.

    kappa at step i approximated as the angle change between consecutive
    displacement vectors (0 if fewer than 2 displacements available).
    """
    deltas = np.diff(vecs, axis=0)
    disp = np.linalg.norm(deltas, axis=1)

    kappa = np.zeros(len(deltas))
    for i in range(1, len(deltas)):
        a, b = deltas[i - 1], deltas[i]
        na, nb = np.linalg.norm(a), np.linalg.norm(b)
        if na > 1e-8 and nb > 1e-8:
            cos_theta = np.clip(np.dot(a, b) / (na * nb), -1.0, 1.0)
            kappa[i] = np.arccos(cos_theta)
    return disp, kappa


def plot_steps(traj_en, traj_es):
    """Displacement ||delta|| and curvature kappa per step, for EN and ES."""
    vecs_en, _ = trajectory_vectors(traj_en)
    vecs_es, _ = trajectory_vectors(traj_es)

    disp_en, kappa_en = compute_steps(vecs_en)
    disp_es, kappa_es = compute_steps(vecs_es)

    fig, axes = plt.subplots(2, 1, figsize=(8, 6), sharex=False)

    axes[0].plot(range(1, len(disp_en) + 1), disp_en, marker='o', color='tab:blue', label='EN')
    axes[0].plot(range(1, len(disp_es) + 1), disp_es, marker='o', color='tab:red', label='ES')
    axes[0].set_ylabel('||delta||')
    axes[0].set_title('Per-step displacement')
    axes[0].legend()

    axes[1].plot(range(1, len(kappa_en) + 1), kappa_en, marker='o', color='tab:blue', label='EN')
    axes[1].plot(range(1, len(kappa_es) + 1), kappa_es, marker='o', color='tab:red', label='ES')
    axes[1].set_ylabel('kappa (rad)')
    axes[1].set_xlabel('step')
    axes[1].set_title('Per-step curvature')
    axes[1].legend()

    fig.tight_layout()
    fig.savefig(os.path.join(OUTDIR, "manifold_steps.png"), dpi=150)
    plt.close(fig)


def gaussian(x, mu, sigma=0.25):
    return np.exp(-0.5 * ((x - mu) / sigma) ** 2) / (sigma * np.sqrt(2 * np.pi))


def plot_gaussians(traj_en, traj_es):
    """Gaussian profile centred on each dimension's final value, EN and ES."""
    final_en = traj_en.final_state.to_vector()
    final_es = traj_es.final_state.to_vector()

    x = np.linspace(-2, 2, 400)

    fig, axes = plt.subplots(2, 3, figsize=(12, 6))
    axes = axes.flatten()

    for i, dim in enumerate(DIMENSIONS):
        axes[i].plot(x, gaussian(x, final_en[i]), color='tab:blue', label='EN')
        axes[i].plot(x, gaussian(x, final_es[i]), color='tab:red', label='ES')
        axes[i].axvline(final_en[i], color='tab:blue', linestyle='--', alpha=0.5)
        axes[i].axvline(final_es[i], color='tab:red', linestyle='--', alpha=0.5)
        axes[i].set_title(dim)
        axes[i].legend(fontsize=8)

    fig.suptitle('Final-state Gaussian profiles per dimension')
    fig.tight_layout()
    fig.savefig(os.path.join(OUTDIR, "manifold_gaussians.png"), dpi=150)
    plt.close(fig)


def animate_en(traj_en):
    """Animated EN trajectory through ideational/field/textual space."""
    vecs, labels = trajectory_vectors(traj_en)

    fig = plt.figure(figsize=(8, 6))
    ax = fig.add_subplot(111, projection='3d')
    ax.set_xlim(vecs[:, 0].min() - 0.2, vecs[:, 0].max() + 0.2)
    ax.set_ylim(vecs[:, 1].min() - 0.2, vecs[:, 1].max() + 0.2)
    ax.set_zlim(vecs[:, 4].min() - 0.2, vecs[:, 4].max() + 0.2)
    ax.set_xlabel('ideational')
    ax.set_ylabel('field')
    ax.set_zlabel('textual')
    ax.set_title('EN semiotic trajectory')

    line, = ax.plot([], [], [], marker='o', color='tab:blue')

    def update(frame):
        line.set_data(vecs[:frame + 1, 0], vecs[:frame + 1, 1])
        line.set_3d_properties(vecs[:frame + 1, 4])
        ax.set_title('EN semiotic trajectory: ' + labels[frame])
        return line,

    anim = animation.FuncAnimation(fig, update, frames=len(vecs), interval=800, blit=False)

    try:
        anim.save(os.path.join(OUTDIR, "manifold_anim.mp4"), writer='ffmpeg', dpi=150)
    except Exception as e:
        print("Could not write MP4 (is ffmpeg installed?): " + str(e))
    plt.close(fig)


def main():
    no_anim = "--no-anim" in sys.argv

    ensure_outdir()

    traj_en = encode_en()
    traj_es = encode_es()

    plot_3d(traj_en, traj_es)
    plot_steps(traj_en, traj_es)
    plot_gaussians(traj_en, traj_es)

    if not no_anim:
        animate_en(traj_en)

    print("Visualisation complete. Outputs written to '" + OUTDIR + "/'.")


if __name__ == "__main__":
    main()
