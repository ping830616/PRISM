#!/usr/bin/env python3
"""Summarize immutable plan coverage and local collection progress."""

from __future__ import annotations

import argparse
import csv
from collections import Counter, defaultdict
from pathlib import Path


def main() -> int:
    root = Path(__file__).resolve().parents[1]
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--progress",
        type=Path,
        default=root / "data/collection-progress.csv",
    )
    parser.add_argument(
        "--plan",
        type=Path,
        default=root / "data/collection-plan.csv",
    )
    args = parser.parse_args()
    source = args.progress if args.progress.exists() else args.plan
    with source.open(newline="", encoding="utf-8") as stream:
        rows = list(csv.DictReader(stream))

    by_platform: dict[str, Counter[str]] = defaultdict(Counter)
    benign_hours: dict[str, float] = defaultdict(float)
    for row in rows:
        by_platform[row["platform_id"]][row["status"]] += 1
        if row["status"] == "valid" and row["scenario"] == "NOMINAL":
            benign_hours[row["platform_id"]] += float(row["benign_hours"] or 0)

    print(f"Collection tracker: {source}")
    for platform_id in sorted(by_platform):
        statuses = ", ".join(
            f"{name}={count}" for name, count in sorted(by_platform[platform_id].items())
        )
        print(
            f"{platform_id}: {statuses}; valid benign hours={benign_hours[platform_id]:.2f}"
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
