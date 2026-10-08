#!/usr/bin/env python3
"""Resolve and verify a pinned KPML source during a remote runtime build."""

from __future__ import annotations

import argparse
import hashlib
import json
import pathlib
import shutil
import sys
import tarfile
import tempfile
import urllib.parse
import urllib.request

try:
    import yaml
except ImportError as exc:
    raise SystemExit("PyYAML is required: pip install pyyaml") from exc


REQUIRED = ("url", "revision", "sha256", "license")


def load_lock(path: pathlib.Path) -> dict:
    data = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    source = data.get("source") or {}
    missing = [name for name in REQUIRED if not source.get(name)]
    if data.get("status") != "resolved" or missing:
        detail = ", ".join(missing) if missing else "status=resolved"
        raise ValueError(
            "KPML source lock is unresolved. Set status: resolved and provide "
            f"source fields: {detail}."
        )
    parsed = urllib.parse.urlparse(source["url"])
    if parsed.scheme != "https":
        raise ValueError("KPML source URL must use https.")
    return data


def sha256_file(path: pathlib.Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def download(url: str, destination: pathlib.Path) -> None:
    request = urllib.request.Request(url, headers={"User-Agent": "kpml-sandbox/1"})
    with urllib.request.urlopen(request, timeout=90) as response, destination.open("wb") as out:
        shutil.copyfileobj(response, out)


def extract(archive: pathlib.Path, destination: pathlib.Path) -> None:
    with tarfile.open(archive, "r:*") as bundle:
        members = bundle.getmembers()
        root = destination.resolve()
        for member in members:
            target = (destination / member.name).resolve()
            if not target.is_relative_to(root):
                raise ValueError(f"Unsafe archive path: {member.name}")
        bundle.extractall(destination, members=members)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--lock", required=True, type=pathlib.Path)
    parser.add_argument("--destination", required=True, type=pathlib.Path)
    parser.add_argument("--provenance", required=True, type=pathlib.Path)
    args = parser.parse_args()

    lock = load_lock(args.lock)
    source = lock["source"]
    args.destination.mkdir(parents=True, exist_ok=True)
    args.provenance.parent.mkdir(parents=True, exist_ok=True)

    with tempfile.TemporaryDirectory() as tmpdir:
        archive = pathlib.Path(tmpdir) / "kpml-source.tar"
        download(source["url"], archive)
        actual = sha256_file(archive)
        expected = source["sha256"].lower()
        if actual.lower() != expected:
            raise ValueError(
                f"KPML checksum mismatch: expected {expected}, received {actual}."
            )
        extract(archive, args.destination)

    record = {
        "artifact": "kpml-runtime-source",
        "status": "verified",
        "url": source["url"],
        "revision": source["revision"],
        "sha256": actual,
        "license": source["license"],
        "destination": str(args.destination),
    }
    args.provenance.write_text(json.dumps(record, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(record))
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:
        print(f"KPML source resolution failed: {exc}", file=sys.stderr)
        raise SystemExit(2)
