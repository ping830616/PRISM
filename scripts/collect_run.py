#!/usr/bin/env python3
"""Collect one synchronized PRISM run."""

from __future__ import annotations

import argparse
from pathlib import Path

from prism_slm.collection import CollectionRequest, collect


def main() -> int:
    root = Path(__file__).resolve().parents[1]
    parser = argparse.ArgumentParser()
    parser.add_argument("--platform-id", required=True)
    parser.add_argument("--workload", required=True)
    parser.add_argument("--scenario", required=True)
    parser.add_argument("--repetition", type=int, required=True)
    parser.add_argument(
        "--split",
        choices=("calibration", "development", "locked_test", "smoke"),
        default="smoke",
    )
    parser.add_argument("--duration-seconds", type=int, default=30)
    parser.add_argument("--sampling-hz", type=float, default=5.0)
    parser.add_argument("--warmup-seconds", type=float, default=5.0)
    parser.add_argument(
        "--interruption-seconds",
        type=float,
        default=10.0,
        help="Masked enriched-telemetry interval for TELEMETRY_INTERRUPTION",
    )
    parser.add_argument("--purpose", choices=("smoke", "production"), default="smoke")
    parser.add_argument("--profile", choices=("portable", "enriched"), default="enriched")
    parser.add_argument("--run-id")
    parser.add_argument("--macmon-executable", default="macmon")
    parser.add_argument("--enable-xctrace", action="store_true")
    parser.add_argument("--xctrace-template", default="Time Profiler")
    parser.add_argument("--output-root", type=Path, default=root / "data/raw")
    args = parser.parse_args()

    run_dir = collect(
        CollectionRequest(
            platform_id=args.platform_id,
            workload=args.workload,
            scenario=args.scenario,
            repetition=args.repetition,
            split=args.split,
            duration_seconds=args.duration_seconds,
            sampling_hz=args.sampling_hz,
            warmup_seconds=args.warmup_seconds,
            interruption_seconds=args.interruption_seconds,
            purpose=args.purpose,
            profile=args.profile,
            output_root=args.output_root,
            run_id=args.run_id,
            macmon_executable=args.macmon_executable,
            enable_xctrace=args.enable_xctrace,
            xctrace_template=args.xctrace_template,
        )
    )
    print(f"Valid PRISM run: {run_dir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
