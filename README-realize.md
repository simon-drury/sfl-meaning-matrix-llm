# sfl_realize.py — De-matrixising: Meaning State to Lexical Output

## Purpose

The final stage of the pipeline. The transformer outputs a meaning state
\(M_{\text{out}} \in \mathcal{M}\). This module retrieves the lexical items
whose semiotic fingerprints \(\mathbf{f}_w\) are closest to \(M_{\text{out}}\)
within the vocabulary space \(\mathcal{V}_L\) of a target language \(L\).

\[
w^* = \arg\min_{w \in \mathcal{V}_L}\; \left\| \mathbf{f}_w - M_{\text{out}} \right\|_2
\]

---

## Co-equal multilingual realization

The same \(M_{\text{out}}\) presented to \(\mathcal{V}_{\text{EN}}\) and
\(\mathcal{V}_{\text{ES}}\) produces two independent realizations in their
respective languages. There is no translation step. Both outputs are
co-equal realizations of the same meaning state.

Whereas machine translation maps form to form across languages, this
architecture maps meaning to form independently within each language.

---

## Semiotic fingerprints

Each lexical item \(w \in \mathcal{V}_L\) carries a fingerprint
\(\mathbf{f}_w \in [-1, 1]^6\) encoding its metafunctional position
in the semiotic manifold. In production, fingerprints are learned from
SFL-annotated corpora. The pilot vocabularies are hand-encoded from
the two iconic prompt analyses.

As with all components, the fingerprint dimensionality \(n_{\text{dim}}\)
is a parameter. Vocabularies grow with the manifold.

---

## Pipeline position

```
sfl_matrix_engine.py   parse prompt -> MeaningTrajectory
       |
sfl_manifold.py        path geometry -> kappa, delta, phi, L_sp
       |
sfl_adapter.py         W_adapt: R^6 -> R^d_model
       |
[transformer]          forward pass over meaning embeddings
       |
sfl_realize.py         M_out -> w* in V_L
```

---

## Pilot results

### EN trajectory realization

| Step | Source unit | Best match | Top candidates |
|---|---|---|---|
| 0 | hey | hey | hey(0.00)  hello(0.22)  sorry(0.79) |
| 1 | why dont you | hello | hello(0.42)  hey(0.49)  sorry(0.78) |
| 2 | print hello world | hello world | hello world(0.37)  print(0.55)  code(0.72) |
| 3 | for me | for me | for me(0.00)  print(0.55)  show(0.62) |
| 4 | please thank you | thank you | thank you(0.26)  please(0.37)  sorry(0.63) |

### Cross-language demo: EN final state -> both vocabularies

```
EN best match : thank you
ES best match : gracias
(same M_out, different V_L -- no translation)
```

The meaning state encodes *gratitude + interpersonal closure*.
The EN vocabulary realizes it as `thank you`; the ES vocabulary
realizes it as `gracias`. One meaning, two co-equal forms.

---

## Scalability

`VocabularySpace` is a pure data structure. It can be backed by:
- An in-memory numpy array (current pilot)
- A FAISS index for million-scale vocabularies
- A distributed vector store for cross-lingual, multi-register corpora

The `nearest()` interface is identical in all cases.

---

## Next step

`api.py` — FastAPI wrapper exposing the full pipeline as a stateless
HTTP service, horizontally scalable at Tier 2.
