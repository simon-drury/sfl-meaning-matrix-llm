#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
LOCK_FILE="${ROOT}/source-lock.yaml"
KPML_HOME="${KPML_HOME:-/opt/kpml}"
RESULTS_ROOT="${RESULTS_ROOT:-/data/results}"

mkdir -p "${RESULTS_ROOT}"

python3 "${ROOT}/bootstrap/resolve_kpml_source.py" \
  --lock "${LOCK_FILE}" \
  --destination "${KPML_HOME}" \
  --provenance "${RESULTS_ROOT}/kpml-source-provenance.json"

echo "Verified KPML source installed at ${KPML_HOME}"
echo "KPML loader integration remains intentionally disabled until loader_entrypoint,"
echo "grammar_root, and generation_entrypoint are pinned in source-lock.yaml."
