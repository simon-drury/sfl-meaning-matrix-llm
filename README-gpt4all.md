# sfl_gpt4all.py — GPT4All Bridge

Bridges the LASSM semiotic pipeline with a locally-running GPT4All transformer backbone.

## Architecture

The bridge implements the full Form → Meaning → Form pipeline with a pretrained backbone:

```
prompt
  |
  v
sfl_matrix_engine_v3.py   ← parse to 9D semiotic trajectory
  |
  v
sfl_adapter.py            ← W_adapt: R^{d_model} → R^9
  |
  v
GPT4All backbone          ← transformer, modality-blind
  |
  v
M_out ∈ [-1,1]^{3×3}
  |
  v
sfl_realize.py            ← k-NN in empirical 9D vocabulary
  |
  v
realization
```

## Status

Tier 2 — requires local GPT4All installation and model download (~4 GB).
The semiotic pipeline (matrix engine, manifold, realizer) runs independently without this bridge.

## Notes

- The transformer backbone is modality-blind throughout
- Adapter training (LoRA toward Llama-3.2 hidden states) is in `wadapt_lora_training_sketch.ipynb`
- See `README-adapter.md` for the adapter specification
