from __future__ import annotations

import json
import os
import pathlib
import uuid
from datetime import datetime, timezone
from typing import Any

import yaml
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field


HERE = pathlib.Path(__file__).resolve()
RUNTIME_ROOT = HERE.parents[1]
LOCK_PATH = RUNTIME_ROOT / "source-lock.yaml"
MANIFEST_PATH = RUNTIME_ROOT / "deployment-manifest.yaml"
RESULTS_ROOT = pathlib.Path(os.environ.get("RESULTS_ROOT", "/data/results"))

app = FastAPI(title="KPML SFL Realizer", version="0.1.0")


class GenerationRequest(BaseModel):
    request_id: str | None = None
    meaning_matrix: dict[str, Any] = Field(default_factory=dict)


def read_yaml(path: pathlib.Path) -> dict[str, Any]:
    return yaml.safe_load(path.read_text(encoding="utf-8")) or {}


def lock_status() -> dict[str, Any]:
    lock = read_yaml(LOCK_PATH)
    source = lock.get("source") or {}
    required = ("url", "revision", "sha256", "license")
    resolved = lock.get("status") == "resolved" and all(source.get(k) for k in required)
    return {"resolved": resolved, "source": source, "lock_schema_version": lock.get("schema_version")}


@app.get("/health")
def health() -> dict[str, Any]:
    status = lock_status()
    return {
        "status": "ok",
        "kpml_source_locked": status["resolved"],
        "runtime": "hosted-kpml-sandbox",
    }


@app.get("/metadata")
def metadata() -> dict[str, Any]:
    return {
        "manifest": read_yaml(MANIFEST_PATH),
        "source_lock": lock_status(),
        "results_root": str(RESULTS_ROOT),
    }


@app.post("/generate")
def generate(request: GenerationRequest) -> dict[str, Any]:
    status = lock_status()
    request_id = request.request_id or str(uuid.uuid4())

    if not status["resolved"]:
        raise HTTPException(
            status_code=503,
            detail={
                "request_id": request_id,
                "status": "blocked",
                "reason": (
                    "KPML source lock is unresolved. Pin URL, revision, SHA-256, "
                    "license, loader entrypoint, grammar root, and generation "
                    "entrypoint before enabling realization."
                ),
                "source_lock": status,
            },
        )

    raise HTTPException(
        status_code=501,
        detail={
            "request_id": request_id,
            "status": "not_implemented",
            "reason": (
                "KPML source is locked, but the Lisp loader and generation bridge "
                "have not yet been committed."
            ),
            "timestamp_utc": datetime.now(timezone.utc).isoformat(),
        },
    )


@app.post("/record-request")
def record_request(request: GenerationRequest) -> dict[str, Any]:
    RESULTS_ROOT.mkdir(parents=True, exist_ok=True)
    request_id = request.request_id or str(uuid.uuid4())
    payload = {
        "request_id": request_id,
        "received_at_utc": datetime.now(timezone.utc).isoformat(),
        "meaning_matrix": request.meaning_matrix,
        "runtime_metadata": {"source_lock": lock_status()},
    }
    output = RESULTS_ROOT / f"{request_id}.json"
    output.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    return {"request_id": request_id, "recorded": str(output)}
