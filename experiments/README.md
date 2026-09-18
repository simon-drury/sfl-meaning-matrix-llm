# LASSM semiotic-transition baseline

This experiment tests a narrow, falsifiable question: can a model using the LASSM 3x2 state structure and its intrinsic covariance features predict the next six-dimensional semiotic state more accurately than a small MLP baseline?

## Run

```bash
pip install torch
python experiments/lassm_baseline_comparison.py
```

The script writes `experiments/results_seed_transition.json`, containing total MSE, MSE by semiotic axis, and mean Euclidean next-state error for both models.

## Models

- `BaselineMLP` consumes the six flattened source coordinates.
- `StructuredLASSM` reshapes those coordinates into a 3x2 state, derives register covariance `M^T M` and metafunction covariance `M M^T`, and uses the original coordinates plus those 13 derived values.

## Scope and limits

`data/seed_turn_transitions.csv` contains 20 manually constructed, heuristic seed annotations. It is a runnable smoke-test dataset, not an empirical validation corpus. Its metrics must not be used to support claims of general linguistic validity, multilingual transfer, or superiority of LASSM. The next research task is to replace this seed set with independently annotated data and use repeated, held-out evaluation.
