# Hosted KPML Runtime Space

This directory is the Docker Space entry point for the experimental
`simondrury/kpml-sfl-realizer` runtime.

## Remote-only rule

- GitHub `kpml-sandbox` is the canonical source and research record.
- The Hugging Face Space executes the runtime remotely.
- Attach persistent Space storage and mount it at `/data` if request records,
  source provenance, traces, or generated corpora must survive restarts.
- No local build or local disk is required.

## Build gate

The image deliberately starts an inspectable API before KPML is available, but
realization is blocked until `../source-lock.yaml` is fully resolved.

A source lock must include:

- HTTPS source archive URL
- immutable revision identifier
- SHA-256 digest of the exact archive
- license
- KPML loader entrypoint
- grammar root
- generation entrypoint

When those values are pinned, run:

```bash
/workspace/bootstrap/build_remote_runtime.sh
```

during the remote build or controlled Space startup. It verifies the archive
before extracting it to `${KPML_HOME:-/opt/kpml}` and writes a provenance record
under `${RESULTS_ROOT:-/data/results}`.

## API

- `GET /health` reports service and source-lock status.
- `GET /metadata` returns the deployment manifest and lock metadata.
- `POST /record-request` records a meaning-matrix request under `/data/results`.
- `POST /generate` remains blocked until the KPML source and Lisp bridge are
  both pinned and implemented.

The intended request boundary is the existing sandbox contract at
`../../01-kpml-input-contract.md`.
