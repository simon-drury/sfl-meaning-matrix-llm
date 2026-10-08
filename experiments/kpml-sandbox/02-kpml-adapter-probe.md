# Experiment 02: Deterministic KPML Adapter Probe

## Question

Can a meaning-matrix request be represented at the KPML boundary in a stable, inspectable form before any external realization is attempted?

## Design

`02-kpml-adapter-probe.py` validates the minimal contract established in `01-kpml-input-contract.md`, serializes it into canonical JSON, and records a structured result.

The probe has two modes:

- **Dry run:** validates and serializes the request with no KPML installation.
- **Command mode:** passes canonical JSON to a locally configured bridge command through `KPML_COMMAND` or `--command`.

The adapter does not claim that canonical JSON is KPML syntax. It is the explicit, deterministic interchange boundary from which a genuine KPML grammar-selection bridge can be implemented and tested.

## Baseline

Before this probe, the sandbox contained a scope and contract but no executable mechanism to validate a request or capture realization-boundary evidence.

## Success criteria

- The supplied minimal request passes validation.
- Equivalent input objects always produce byte-identical canonical serialization.
- Dry-run output records the request, serialization, mode, elapsed time, and environment metadata.
- Command-mode output retains stdout, stderr, exit status, and elapsed time for later comparison.

## Run

```bash
python experiments/kpml-sandbox/02-kpml-adapter-probe.py \
  experiments/kpml-sandbox/examples/minimal-request.json \
  --output experiments/kpml-sandbox/results/minimal-dry-run.json
```

To invoke a local bridge:

```bash
export KPML_COMMAND='kpml-bridge --request '
python experiments/kpml-sandbox/02-kpml-adapter-probe.py \
  experiments/kpml-sandbox/examples/minimal-request.json
```

A bridge command may include `{payload}`, which will be replaced by canonical JSON. If it does not, the command itself remains responsible for reading the request.

## Next experiment

Replace the command shim with a typed mapping from the three metafunctional structures and field–tenor–mode context into a small, documented KPML grammar-selection fragment. Compare outputs against manually authored KPML examples for semantic coverage, grammaticality, and traceability.
