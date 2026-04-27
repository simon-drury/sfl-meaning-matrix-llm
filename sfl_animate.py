#!/usr/bin/env python3
"""
sfl_animate.py
Export a self-contained animated HTML visualisation of the SFL meaning
trajectories using Plotly.  No server required — open the file in any browser.

Outputs
-------
  output/manifold_animated.html

Usage
-----
  python sfl_animate.py

Or call generate_html() from app.py to wire it into the Gradio UI.
"""

import os
import json
import numpy as np

from sfl_matrix_engine import encode_en, encode_es, MeaningTrajectory

os.makedirs("output", exist_ok=True)

EN_COLOR = "#4f98a3"
ES_COLOR = "#da7101"
BG       = "#12121a"
DIM      = ["ideational", "field", "interpersonal", "tenor", "textual", "mode"]


def _traj_to_dict(traj: MeaningTrajectory, color: str) -> dict:
    states = [s.to_vector() for s in traj.states]
    labels = [s.label for s in traj.states]
    return {
        "lang":   traj.lang,
        "color":  color,
        "labels": labels,
        "states": [list(map(float, v)) for v in states],
    }


def generate_html(out_path: str = "output/manifold_animated.html") -> str:
    en = _traj_to_dict(encode_en(), EN_COLOR)
    es = _traj_to_dict(encode_es(), ES_COLOR)
    data_json = json.dumps({"en": en, "es": es})

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<title>SFL Meaning Matrix — Animated Manifold</title>
<script src="https://cdn.plot.ly/plotly-2.32.0.min.js"></script>
<style>
  body  {{ background:{BG}; color:#ccc; font-family:monospace; margin:0; padding:0; }}
  #top  {{ display:flex; align-items:center; gap:16px; padding:14px 20px; background:#0d0d14; }}
  h1    {{ font-size:1rem; margin:0; color:#eee; font-weight:400; }}
  .btn  {{ background:#1e1e2e; color:#ccc; border:1px solid #333; padding:6px 16px;
           border-radius:4px; cursor:pointer; font-family:monospace; font-size:.85rem; }}
  .btn.active {{ border-color:{EN_COLOR}; color:{EN_COLOR}; }}
  .btn.active-es {{ border-color:{ES_COLOR}; color:{ES_COLOR}; }}
  #txt  {{ flex:1; background:#1e1e2e; color:#eee; border:1px solid #333;
           padding:6px 12px; border-radius:4px; font-family:monospace;
           font-size:.85rem; outline:none; }}
  #encode-btn {{ background:#1e1e2e; color:#aaa; border:1px solid #333;
                 padding:6px 14px; border-radius:4px; cursor:pointer;
                 font-family:monospace; font-size:.85rem; }}
  #encode-btn:hover {{ border-color:#aaa; color:#eee; }}
  #chart {{ width:100vw; height:calc(100vh - 58px); }}
  #info  {{ position:fixed; bottom:16px; right:20px; font-size:.78rem;
            color:#555; pointer-events:none; }}
</style>
</head>
<body>
<div id="top">
  <h1>SFL Meaning Manifold</h1>
  <button class="btn active"   id="btn-en" onclick="switchLang('en')">EN</button>
  <button class="btn"          id="btn-es" onclick="switchLang('es')">ES</button>
  <input  id="txt" type="text" placeholder="free text — press Encode to project onto manifold" />
  <button id="encode-btn" onclick="encodeText()">Encode</button>
</div>
<div id="chart"></div>
<div id="info">axes: ideational &nbsp;·&nbsp; field &nbsp;·&nbsp; textual</div>

<script>
const RAW = {data_json};
const DIM = {json.dumps(DIM)};
let currentLang = 'en';

function buildFrames(traj) {{
  const frames = [];
  const n = traj.states.length;
  for (let k = 1; k <= n; k++) {{
    const xs = [], ys = [], zs = [], ts = [];
    for (let i = 0; i < k; i++) {{
      xs.push(traj.states[i][0]);
      ys.push(traj.states[i][1]);
      zs.push(traj.states[i][4]);
      ts.push(traj.labels[i]);
    }}
    // current point highlight
    const cx = [traj.states[k-1][0]];
    const cy = [traj.states[k-1][1]];
    const cz = [traj.states[k-1][4]];
    const cl = [traj.labels[k-1]];
    frames.push({{
      name: String(k),
      data: [
        {{ x: xs, y: ys, z: zs, text: ts,
           mode: 'lines+markers+text',
           textposition: 'top center',
           textfont: {{ size: 11, color: traj.color }},
           marker: {{ size: 5, color: traj.color, opacity: 0.6 }},
           line: {{ color: traj.color, width: 3 }} }},
        {{ x: cx, y: cy, z: cz, text: cl,
           mode: 'markers+text',
           textposition: 'top center',
           textfont: {{ size: 13, color: '#ffffff' }},
           marker: {{ size: 12, color: '#ffffff',
                      line: {{ color: traj.color, width: 2 }} }} }},
      ]
    }});
  }}
  return frames;
}}

function makeLayout(lang) {{
  const col = lang === 'en' ? '{EN_COLOR}' : '{ES_COLOR}';
  return {{
    paper_bgcolor: '{BG}',
    scene: {{
      bgcolor: '#0d0d14',
      xaxis: {{ title: 'ideational', color: '#666', range: [-1.1, 1.1] }},
      yaxis: {{ title: 'field',       color: '#666', range: [-1.1, 1.1] }},
      zaxis: {{ title: 'textual',     color: '#666', range: [-1.1, 1.1] }},
      camera: {{ eye: {{ x: 1.4, y: 1.4, z: 0.7 }} }},
    }},
    margin: {{ l:0, r:0, t:30, b:0 }},
    font: {{ color: '#aaa', family: 'monospace' }},
    showlegend: false,
    title: {{
      text: lang.toUpperCase() + ' — meaning trajectory through semiotic manifold',
      font: {{ size: 13, color: '#888' }}, x: 0.01
    }},
    updatemenus: [{{
      type: 'buttons', showactive: false,
      x: 0.01, y: 0.01, xanchor: 'left', yanchor: 'bottom',
      bgcolor: '#1e1e2e', bordercolor: '#333', font: {{ color: '#aaa', size: 11 }},
      buttons: [
        {{ label: '▶ Play',  method: 'animate',
           args: [null, {{ fromcurrent: true, frame: {{ duration: 700, redraw: true }},
                           transition: {{ duration: 400, easing: 'cubic-in-out' }} }}] }},
        {{ label: '⏸ Pause', method: 'animate',
           args: [[null], {{ mode: 'immediate', frame: {{ duration: 0 }}, transition: {{ duration: 0 }} }}] }},
      ]
    }}],
    sliders: [{{
      steps: RAW[lang].states.map((_, i) => ({{
        method: 'animate',
        label: RAW[lang].labels[i],
        args: [[String(i+1)], {{ mode: 'immediate', frame: {{ duration: 0 }}, transition: {{ duration: 200 }} }}]
      }})),
      x: 0.05, y: 0, len: 0.9,
      currentvalue: {{ prefix: 'step: ', font: {{ color: '#aaa', size: 11 }} }},
      bgcolor: '#1e1e2e', bordercolor: '#333',
      font: {{ color: '#888', size: 10 }},
    }}],
  }};
}}

function render(lang, extraTraces) {{
  const traj   = RAW[lang];
  const frames = buildFrames(traj);
  const first  = frames[0].data;
  const traces = [...first, ...(extraTraces || [])];
  Plotly.newPlot('chart', traces, makeLayout(lang), {{ responsive: true }})
    .then(() => Plotly.addFrames('chart', frames));
}}

function switchLang(lang) {{
  currentLang = lang;
  document.getElementById('btn-en').className = 'btn' + (lang==='en' ? ' active' : '');
  document.getElementById('btn-es').className = 'btn' + (lang==='es' ? ' active-es' : '');
  render(lang);
}}

// Free-text encoder: naive projection onto 6D manifold
// Each word contributes a small delta proportional to its character hash.
// This is intentionally lightweight — it shows trajectory shape, not semantics.
function hashWord(w) {{
  let h = 0;
  for (let c of w) h = (Math.imul(31, h) + c.charCodeAt(0)) | 0;
  return h;
}}

function encodeText() {{
  const raw = document.getElementById('txt').value.trim();
  if (!raw) return;
  const words = raw.split(/\\s+/);
  // Start from origin
  let state = [0,0,0,0,0,0];
  const xs=[state[0]], ys=[state[1]], zs=[state[4]], ts=['[start]'];
  for (const w of words) {{
    const h = hashWord(w);
    const delta = DIM.map((_, i) => ((h >> (i*4)) & 0xff) / 255 * 0.4 - 0.2);
    state = state.map((v,i) => Math.max(-1, Math.min(1, v + delta[i])));
    xs.push(state[0]); ys.push(state[1]); zs.push(state[4]); ts.push(w);
  }}
  const freeTrace = {{
    x: xs, y: ys, z: zs, text: ts,
    type: 'scatter3d', mode: 'lines+markers+text',
    textposition: 'top center',
    textfont: {{ size: 10, color: '#aaffaa' }},
    marker: {{ size: 5, color: '#aaffaa', opacity: 0.8 }},
    line: {{ color: '#aaffaa', width: 2, dash: 'dot' }},
    name: 'free text'
  }};
  // Overlay onto existing chart without full redraw
  const data  = document.getElementById('chart').data || [];
  const idx   = data.findIndex(t => t.name === 'free text');
  if (idx >= 0) Plotly.deleteTraces('chart', idx);
  Plotly.addTraces('chart', freeTrace);
}}

// init
render('en');
</script>
</body>
</html>
"""
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(html)
    print(f"  saved: {out_path}")
    return out_path


if __name__ == "__main__":
    generate_html()
