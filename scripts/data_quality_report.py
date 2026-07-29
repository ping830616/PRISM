#!/usr/bin/env python3
"""Aggregate per-run validation into a platform data-quality report."""

from __future__ import annotations

import argparse
import json
import statistics
from collections import Counter, defaultdict
from pathlib import Path


def main() -> int:
    root = Path(__file__).resolve().parents[1]
    parser = argparse.ArgumentParser()
    parser.add_argument("--platform-id", required=True)
    parser.add_argument("--raw-root", type=Path, default=root / "data/raw")
    parser.add_argument(
        "--output",
        type=Path,
        default=None,
    )
    parser.add_argument("--include-smoke", action="store_true")
    args = parser.parse_args()

    runs: list[dict] = []
    for validation_path in sorted(
        (args.raw_root / args.platform_id).glob("*/*/validation.json")
    ):
        run_dir = validation_path.parent
        collection_path = run_dir / "collection.json"
        if not collection_path.is_file():
            continue
        collection = json.loads(collection_path.read_text())
        if not args.include_smoke and collection.get("purpose") != "production":
            continue
        validation = json.loads(validation_path.read_text())
        runs.append(
            {
                "run_id": collection.get("run_id"),
                "scenario": collection.get("scenario"),
                "workload": collection.get("workload"),
                "purpose": collection.get("purpose"),
                "valid": validation.get("valid", False),
                "duration_observed_seconds": validation.get(
                    "duration_observed_seconds",
                    0,
                ),
                "warnings": validation.get("warnings", []),
                "failures": validation.get("failures", []),
                "quality": validation.get("quality", {}),
            }
        )

    statuses = Counter("valid" if run["valid"] else "invalid" for run in runs)
    scenario_counts: dict[str, Counter[str]] = defaultdict(Counter)
    channel_fractions: dict[str, list[float]] = defaultdict(list)
    warning_counts: Counter[str] = Counter()
    failure_counts: Counter[str] = Counter()
    benign_hours = 0.0
    for run in runs:
        status = "valid" if run["valid"] else "invalid"
        scenario_counts[str(run["scenario"])][status] += 1
        if run["valid"] and run["scenario"] == "NOMINAL":
            benign_hours += float(run["duration_observed_seconds"]) / 3600
        for warning in run["warnings"]:
            warning_counts[str(warning)] += 1
        for failure in run["failures"]:
            failure_counts[str(failure)] += 1
        for name, metrics in run["quality"].get("critical_channels", {}).items():
            channel_fractions[name].append(float(metrics["non_null_fraction"]))

    report = {
        "platform_id": args.platform_id,
        "run_count": len(runs),
        "statuses": dict(sorted(statuses.items())),
        "valid_benign_hours": benign_hours,
        "scenario_counts": {
            name: dict(sorted(counts.items()))
            for name, counts in sorted(scenario_counts.items())
        },
        "critical_channel_availability": {
            name: {
                "minimum": min(values),
                "median": statistics.median(values),
                "maximum": max(values),
                "run_count": len(values),
            }
            for name, values in sorted(channel_fractions.items())
            if values
        },
        "warning_counts": dict(sorted(warning_counts.items())),
        "failure_counts": dict(sorted(failure_counts.items())),
    }
    destination = args.output or (
        root / "artifacts/data-quality" / f"{args.platform_id.lower()}.json"
    )
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n")
    print(json.dumps(report, indent=2, sort_keys=True))
    print(f"Quality report: {destination}")
    return 0 if statuses.get("invalid", 0) == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
