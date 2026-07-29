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
    "run_kind",
    "repetition",
    "planned_split",
    "purpose",
    "profile",
    "duration_seconds",
    "sampling_hz",
    "warmup_seconds",
    "interruption_seconds",
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


def _matrix_row(
    *,
    platform: str,
    workload: str,
    scenario: str,
    repetition: int,
    collection: dict,
    run_kind: str,
) -> dict[str, object]:
    run_id = (
        f"{platform.lower()}__{workload.lower()}__"
        f"{scenario.lower()}__r{repetition:02d}"
    )
    return {
        "run_id": run_id,
        "platform_id": platform,
        "workload": workload,
        "scenario": scenario,
        "run_kind": run_kind,
        "repetition": repetition,
        "planned_split": split_for(scenario, repetition),
        "purpose": "production",
        "profile": "enriched",
        "duration_seconds": collection["target_run_duration_seconds"],
        "sampling_hz": collection["sampling_hz"],
        "warmup_seconds": (
            0
            if scenario == "NOMINAL"
            else collection["anomaly_warmup_seconds"]
        ),
        "interruption_seconds": (
            collection["telemetry_interruption_seconds"]
            if scenario == "TELEMETRY_INTERRUPTION"
            else 0
        ),
        "status": "planned",
        "replacement_for": "",
        "start_utc": "",
        "end_utc": "",
        "valid_rows": "",
        "benign_hours": "",
        "exclusion_reason": "",
        "notes": "",
    }


def build_rows(config: dict, repetitions_override: int | None = None) -> list[dict[str, object]]:
    platforms = [
        item["id"] for item in config["platforms"] if item.get("required", False)
    ]
    matrix = config["matrix"]
    collection = config["collection"]
    workloads = matrix["workloads"]
    repetitions = repetitions_override or collection["minimum_independent_repetitions"]
    if repetitions < collection["minimum_independent_repetitions"]:
        raise ValueError("Repetitions cannot be below the declared minimum")

    rows: list[dict[str, object]] = []
    for platform in platforms:
        for workload in workloads:
            for scenario in matrix["required_scenarios"]:
                for repetition in range(1, repetitions + 1):
                    rows.append(
                        _matrix_row(
                            platform=platform,
                            workload=workload,
                            scenario=scenario,
                            repetition=repetition,
                            collection=collection,
                            run_kind="required_matrix",
                        )
                    )

        for workload in matrix["targeted_scenario_workloads"]:
            for scenario in matrix["targeted_scenarios"]:
                for repetition in range(1, repetitions + 1):
                    rows.append(
                        _matrix_row(
                            platform=platform,
                            workload=workload,
                            scenario=scenario,
                            repetition=repetition,
                            collection=collection,
                            run_kind="targeted_extension",
                        )
                    )

        long_benign = config["long_benign"]
        for workload in long_benign["workloads"]:
            for session in range(1, long_benign["sessions_per_workload"] + 1):
                rows.append(
                    {
                        "run_id": (
                            f"{platform.lower()}__{workload.lower()}__"
                            f"long_benign__s{session:02d}"
                        ),
                        "platform_id": platform,
                        "workload": workload,
                        "scenario": "NOMINAL",
                        "run_kind": "long_benign",
                        "repetition": session,
                        "planned_split": (
                            "development" if session == 1 else "locked_test"
                        ),
                        "purpose": "production",
                        "profile": "enriched",
                        "duration_seconds": long_benign["session_duration_seconds"],
                        "sampling_hz": long_benign["sampling_hz"],
                        "warmup_seconds": 0,
                        "interruption_seconds": 0,
                        "status": "planned",
                        "replacement_for": "",
                        "start_utc": "",
                        "end_utc": "",
                        "valid_rows": "",
                        "benign_hours": "",
                        "exclusion_reason": "",
                        "notes": "long-benign supplement toward 12 h/platform",
                    }
                )
    return rows


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
    parser.add_argument(
        "--overwrite",
        action="store_true",
        help="Replace an existing plan; never use after collection has started",
    )
    args = parser.parse_args()

    with args.config.open("rb") as stream:
        config = tomllib.load(stream)

    if args.output.exists() and not args.overwrite:
        raise SystemExit(
            f"Plan already exists: {args.output}. Pass --overwrite only before "
            "production collection begins."
        )
    try:
        rows = build_rows(config, args.repetitions)
    except ValueError as exc:
        raise SystemExit(str(exc)) from exc

    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open("w", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, fieldnames=FIELDS, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)

    seconds = sum(int(row["duration_seconds"]) for row in rows)
    kinds: dict[str, int] = {}
    for row in rows:
        key = str(row["run_kind"])
        kinds[key] = kinds.get(key, 0) + 1
    print(f"Wrote {len(rows)} planned runs to {args.output}")
    print(
        "Run kinds: "
        + ", ".join(f"{key}={value}" for key, value in sorted(kinds.items()))
    )
    print(f"Declared collection time: {seconds / 3600:.1f} machine-hours")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
