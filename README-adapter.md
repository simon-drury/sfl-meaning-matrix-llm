# sfl_adapter.py — Meaning-to-Embedding Projection Layer

## Purpose

Bridges the semiotic manifold engine and the transformer model.
Takes the \(n_{\text{dim}}\)-dimensional meaning vector produced by
`sfl_manifold.py` and projects it into the embedding space of a local
transformer, so the transformer’s attention machinery can operate over
meaning states rather than token embeddings.

---

## The projection

\[
\mathbf{e}_t = W_{\text{adapt}}\,\mathbf{m}_t + \mathbf{b}
\]

| Symbol | Shape | Description |
|---|---|---|
| \(\mathbf{m}_t\) | \((n_{\text{dim}},)\) | Meaning vector at step \(t\) |
| \(W_{\text{adapt}}\) | \((d_{\text{model}} \times n_{\text{dim}})\) | Learned projection matrix |
| \(\mathbf{b}\) | \((d_{\text{model}},)\) | Learned bias |
| \(\mathbf{e}_t\) | \((d_{\text{model}},)\) | Embedding vector, ready for the transformer |

Only \(W_{\text{adapt}}\) and \(\mathbf{b}\) are trained.
All transformer weights remain frozen in Stage 1.

---

## Supported local models

| Model | \(d_{\text{model}}\) | Trainable params (\(n_{\text{dim}}=6\)) |
|---|---|---|
| DeepSeek-R1-Distill-Qwen-1.5B | 2048 | 14,336 |
| Llama 3.2 3B Instruct | 3072 | 21,504 |

Both models are installed locally via GPT4All v3.10.0.

---

## Scalability

\(n_{\text{dim}} = 6\) is the current minimum viable dimensionality,
derived from the SFL metafunctional architecture at its most reduced form.
It is a **parameter**, not a constant.

Each dimension could become a polynomial, a higher-moment distribution,
or a sub-vector. The number of dimensions will grow as the theory demands.
`AdapterConfig` accepts any \(n_{\text{dim}}\) without changes to the
downstream transformer.

---

## Validation output

```
AdapterConfig(deepseek-r1-distill-qwen-1.5b | d_model=2048 | n_dim=6 | trainable params=14,336)
  Input  shape : (5, 6)
  Output shape : (5, 2048)  OK
  All finite   : True
  Status       : PASS

AdapterConfig(llama-3.2-3b-instruct | d_model=3072 | n_dim=6 | trainable params=21,504)
  Input  shape : (5, 6)
  Output shape : (5, 3072)  OK
  All finite   : True
  Status       : PASS
```

---

## Next step

`sfl_realize.py` — de-matrixising: maps the transformer output state
\(M_{\text{out}} \in \mathcal{M}\) back to lexical items in language \(L\)
via nearest-neighbour retrieval in \(\mathcal{V}_L\).
