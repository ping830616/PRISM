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
    print(f"submission gate: {config['gates']['submission']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
