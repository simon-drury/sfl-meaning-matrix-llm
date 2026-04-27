#!/usr/bin/env python3
"""
sfl_visualise.py
Semiotic Manifold Visualisation.

Produces three static charts and one animated MP4
from the two iconic prompt trajectories (EN and ES).

Outputs
-------
  output/manifold_3d.png          -- 3D path through ideational/field/textual
  output/manifold_steps.png       -- displacement ||delta|| and curvature kappa per step
  output/manifold_gaussians.png   -- Gaussian profiles for all 6 dimensions, final state
  output/manifold_anim.mp4        -- animated EN trajectory (requires ffmpeg)

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

os.makedirs('output', exist_ok=True)

# ── Palette ───────────────────────────────────────────────────────────────────
BG       = '#12121a'
DIM      = ['ideational', 'field', 'interpersonal', 'tenor', 'textual', 'mode']
COLORS   = ['#4f98a3', '#da7101', '#a12c7b', '#437a22', '#006494', '#7a39bb']
EN_COLOR = '#4f98a3'
ES_COLOR = '#da7101'

plt.rcParams.update({
    'text.color': '#cccccc',
    'axes.labelcolor': '#cccccc',
    'xtick.color': '#888888',
    'ytick.color': '#888888',
    'figure.facecolor': BG,
    'axes.facecolor': BG,
    'axes.spines.top': False,
    'axes.spines.right': False,
})

# ── Trajectory data (sourced from sfl_matrix_engine) ─────────────────────────
_en_traj = encode_en()
_es_traj = encode_es()

en_labels = [s.label for s in _en_traj.states]
es_labels = [s.label for s in _es_traj.states]

en_states = np.array([s.to_vector() for s in _en_traj.states])
es_states = np.array([s.to_vector() for s in _es_traj.states])


def compute_geometry(states):
    """Return displacements, magnitudes, curvatures, dominant drivers."""
    d = np.diff(states, axis=0)
    mags = np.linalg.norm(d, axis=1)
    kappas = [np.nan]
    for i in range(1, len(d)):
        cos = np.dot(d[i-1], d[i]) / (
            np.linalg.norm(d[i-1]) * np.linalg.norm(d[i]) + 1e-9)
        kappas.append(float(np.arccos(np.clip(cos, -1.0, 1.0))))
    drivers = [np.argmax(np.abs(d[i])) for i in range(len(d))]
    return d, mags, kappas, drivers


# ── Chart 1: 3D trajectories ──────────────────────────────────────────────────
def plot_3d():
    fig = plt.figure(figsize=(10, 7), facecolor=BG)
    ax = fig.add_subplot(111, projection='3d')
    ax.set_facecolor(BG)

    for states, labels, col, name in [
        (en_states, en_labels, EN_COLOR, 'EN'),
        (es_states, es_labels, ES_COLOR, 'ES'),
    ]:
        xs, ys, zs = states[:, 0], states[:, 1], states[:, 4]
        ax.plot(xs, ys, zs, color=col, linewidth=2.5, alpha=0.9, label=name)
        ax.scatter(xs, ys, zs, color=col, s=55, zorder=5)
        for i, lbl in enumerate(labels):
            ax.text(xs[i], ys[i], zs[i] + 0.06, lbl,
                    fontsize=7, color=col, alpha=0.85)

    ax.set_xlabel('ideational', labelpad=8)
    ax.set_ylabel('field', labelpad=8)
    ax.set_zlabel('textual', labelpad=8)
    ax.set_title(
        'Meaning Trajectories through the Semiotic Manifold\nEN (teal)  ES (orange)',
        color='#dddddd', pad=14)
    ax.legend(loc='upper left', framealpha=0.15, labelcolor='white')

    for pane in [ax.xaxis.pane, ax.yaxis.pane, ax.zaxis.pane]:
        pane.set_facecolor((0.08, 0.08, 0.12, 0.6))
        pane.set_edgecolor('#222222')
    ax.tick_params(colors='#555555')

    plt.tight_layout()
    plt.savefig('output/manifold_3d.png', dpi=150, facecolor=BG)
    plt.close()
    print('  saved: output/manifold_3d.png')


# ── Chart 2: displacement and curvature per step ──────────────────────────────
def plot_steps():
    _, en_mag, en_kap, en_phi = compute_geometry(en_states)
    _, es_mag, es_kap, es_phi = compute_geometry(es_states)

    step_en = [f'EN {i+1}\n{en_labels[i+1][:10]}' for i in range(len(en_mag))]
    step_es = [f'ES {i+1}\n{es_labels[i+1][:10]}' for i in range(len(es_mag))]
    all_steps = step_en + step_es
    all_mags  = list(en_mag) + list(es_mag)
    all_phi   = en_phi + es_phi
    all_kap   = [k if not np.isnan(k) else 0.0 for k in en_kap + es_kap]

    fig, ax = plt.subplots(figsize=(12, 5), facecolor=BG)
    ax.set_facecolor(BG)

    bar_colors = [COLORS[p] for p in all_phi]
    ax.bar(all_steps, all_mags, color=bar_colors, alpha=0.85, zorder=2)
    ax.plot(all_steps, all_kap, 'o--', color='#ffffff', linewidth=1.8,
            markersize=6, label='kappa (curvature)', zorder=3)

    ax.set_ylabel('Magnitude')
    ax.set_title(
        'Displacement ||delta|| and Curvature kappa per Meaning Step\n'
        'Bar colour = dominant driver phi',
        color='#dddddd')
    ax.tick_params(axis='x', labelsize=8)
    ax.spines['bottom'].set_color('#333')
    ax.spines['left'].set_color('#333')

    from matplotlib.patches import Patch
    legend_els = [Patch(facecolor=COLORS[i], label=DIM[i]) for i in range(6)]
    legend_els.append(
        plt.Line2D([0], [0], color='white', linestyle='--', marker='o',
                   label='kappa'))
    ax.legend(handles=legend_els, loc='upper left',
              framealpha=0.15, labelcolor='white', fontsize=8)

    plt.tight_layout()
    plt.savefig('output/manifold_steps.png', dpi=150, facecolor=BG)
    plt.close()
    print('  saved: output/manifold_steps.png')


# ── Chart 3: Gaussian profiles, final state ───────────────────────────────────
def plot_gaussians():
    x = np.linspace(-1.5, 1.5, 400)
    sigma = 0.20

    fig, ax = plt.subplots(figsize=(10, 7), facecolor=BG)
    ax.set_facecolor(BG)

    for i, dim in enumerate(DIM):
        mu_en = en_states[-1, i]
        mu_es = es_states[-1, i]
        offset = i * 3.2
        col = COLORS[i]

        y_en = np.exp(-0.5 * ((x - mu_en) / sigma) ** 2) / (sigma * np.sqrt(2 * np.pi))
        y_es = np.exp(-0.5 * ((x - mu_es) / sigma) ** 2) / (sigma * np.sqrt(2 * np.pi))

        ax.fill_between(x, offset, y_en + offset, alpha=0.30, color=col)
        ax.plot(x, y_en + offset, color=col, linewidth=2.0, label=f'{dim} EN')
        ax.plot(x, y_es + offset, color=col, linewidth=1.5, linestyle='--',
                alpha=0.75)
        ax.text(-1.45, offset + 0.4, dim, fontsize=9, color=col)

    ax.set_xlabel('Dimension value  [-1, 1]')
    ax.set_title(
        'Gaussian Profiles: Final Meaning State per Dimension\n'
        'Solid = EN   Dashed = ES',
        color='#dddddd')
    ax.set_yticks([])
    ax.spines['bottom'].set_color('#333')
    ax.spines['left'].set_color('#222')
    ax.axvline(0, color='#333', linewidth=0.8, linestyle=':')

    plt.tight_layout()
    plt.savefig('output/manifold_gaussians.png', dpi=150, facecolor=BG)
    plt.close()
    print('  saved: output/manifold_gaussians.png')


# ── Chart 4: animated EN trajectory ──────────────────────────────────────────
def plot_animation():
    fig = plt.figure(figsize=(9, 6), facecolor=BG)
    ax = fig.add_subplot(111, projection='3d')
    ax.set_facecolor(BG)
    ax.set_xlim(-1, 1); ax.set_ylim(-1, 1); ax.set_zlim(-1, 1)
    ax.set_xlabel('ideational'); ax.set_ylabel('field'); ax.set_zlabel('textual')
    ax.set_title('EN Meaning Trajectory — Animated', color='#dddddd')
    for pane in [ax.xaxis.pane, ax.yaxis.pane, ax.zaxis.pane]:
        pane.set_facecolor((0.08, 0.08, 0.12, 0.6))
        pane.set_edgecolor('#222222')

    line,  = ax.plot([], [], [], color=EN_COLOR, linewidth=2.5)
    point, = ax.plot([], [], [], 'o', color=EN_COLOR, markersize=9)
    label_obj = ax.text2D(0.05, 0.92, '', transform=ax.transAxes,
                          color=EN_COLOR, fontsize=11)

    xs = en_states[:, 0]
    ys = en_states[:, 1]
    zs = en_states[:, 4]

    def init():
        line.set_data([], []); line.set_3d_properties([])
        point.set_data([], []); point.set_3d_properties([])
        label_obj.set_text('')
        return line, point, label_obj

    def update(frame):
        n = frame + 1
        line.set_data(xs[:n], ys[:n]); line.set_3d_properties(zs[:n])
        point.set_data([xs[frame]], [ys[frame]]); point.set_3d_properties([zs[frame]])
        label_obj.set_text(en_labels[frame])
        ax.view_init(elev=20, azim=frame * 12)
        return line, point, label_obj

    anim = animation.FuncAnimation(
        fig, update, frames=len(en_states),
        init_func=init, interval=900, blit=False)

    try:
        writer = animation.FFMpegWriter(fps=1, bitrate=800)
        anim.save('output/manifold_anim.mp4', writer=writer)
        print('  saved: output/manifold_anim.mp4')
    except Exception as e:
        print(f'  MP4 skipped (ffmpeg not found): {e}')
        anim.save('output/manifold_anim.gif', writer='pillow', fps=1)
        print('  saved: output/manifold_anim.gif  (fallback)')
    plt.close()


if __name__ == '__main__':
    no_anim = '--no-anim' in sys.argv
    print('Generating semiotic manifold visualisations...')
    plot_3d()
    plot_steps()
    plot_gaussians()
    if not no_anim:
        plot_animation()
    print('Done. Charts in output/')
