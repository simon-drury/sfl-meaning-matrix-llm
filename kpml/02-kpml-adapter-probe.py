#!/usr/bin/env python3
"""Deterministic KPML adapter probe for the SFL Meaning Matrix sandbox.

The probe makes the boundary between a meaning-matrix request and an external
KPML realizer explicit. It is intentionally transport-agnostic: dry-run mode
validates serialization without KPML; command mode delegates to a local bridge.
"""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
import time
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any


REQUIRED_CONTEXT_KEYS = ("field", "tenor", "mode")
REQUIRED_METAFUNCTION_KEYS = ("ideational", "interpersonal", "textual")


@dataclass(frozen=True)
class ProbeResult:
    request: dict[str, Any]
    serialized_request: str
    mode: str
    command: list[str]
    returncode: int | None
    stdout: str
    stderr: str
    elapsed_ms: int
    environment: dict[str, str | None]


def load_request(path: Path) -> dict[str, Any]:
    with path.open(encoding="utf-8") as handle:
        request = json.load(handle)
    if not isinstance(request, dict):
        raise ValueError("KPML request must be a JSON object")
    return request


def validate_request(request: dict[str, Any]) -> None:
    missing = [key for key in ("context", "metafunctions") if key not in request]
    if missing:
        raise ValueError(f"Missing top-level key(s): {', '.join(missing)}")

    context = request["context"]
    metafunctions = request["metafunctions"]
    if not isinstance(context, dict) or not isinstance(metafunctions, dict):
        raise ValueError("context and metafunctions must be objects")

    missing_context = [key for key in REQUIRED_CONTEXT_KEYS if key not in context]
    missing_metafunctions = [key for key in REQUIRED_METAFUNCTION_KEYS if key not in metafunctions]
    if missing_context or missing_metafunctions:
        messages = []
        if missing_context:
            messages.append(f"context: {', '.join(missing_context)}")
        if missing_metafunctions:
            messages.append(f"metafunctions: {', '.join(missing_metafunctions)}")
        raise ValueError("Missing required keys — " + "; ".join(messages))


def serialize_request(request: dict[str, Any]) -> str:
    """Canonical JSON is the first inspectable KPML-boundary representation."""
    return json.dumps(request, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def run_probe(request: dict[str, Any], command_template: str | None) -> ProbeResult:
    serialized = serialize_request(request)
    started = time.perf_counter()
    environment = {
        "KPML_COMMAND": os.getenv("KPML_COMMAND"),
        "PYTHON_VERSION": sys.version.split()[0],
    }

    if not command_template:
        elapsed_ms = round((time.perf_counter() - started) * 1000)
        return ProbeResult(
            request=request,
            serialized_request=serialized,
            mode="dry-run",
            command=[],
            returncode=None,
            stdout="",
            stderr="",
            elapsed_ms=elapsed_ms,
            environment=environment,
        )

    command = command_template.format(payload=serialized)
    completed = subprocess.run(
        command,
        shell=True,
        text=True,
        capture_output=True,
        check=False,
    )
    elapsed_ms = round((time.perf_counter() - started) * 1000)
    return ProbeResult(
        request=request,
        serialized_request=serialized,
        mode="command",
        command=[command],
        returncode=completed.returncode,
        stdout=completed.stdout,
        stderr=completed.stderr,
        elapsed_ms=elapsed_ms,
        environment=environment,
    )


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("request", type=Path, help="JSON file conforming to the sandbox input contract")
    parser.add_argument("--command", default=os.getenv("KPML_COMMAND"), help="Local bridge command; use {payload} for canonical JSON")
    parser.add_argument("--output", type=Path, help="Write structured probe result to this JSON file")
    args = parser.parse_args()

    try:
        request = load_request(args.request)
        validate_request(request)
        result = run_probe(request, args.command)
    except (OSError, ValueError, json.JSONDecodeError) as error:
        print(f"KPML probe failed: {error}", file=sys.stderr)
        return 2

    payload = json.dumps(asdict(result), ensure_ascii=False, indent=2, sort_keys=True)
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(payload + "\n", encoding="utf-8")
    print(payload)
    return 0 if result.returncode in (None, 0) else result.returncode


if __name__ == "__main__":
    raise SystemExit(main())
