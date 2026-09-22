# sfl_realize.py — Lexical Realization

Maps a 9D semiotic output state $M_{\text{out}} \in [-1,1]^9$ to the nearest lexical item in the empirical vocabulary.

## How it works

Realization is k-nearest-neighbour retrieval over the empirical vocabulary:

$$w^* = \arg\min_{w \in \mathcal{V}} \|\hat{\mathbf{m}}_{\text{out}} - \mathbf{f}_w\|_2$$

where $\mathbf{f}_w$ is the empirical 9D centroid for lexical item $w$, derived from treebank trajectories.

- **Input**: 9D state vector $\mathbf{m}_{\text{out}} \in [-1,1]^9$
- **Vocabulary**: `data/empirical_vocabulary_9d.json` — 32,580 items with empirical centroids
- **Output**: best match + ranked candidates with Euclidean distances
- **Multilingual**: same M_out presented independently to EN, ES, FR vocabularies — no translation

## Run

```bash
python sfl_realize.py
```

## Notes

- The realizer is modular and swappable: k-NN now (mv0), learned decoder later (mv1+)
- The SFLMeaningTransformer does not change when the realizer is upgraded
- NLP does the retrieval. SFL does the reasoning.
