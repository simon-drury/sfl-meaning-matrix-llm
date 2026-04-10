# api.py -- SFL Meaning Matrix: FastAPI Wrapper

## The transformer is modality-blind

The API enforces the core architectural principle:
the transformer operates on meaning states in M.
It has no knowledge of input or output modality.
Modality is handled at the edges -- by the parser (input)
and the realizer (output).

```
prompt (any modality)
     |
     v
[parser]              <- input edge
     |
     v
MeaningTrajectory     <- transformer sees only this
     |
     v
[transformer]
     |
     v
M_out in M
     |
     v
[realizer]            <- output edge, modality is a parameter
     |
     v
realization (text today, audio tomorrow, visual next week)
```

---

## Run

```bash
pip install fastapi uvicorn numpy
uvicorn api:app --reload
```

Interactive docs auto-generated at: `http://127.0.0.1:8000/docs`

---

## Endpoints

| Method | Endpoint | What it does |
|---|---|---|
| `GET` | `/health` | Liveness check |
| `GET` | `/dims` | Manifold dimension names and ranges |
| `POST` | `/analyze` | Prompt -> full MeaningTrajectory with geometry |
| `POST` | `/realize` | M_out + modality -> nearest realization |
| `POST` | `/pipeline` | Prompt + modality -> trajectory + realization in one call |

---

## Example: full pipeline

```bash
curl -X POST http://127.0.0.1:8000/pipeline \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "hey why dont you print hello world for me please thank you",
    "lang_in": "EN",
    "modality": "text",
    "lang_out": "EN",
    "k": 3
  }'
```

```json
{
  "lang_in": "EN",
  "modality": "text",
  "lang_out": "EN",
  "trajectory": [
    {"t": 0, "state": [-0.7, -0.5, 0.8, 0.9, 0.6, -0.6], "label": "hey"},
    {"t": 1, "state": [-0.6, -0.3, 0.9, 0.9, 0.8, -0.6], "delta": 0.26, "kappa": null, "phi": "interpersonal"}
  ],
  "path_length": 1.43,
  "realization": {
    "modality": "text",
    "lang": "EN",
    "best": "thank you",
    "candidates": [
      {"form": "thank you", "distance": 0.26},
      {"form": "please",    "distance": 0.37},
      {"form": "sorry",     "distance": 0.63}
    ]
  }
}
```

---

## Cross-language: same M_out, two modalities

```bash
# EN realization
curl -X POST http://127.0.0.1:8000/realize \
  -d '{"M_out": [0.1, 0.6, 1.0, 1.0, 0.8, -0.6], "modality": "text", "lang": "EN"}'
# -> "thank you"

# ES realization -- same M_out
curl -X POST http://127.0.0.1:8000/realize \
  -d '{"M_out": [0.1, 0.6, 1.0, 1.0, 0.8, -0.6], "modality": "text", "lang": "ES"}'
# -> "gracias"
```

No translation. Two independent lookups in two vocabulary spaces.
The transformer never knew which language was involved.

---

## Adding a new modality

Register a new realizer in `api.py`:

```python
# In _register_text_realizers() or a new _register_audio_realizers():
REALIZERS["audio:EN"] = AudioRealizerEN()   # your class, same .nearest() interface
REALIZERS["visual"]   = VisualRealizer()    # no lang needed for some modalities
```

The `/realize` and `/pipeline` endpoints work immediately.
The transformer does not change.

---

## What this is not

- No authentication
- No persistent storage
- No batching or streaming
- Pilot vocabulary only (hand-encoded fingerprints)

All of those are Tier 2.
