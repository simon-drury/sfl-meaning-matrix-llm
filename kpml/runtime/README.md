# Hosted KPML Runtime Resolution Package

This is the remote-first build boundary for the KPML realization experiment.

It does **not** pretend that a KPML distribution, loader, grammar, or generation
entrypoint has already been validated. Instead it establishes the reproducible
conditions required to add one without guessing:

1. Pin a retrievable KPML source archive in `source-lock.yaml`.
2. Record its immutable revision, SHA-256 digest, and license.
3. Identify the actual Lisp loader, grammar root, and generation entrypoint.
4. Build and run remotely in a dedicated Hugging Face Docker Space.
5. Preserve curated source provenance, grammar versions, fixtures, traces, and
   experimental conclusions in GitHub.

## Repository roles

| System | Role |
|---|---|
| GitHub `kpml-sandbox` | Canonical source, research record, fixtures, manifests, and curated results |
| Hugging Face Docker Space | Disposable remote runtime for source resolution and generation |
| Hugging Face persistent storage at `/data` | Runtime-local traces, source provenance, and batch outputs |
| Colab | Optional disposable client for submitting batches to the remote API |

## Space target

The intended independent runtime is:

```text
simondrury/kpml-sfl-realizer
```

It must remain separate from the existing SFL manifold demonstration Space.

## Safety gate

`source-lock.yaml` is initially unresolved. The resolver refuses to download or
extract KPML until all identity and integrity fields are supplied. The HTTP
`/generate` endpoint returns a clear blocked response until a source is locked
and the actual KPML Lisp bridge has been committed.

This is an integration gate, not a substitute for integration. Once a source is
pinned, the next additive commit is the Common Lisp loader/bridge and the first
end-to-end realization run for the three cases in `deployment-manifest.yaml`.
