#!/usr/bin/env python3
"""Validate the PRISM experiment contract before data collection."""

from __future__ import annotations

import argparse
from datetime import date
from pathlib import Path
import tomllib


REQUIRED_TOP_LEVEL = {
    "study",
    "platforms",
    "matrix",
    "collection",
    "splits",
    "gates",
    "long_benign",
}

EXTENSION_REQUIRED_SCENARIOS = {
    "NOMINAL",
    "ATOMIC",
    "BRANCH",
    "CACHE",
    "MEMBW",
    "TLB",
    "CONTROLLED_CRASH",
    "TELEMETRY_INTERRUPTION",
}
EXTENSION_TARGETED_SCENARIOS = {
    "THERMAL_SHIFT",
    "POWER_SHIFT",
    "DEGRADATION_PROXY",
}


def validate(config: dict) -> list[str]:
    errors: list[str] = []
    missing = sorted(REQUIRED_TOP_LEVEL - set(config))
    if missing:
        errors.append(f"missing top-level keys: {', '.join(missing)}")

    required_platforms = [
        platform for platform in config.get("platforms", []) if platform.get("required")
    ]
    if len(required_platforms) < 2:
        errors.append("at least two platforms must be required")

    required_ids = [platform.get("id") for platform in required_platforms]
    if len(required_ids) != len(set(required_ids)):
        errors.append("required platform IDs must be unique")

    repetitions = config.get("collection", {}).get(
        "minimum_independent_repetitions", 0
    )
    if repetitions < 3:
        errors.append("minimum independent repetitions must be at least 3")

    matrix = config.get("matrix", {})
    required_scenarios = set(matrix.get("required_scenarios", []))
    missing_required = sorted(EXTENSION_REQUIRED_SCENARIOS - required_scenarios)
    if missing_required:
        errors.append(
            "required scenarios do not cover the extension: "
            + ", ".join(missing_required)
        )
    targeted_scenarios = set(matrix.get("targeted_scenarios", []))
    missing_targeted = sorted(EXTENSION_TARGETED_SCENARIOS - targeted_scenarios)
    if missing_targeted:
        errors.append(
            "targeted scenarios do not cover the extension: "
            + ", ".join(missing_targeted)
        )
    if len(matrix.get("targeted_scenario_workloads", [])) < 2:
        errors.append("targeted extension scenarios require at least two workloads")

    collection = config.get("collection", {})
    if collection.get("target_run_duration_seconds", 0) < 720:
        errors.append("production matrix runs must be at least 720 seconds")
    if collection.get("target_benign_hours_per_required_platform", 0) < 12:
        errors.append("benign target must be at least 12 hours per platform")

    long_benign = config.get("long_benign", {})
    if not long_benign.get("required"):
        errors.append("long-benign collection must be required")
    long_workloads = long_benign.get("workloads", [])
    sessions = long_benign.get("sessions_per_workload", 0)
    session_seconds = long_benign.get("session_duration_seconds", 0)
    matrix_benign_hours = (
        len(matrix.get("workloads", []))
        * repetitions
        * collection.get("target_run_duration_seconds", 0)
        / 3600
    )
    supplement_hours = len(long_workloads) * sessions * session_seconds / 3600
    if matrix_benign_hours + supplement_hours < collection.get(
        "target_benign_hours_per_required_platform", 0
    ):
        errors.append(
            "matrix nominal runs plus long-benign sessions do not meet the "
            "per-platform benign-hour target"
        )

    if config.get("splits", {}).get("unit") != "run_id":
        errors.append("split unit must be run_id")
    if not config.get("splits", {}).get("forbid_window_level_split"):
        errors.append("window-level splitting must be forbidden")

    fractions = [
        config.get("splits", {}).get("calibration_fraction", 0),
        config.get("splits", {}).get("development_fraction", 0),
        config.get("splits", {}).get("locked_test_fraction", 0),
    ]
    if abs(sum(fractions) - 1.0) > 1e-9:
        errors.append("split fractions must sum to 1.0")

    gate_dates: list[date] = []
    for gate_name, raw_date in config.get("gates", {}).items():
        try:
            gate_dates.append(date.fromisoformat(str(raw_date)))
        except ValueError:
            errors.append(f"gate {gate_name} has invalid ISO date: {raw_date}")
    if gate_dates != sorted(gate_dates):
        errors.append("gate dates must be chronological")

    return errors


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("config", type=Path)
    args = parser.parse_args()

    with args.config.open("rb") as config_file:
        config = tomllib.load(config_file)
    errors = validate(config)
    if errors:
        for error in errors:
            print(f"ERROR: {error}")
        return 1

    required_platforms = [
        platform["id"] for platform in config["platforms"] if platform["required"]
    ]
    print("PRISM experiment contract is valid")
    print(f"required platforms: {', '.join(required_platforms)}")
    print(
        "minimum repetitions: "
        f"{config['collection']['minimum_independent_repetitions']}"
    )
    print(
        "extension scenarios: "
        f"{len(config['matrix']['required_scenarios'])} required + "
        f"{len(config['matrix']['targeted_scenarios'])} targeted"
    )
    matrix_benign_hours = (
        len(config["matrix"]["workloads"])
        * config["collection"]["minimum_independent_repetitions"]
        * config["collection"]["target_run_duration_seconds"]
        / 3600
    )
    long_benign = config["long_benign"]
    supplement_hours = (
        len(long_benign["workloads"])
        * long_benign["sessions_per_workload"]
        * long_benign["session_duration_seconds"]
        / 3600
    )
    print(
        "benign coverage per platform: "
        f"{matrix_benign_hours:.1f} h matrix + "
        f"{supplement_hours:.1f} h supplement = "
        f"{matrix_benign_hours + supplement_hours:.1f} h"
    )
    print(f"submission gate: {config['gates']['submission']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
