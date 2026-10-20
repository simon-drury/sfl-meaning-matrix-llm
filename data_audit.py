"""Audit of the empirical 9D meaning-state data.

Reads data/empirical_trajectories.jsonl and reports what the training
pipeline would actually see: record count, coordinate variation,
zero-delta steps, and the no-change baseline MSE that any trained model
must beat.

Run: python data_audit.py [--data data/empirical_trajectories.jsonl]

Coordinate order: metafunction-major rows (ideational, interpersonal,
textual; columns field, tenor, mode). The register-major layout is the
alternative configuration; see the research note on configuration choice.
RESEARCH-LOG.md, entries 2026-10-20, holds the versioning and debug
report, the coordinate order contract and the configuration research
note.
"""
import argparse
import json
from pathlib import Path

import numpy as np


def load_vectors(path):
    vectors = []
    steps = []
    with Path(path).open() as handle:
        for line in handle:
            line = line.strip()
            if not line:
                continue
            item = json.loads(line)
            if isinstance(item, dict) and "vector_9d" in item:
                vectors.append([float(x) for x in item["vector_9d"]])
                steps.append(item.get("step"))
            elif isinstance(item, list) and len(item) == 9:
                vectors.append([float(x) for x in item])
    return np.asarray(vectors, dtype=np.float32), steps


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--data", default="data/empirical_trajectories.jsonl")
    args = parser.parse_args()

    vectors, steps = load_vectors(args.data)
    n = vectors.shape[0]
    deltas = np.diff(vectors, axis=0)

    print(f"file: {args.data}")
    print(f"records: {n}")
    print(f"state dimension: {vectors.shape[1]}")
    print(f"blank-line/document breaks: file read as one uninterrupted block")
    if steps and len(steps) > 1:
        print(f"step ids: {steps[0]} .. {steps[-1]}")

    print(f"\nper-coordinate summary (9 coordinates, metafunction-major rows):")
    for k in range(vectors.shape[1]):
        col = vectors[:, k]
        print(f"  c{k}: min={col.min():.4f} max={col.max():.4f} "
              f"std={col.std():.4f} distinct={len(np.unique(col))}")

    zero_steps = int((np.abs(deltas).sum(axis=1) == 0).sum())
    print(f"\nzero-delta steps (no meaning change): {zero_steps} of {len(deltas)}")

    mse_nochange = float((deltas ** 2).mean())
    print(f"no-change baseline MSE: {mse_nochange:.6f}")
    print("(any trained next-state/next-delta model must be compared against this)")


if __name__ == "__main__":
    main()
