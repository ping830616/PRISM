#!/usr/bin/env python3
"""Compare a valid nominal/anomalous PRISM smoke pair."""

from __future__ import annotations

import argparse
import json
import statistics
from pathlib import Path
from typing import Any


METRICS = {
    "host_cpu_percent": ("host", "cpu_percent"),
    "host_cpu_utilization_derived_percent": (
        "host",
        "cpu_utilization_derived_percent",
    ),
    "cpu_power_w": ("enriched", "cpu_power"),
    "system_power_w": ("enriched", "sys_power"),
    "cpu_temperature_c": ("enriched", "temp", "cpu_temp_avg"),
}


def nested(record: dict[str, Any], path: tuple[str, ...]) -> float | None:
    value: Any = record
    for key in path:
        if not isinstance(value, dict) or key not in value:
            return None
        value = value[key]
    return float(value) if isinstance(value, (int, float)) else None


def rows(run_dir: Path) -> list[dict[str, Any]]:
    validation = json.loads((run_dir / "validation.json").read_text())
    if not validation.get("valid"):
        raise ValueError(f"run is not valid: {run_dir}")
    return [
        json.loads(line)
        for line in (run_dir / "telemetry.jsonl").read_text().splitlines()
        if line.strip()
    ]


def medians(records: list[dict[str, Any]]) -> dict[str, float | None]:
    result: dict[str, float | None] = {}
    for name, path in METRICS.items():
        values = [value for row in records if (value := nested(row, path)) is not None]
        result[name] = statistics.median(values) if values else None
    return result


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("nominal_run", type=Path)
    parser.add_argument("anomalous_run", type=Path)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()

    nominal = rows(args.nominal_run)
    anomalous = rows(args.anomalous_run)
    events = [
        json.loads(line)
        for line in (args.anomalous_run / "events.jsonl").read_text().splitlines()
        if line.strip()
    ]
    onset_events = [event for event in events if event.get("event") == "stressor_started"]
    if len(onset_events) != 1:
        raise ValueError("anomalous run must contain exactly one stressor_started event")
    onset = float(onset_events[0]["t_rel_seconds"])
    before = [row for row in anomalous if float(row["t_rel_seconds"]) < onset]
    after = [row for row in anomalous if float(row["t_rel_seconds"]) >= onset]

    summary = {
        "nominal_run": args.nominal_run.name,
        "anomalous_run": args.anomalous_run.name,
        "stressor_onset_seconds": onset,
        "sample_counts": {
            "nominal": len(nominal),
            "anomalous_pre_onset": len(before),
            "anomalous_post_onset": len(after),
        },
        "nominal_medians": medians(nominal),
        "anomalous_pre_onset_medians": medians(before),
        "anomalous_post_onset_medians": medians(after),
    }
    text = json.dumps(summary, indent=2, sort_keys=True) + "\n"
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(text, encoding="utf-8")
    print(text, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
