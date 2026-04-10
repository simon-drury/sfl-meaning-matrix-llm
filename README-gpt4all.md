# sfl_gpt4all.py -- GPT4All Adapter Bridge

## What this does

Connects the SFL semiotic manifold to a locally running GPT4All model.
This is the step from simulated transformer to real transformer.

```
M_t in R^6
     |
     v
W_adapt (R^6 -> R^768)       <- adapter layer, trained in Step 2
     |
     v
[GPT4All model]               <- backbone, frozen
     |
     v
h_out in R^768
     |
     v
W_inv (R^768 -> R^6)         <- inverse adapter, trained in Step 2
     |
     v
M_out in [-1,1]^6             <- output meaning state
     |
     v
V_L nearest semiotic unit     <- realization in any of EN,ES,PT,IT,ZH
```

---

## Setup

```bash
pip install gpt4all
```

Then download a model in the GPT4All desktop app. Recommended for this stage:

| Model | Use | D_MODEL |
|---|---|---|
| `nomic-embed-text-v1.5.f16.gguf` | Embeddings (fastest) | 768 |
| `Meta-Llama-3-8B-Instruct.Q4_0.gguf` | Full LLM | 4096 |
| `Nous-Hermes-2-Mistral-7B-DPO.Q4_0.gguf` | Full LLM | 4096 |

Set `D_MODEL` in `sfl_gpt4all.py` to match your model.

---

## Dry run (no model needed)

```bash
python sfl_gpt4all.py
```

Runs both pilot trajectories through the adapter matrices only.
No GPT4All model required. Validates the pipeline shape.

---

## Live run

```python
from sfl_gpt4all import encode_en, run_adapter_pipeline

traj = encode_en()
result = run_adapter_pipeline(
    traj,
    model_name="nomic-embed-text-v1.5.f16.gguf",
    use_gpt4all=True
)
```

---

## Step 2 -- training W_adapt and W_inv

Currently W_adapt and W_inv are randomly initialised.
Training them is the next step:

1. Generate (M_t, label) pairs from the pilot trajectories
2. Get GPT4All embeddings for each label
3. Train W_adapt to minimise || GPT4All_embed(label) - W_adapt @ M_t ||_2
4. Train W_inv to minimise || M_t - W_inv @ GPT4All_embed(label) ||_2

This is a simple linear regression on each side. No GPU required.
Once trained, W_adapt and W_inv are saved and loaded at runtime.

---

## Status

| Component | Status |
|---|---|
| Adapter scaffold | complete |
| Dry run pipeline | complete |
| GPT4All live integration | ready to test |
| W_adapt / W_inv training | next |
