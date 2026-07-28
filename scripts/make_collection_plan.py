#!/usr/bin/env python3
"""Generate the predeclared PRISM run-level collection tracker."""

from __future__ import annotations

import argparse
import csv
import tomllib
from pathlib import Path


FIELDS = (
    "run_id",
    "platform_id",
    "workload",
    "scenario",
    "repetition",
    "planned_split",
    "status",
    "replacement_for",
    "start_utc",
    "end_utc",
    "valid_rows",
    "benign_hours",
    "exclusion_reason",
    "notes",
)


def split_for(scenario: str, repetition: int) -> str:
    if repetition >= 3:
        return "locked_test"
    if scenario == "NOMINAL" and repetition == 1:
        return "calibration"
    return "development"


def main() -> int:
    root = Path(__file__).resolve().parents[1]
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--config",
        type=Path,
        default=root / "configs/experiment-matrix.toml",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=root / "data/collection-plan.csv",
    )
    parser.add_argument(
        "--repetitions",
        type=int,
        help="Override minimum repetitions from the experiment configuration",
    )
    args = parser.parse_args()

    with args.config.open("rb") as stream:
        config = tomllib.load(stream)

    platforms = [
        item["id"] for item in config["platforms"] if item.get("required", False)
    ]
    workloads = config["matrix"]["workloads"]
    scenarios = config["matrix"]["required_scenarios"]
    repetitions = args.repetitions or config["collection"][
        "minimum_independent_repetitions"
    ]
    if repetitions < config["collection"]["minimum_independent_repetitions"]:
        raise SystemExit("Repetitions cannot be below the declared minimum")

    rows: list[dict[str, object]] = []
    for platform in platforms:
        for workload in workloads:
            for scenario in scenarios:
                for repetition in range(1, repetitions + 1):
                    run_id = (
                        f"{platform.lower()}__{workload.lower()}__"
                        f"{scenario.lower()}__r{repetition:02d}"
                    )
                    rows.append(
                        {
                            "run_id": run_id,
                            "platform_id": platform,
                            "workload": workload,
                            "scenario": scenario,
                            "repetition": repetition,
                            "planned_split": split_for(scenario, repetition),
                            "status": "planned",
                            "replacement_for": "",
                            "start_utc": "",
                            "end_utc": "",
                            "valid_rows": "",
                            "benign_hours": "",
                            "exclusion_reason": "",
                            "notes": "",
                        }
                    )

    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open("w", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, fieldnames=FIELDS, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)

    seconds = len(rows) * config["collection"]["target_run_duration_seconds"]
    print(f"Wrote {len(rows)} planned runs to {args.output}")
    print(f"Declared collection time: {seconds / 3600:.1f} machine-hours")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
