#!/usr/bin/env python3
"""Gate production collection on a clean revision and current smoke evidence."""

from __future__ import annotations

import argparse
import json
import platform
import shutil
import subprocess
import sys
from pathlib import Path

from prism_slm.collection import repository_state


def main() -> int:
    root = Path(__file__).resolve().parents[1]
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--platform-id",
        choices=("M2_MACOS", "EPYC_LINUX"),
        required=True,
    )
    parser.add_argument("--raw-root", type=Path, default=root / "data/raw")
    args = parser.parse_args()

    failures: list[str] = []
    expected_system = {"M2_MACOS": "Darwin", "EPYC_LINUX": "Linux"}[
        args.platform_id
    ]
    if platform.system() != expected_system:
        failures.append(
            f"{args.platform_id} requires {expected_system}, not {platform.system()}"
        )

    state = repository_state()
    if state.get("git_dirty") is not False:
        failures.append("Git checkout is not clean")
    commit = state.get("git_commit")

    preflight = subprocess.run(
        [
            sys.executable,
            str(root / "scripts/preflight.py"),
            str(root / "configs/experiment-matrix.toml"),
        ],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        check=False,
    )
    if preflight.returncode != 0:
        failures.append("experiment preflight failed")

    if args.platform_id == "M2_MACOS" and shutil.which("macmon") is None:
        failures.append("macmon is not installed or not on PATH")

    current_smoke: dict[str, Path] = {}
    platform_root = args.raw_root / args.platform_id
    for collection_path in sorted(
        platform_root.glob("*/*/collection.json"),
        reverse=True,
    ):
        run_dir = collection_path.parent
        validation_path = run_dir / "validation.json"
        if not validation_path.is_file():
            continue
        collection = json.loads(collection_path.read_text())
        validation = json.loads(validation_path.read_text())
        scenario = str(collection.get("scenario", ""))
        if (
            collection.get("purpose") == "smoke"
            and collection.get("platform_id") == args.platform_id
            and collection.get("profile") == "enriched"
            and collection.get("software", {}).get("git_commit") == commit
            and collection.get("software", {}).get("git_dirty") is False
            and validation.get("valid") is True
            and scenario in {"NOMINAL", "ATOMIC"}
            and scenario not in current_smoke
        ):
            current_smoke[scenario] = run_dir

    for scenario in ("NOMINAL", "ATOMIC"):
        if scenario not in current_smoke:
            failures.append(
                f"no valid clean-revision {scenario} smoke run for commit {commit}"
            )

    print(preflight.stdout.rstrip())
    print(f"repository commit: {commit}")
    for scenario, run_dir in sorted(current_smoke.items()):
        print(f"{scenario.lower()} smoke: {run_dir}")
    if failures:
        for failure in failures:
            print(f"ERROR: {failure}")
        return 1
    print(f"{args.platform_id} is ready for predeclared production collection")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
