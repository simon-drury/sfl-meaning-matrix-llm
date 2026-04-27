#!/usr/bin/env python3
"""
app.py
Gradio demo: SFL Meaning Matrix pipeline + visualisation.

Two tabs:
  1. Pipeline  -- encode EN or ES iconic prompt -> trajectory + realization in all 5 languages
  2. Visualise -- generate the three static manifold charts

Run locally:
  pip install -r requirements.txt gradio
  python app.py

Deploy to Hugging Face Spaces:
  - Runtime: CPU basic (no GPU required)
  - requirements.txt must include: gradio numpy matplotlib fastapi uvicorn pydantic
"""

import os
import numpy as np
import gradio as gr

from sfl_matrix_engine import encode_en, encode_es
from sfl_manifold import compute_manifold
from sfl_attention import cluster_attention, activated_region
from sfl_realize import (
    build_pilot_en, build_pilot_es, build_pilot_pt,
    build_pilot_it, build_pilot_zh,
)
from sfl_visualise import plot_3d, plot_steps, plot_gaussians

os.makedirs("output", exist_ok=True)

VOCABS = {
    "EN": build_pilot_en(),
    "ES": build_pilot_es(),
    "PT": build_pilot_pt(),
    "IT": build_pilot_it(),
    "ZH": build_pilot_zh(),
}

ENCODERS = {"EN": encode_en, "ES": encode_es}


# ---------------------------------------------------------------------------
# Tab 1: Pipeline
# ---------------------------------------------------------------------------

def run_pipeline(lang: str) -> str:
    traj = ENCODERS[lang]()
    analysis = compute_manifold(traj)
    attn = cluster_attention(traj)
    region = activated_region(traj, attn)

    lines = []
    lines.append(f"## Meaning Trajectory [{lang}]\n")
    lines.append(f"{'Step':<4} {'Label':<26} {'||delta||':>8}  {'kappa':>7}  {'driver':<16}")
    lines.append("-" * 68)
    for s in analysis.steps:
        kap = f"{s.curvature:.3f}" if not np.isnan(s.curvature) else "   -  "
        lines.append(
            f"{s.t:<4} {s.label[:25]:<26} {s.displacement:>8.3f}  {kap:>7}  {s.dominant_driver:<16}"
        )
    lines.append(f"\nGeodesic energy E(gamma): {analysis.path_loss:.4f}")

    lines.append("\n## Attention clusters (softmax weights across steps)\n")
    step_labels = [s.label for s in traj.states]
    header = f"{'Step':<26}" + "".join(f"{c[:12]:>14}" for c in attn)
    lines.append(header)
    lines.append("-" * (26 + 14 * len(attn)))
    for i, lbl in enumerate(step_labels):
        row = f"{lbl[:25]:<26}" + "".join(f"{attn[c][i]:>14.3f}" for c in attn)
        lines.append(row)

    lines.append("\n## Activated semiotic region (attention-weighted centroid)\n")
    dim_names = ["ideational", "field", "interpersonal", "tenor", "textual", "mode"]
    for name, val in zip(dim_names, region):
        bar = "+" * int(abs(val) * 20) if val >= 0 else "-" * int(abs(val) * 20)
        lines.append(f"  {name:<15} {val:>7.3f}  {bar}")

    lines.append("\n## Five-language realization (same M_out, no translation)\n")
    M_out = region
    for code, vocab in VOCABS.items():
        best, dist = vocab.nearest(M_out, k=1)[0]
        top3 = vocab.nearest(M_out, k=3)
        candidates = "  ".join(f"{w}({d:.2f})" for w, d in top3)
        lines.append(f"  {code:<4} best: {best:<20} candidates: {candidates}")

    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Tab 2: Visualise
# ---------------------------------------------------------------------------

def run_visualise():
    plot_3d()
    plot_steps()
    plot_gaussians()
    return (
        "output/manifold_3d.png",
        "output/manifold_steps.png",
        "output/manifold_gaussians.png",
    )


# ---------------------------------------------------------------------------
# Gradio UI
# ---------------------------------------------------------------------------

with gr.Blocks(title="SFL Meaning Matrix") as demo:
    gr.Markdown(
        "# SFL Meaning Matrix\n"
        "**Meaning before form. Language after meaning.**\n\n"
        "Phase 1 demo: meaning manifold pipeline + visualisation. "
        "No GPU required. No model downloads."
    )

    with gr.Tab("Pipeline"):
        gr.Markdown(
            "Run the full pipeline on one of the two iconic pilot prompts.\n\n"
            "- **EN**: *hey / why dont you / print hello world / for me / please thank you*\n"
            "- **ES**: *buenos dias / hoy es viernes / Esto es CNN / dia importante / y para muchos*"
        )
        lang_input = gr.Radio(
            choices=["EN", "ES"], value="EN", label="Input language"
        )
        run_btn = gr.Button("Run pipeline")
        output_text = gr.Textbox(
            label="Pipeline output", lines=40, max_lines=60
        )
        run_btn.click(fn=run_pipeline, inputs=lang_input, outputs=output_text)

    with gr.Tab("Visualise"):
        gr.Markdown(
            "Generate the three static manifold charts from the two pilot trajectories."
        )
        viz_btn = gr.Button("Generate charts")
        img_3d    = gr.Image(label="3D trajectories (ideational / field / textual)")
        img_steps = gr.Image(label="Displacement and curvature per step")
        img_gauss = gr.Image(label="Gaussian profiles — final meaning state")
        viz_btn.click(
            fn=run_visualise,
            inputs=None,
            outputs=[img_3d, img_steps, img_gauss],
        )

if __name__ == "__main__":
    demo.launch(share=True)
