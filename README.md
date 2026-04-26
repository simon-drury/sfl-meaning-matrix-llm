# SFL Meaning Matrix LLM

> **language as social semiotic halliday 1978**

A research architecture that grounds transformer-based language models in
Systemic Functional Linguistics (SFL). Instead of predicting the next token
directly, the system computes a trajectory through a six-dimensional
*semiotic manifold* — then realizes that trajectory as lexical output
independently in each target language.

English and Spanish are co-equal first languages. There is no translation step.

---

## The core claim

Current LLMs map form to form: token sequence in, token sequence out.
This architecture maps form to meaning to form:

```
prompt (any modality)
     |
     v
MeaningTrajectory in M   <-- semiotic manifold, 6 dimensions
     |
     v
W_adapt: R^6 -> R^d_model   <-- adapter layer
     |
     v
[transformer forward pass]  <-- modality-blind
     |
     v
M_out in M               <-- output meaning state
     |
     v
w* in V_L                <-- nearest item in realization space for modality L
```

The manifold encodes the six metafunctions of SFL:
**ideational, field, interpersonal, tenor, textual, mode.**
Every meaning state is a point in this space. Every utterance is a trajectory.

---

## Quick start

```bash
git clone https://github.com/simon-drury/sfl-meaning-matrix-llm.git
cd sfl-meaning-matrix-llm
pip install -r requirements.txt

# Run the geometry engine on the two pilot prompts
python sfl_manifold.py

# Run the de-matrixising demo (EN + ES co-equal realization)
python sfl_realize.py

# Produce all visualisation charts
python sfl_visualise.py --no-anim       # static PNGs
python sfl_visualise.py                 # + MP4 animation (needs ffmpeg)

# Run the API
uvicorn api:app --reload
# -> http://127.0.0.1:8000/docs
```

Charts are written to `output/`.

---

## Repository map

| File | Stage | Detail |
|---|---|---|
| `MANIFOLD.md` | Theory | Full formal specification with LaTeX |
| `sfl_matrix_engine.py` | Parse | Prompt -> `MeaningTrajectory` |
| `sfl_manifold.py` | Geometry | delta_t, kappa_t, phi_t, L_sp |
| `sfl_attention.py` | Attention | SFL-weighted self-attention mask |
| `sfl_adapter.py` | Adapter | W_adapt: R^6 -> R^d_model |
| `sfl_realize.py` | Realize | M_out -> w* in V_L (EN and ES) |
| `sfl_visualise.py` | Visualise | 3D trajectory, step geometry, Gaussians, animation |
| `api.py` | API | FastAPI wrapper, modality-first, full pipeline endpoint |
| `wadapt_lora_training_sketch.ipynb` | Research | Colab sketch: LoRA adapter training toward Llama-3.2 |

Each module has two READMEs: English (`README-{module}.md`) and
Spanish (`README-{module}-ES.md`).

---

## The two pilot prompts

All pilot data derives from exactly two iconic prompts, one per language.

**EN** — a human instructing an LLM:
```
hey  /  why dont you  /  print hello world  /  for me  /  please thank you
```

**ES** — a broadcast news opening:
```
buenos dias  /  hoy es viernes  /  Esto es CNN  /  dia importante  /  y para muchos
```

These were chosen because they span the full range of the semiotic manifold:
from phatic interpersonal register (low ideational, high tenor) to
institutional broadcast register (high field, high textual).

---

## The six dimensions

| Dimension | What it encodes | Range |
|---|---|---|
| ideational | propositional / experiential content | [-1, 1] |
| field | domain / subject matter specificity | [-1, 1] |
| interpersonal | speaker-hearer relationship | [-1, 1] |
| tenor | formality and power | [-1, 1] |
| textual | discourse / cohesion | [-1, 1] |
| mode | channel / written-spoken continuum | [-1, 1] |

A meaning state M_t is a point in [-1, 1]^6.
A meaning trajectory T is the ordered sequence M_0, M_1, ..., M_T.

---

## Key geometric quantities

| Symbol | Name | What it measures |
|---|---|---|
| delta_t | displacement | how far meaning moved at step t |
| kappa_t | curvature | how sharply the trajectory turned at step t |
| phi_t | driver | which dimension drove the move |
| L_sp | path length | total semantic distance traversed |

A straight trajectory = coherent, low-energy meaning development.
A sharp kappa peak = semantic event: register shift, evaluative move, field change.

---

## Co-equal multilingual realization

The same M_out presented to V_EN and V_ES independently:

```
EN final state (please thank you):
  EN best match : thank you
  ES best match : gracias
  (same M_out, different V_L -- no translation)
```

The meaning state encodes *gratitude + interpersonal closure*.
Each vocabulary realizes it in its own language from the same geometric point.

---

## Determinism and probability

The system is deliberately agnostic on this question at the current stage.
A meaning state is modelled as a Gaussian region in the manifold
(sigma = 0.20 in the pilot), not a point. This means:

- Small displacements (delta_t < 0.3) are treated as within-region movement
- Large displacements signal genuine semantic events
- The nearest-neighbour retrieval in sfl_realize.py can be extended to
  top-k stochastic sampling from the Gaussian at any time

Whether the trajectory is deterministic (given sufficient context) or
irreducibly probabilistic is an open research question.

---

## Visualisation outputs

Running `sfl_visualise.py` produces:

| File | What it shows |
|---|---|
| `output/manifold_3d.png` | EN and ES trajectories as paths through ideational/field/textual space |
| `output/manifold_steps.png` | Displacement and curvature per step, coloured by dominant driver |
| `output/manifold_gaussians.png` | Gaussian profiles for all 6 dimensions at final state |
| `output/manifold_anim.mp4` | Animated EN trajectory, one frame per meaning unit |

---

## API

See [`README-api.md`](README-api.md) for full endpoint documentation.

```bash
uvicorn api:app --reload
# Interactive docs at http://127.0.0.1:8000/docs
```

| Endpoint | What it does |
|---|---|
| `GET /health` | Liveness check |
| `GET /dims` | Manifold dimension names and ranges |
| `POST /analyze` | Prompt -> full MeaningTrajectory with geometry |
| `POST /realize` | M_out + modality -> nearest realization |
| `POST /pipeline` | Prompt + modality -> trajectory + realization |

---

## Formal theory

See [`MANIFOLD.md`](MANIFOLD.md) for the full mathematical specification,
including the definition of M as a smooth Riemannian manifold, the
geodesic path functional, the adapter projection, and the realization
retrieval criterion.

---

## Implementation status

**Phase 1 — meaning manifold pipeline: complete and runnable.**

| Component | File | Status |
|---|---|---|
| Semantic parser (matrix engine) | `sfl_matrix_engine.py` | ✅ Operational |
| Manifold geometry | `sfl_manifold.py` | ✅ Operational |
| SFL attention layer | `sfl_attention.py` | ✅ Operational |
| Lexical realization (EN/ES/PT/IT/ZH) | `sfl_realize.py` | ✅ Operational |
| Trajectory visualisation | `sfl_visualise.py` | ✅ Operational |
| FastAPI pipeline wrapper | `api.py` | ✅ Operational |
| LoRA adapter sketch (Colab) | `wadapt_lora_training_sketch.ipynb` | ✅ Runnable in Colab |

**Phase 2 — transformer integration: architecture specified, implementation in progress.**

| Component | File | Status | Requires |
|---|---|---|---|
| Adapter projection W_adapt | `sfl_adapter.py` | 🔧 Integration pending | GPT4All local install |
| GPT4All bridge | `sfl_gpt4all.py` | 🔧 Integration pending | GPT4All local install + model (~4 GB) |
| Wadapt LoRA training | `wadapt_lora_training_sketch.ipynb` | 🔧 Training targets pending | Llama-3.2 hidden states |

Phase 1 components run with `pip install -r requirements.txt` — no GPU, no model downloads, under 50 MB total.
Phase 2 components require a local transformer installation and are the subject of ongoing research.

---

## Theoretical grounding

- Halliday, M.A.K. (1985). *An Introduction to Functional Grammar*. Arnold.
- Halliday, M.A.K. & Matthiessen, C. (2014). *Halliday's Introduction to Functional Grammar* (4th ed.). Routledge.
- Martin, J.R. (1992). *English Text: System and Structure*. Benjamins.

The SFL metafunctions (ideational, interpersonal, textual) and the
register variables (field, tenor, mode) are the theoretical basis for
the six dimensions of the manifold.

---

## Language policy

All module READMEs are maintained in parallel:
English (`README-{module}.md`) and Spanish (`README-{module}-ES.md`).
Both are primary. Neither is a translation of the other.
