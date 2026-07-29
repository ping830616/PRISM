#!/usr/bin/env python3
"""Preview or execute the next predeclared PRISM production run."""

from __future__ import annotations

import argparse
import csv
import platform
import shlex
import shutil
from pathlib import Path

from prism_slm.collection import CollectionRequest, collect, update_collection_plan


def _default_platform() -> str:
    system = platform.system()
    if system == "Darwin":
        return "M2_MACOS"
    if system == "Linux":
        return "EPYC_LINUX"
    raise SystemExit(f"Unsupported collection operating system: {system}")


def _read_rows(path: Path) -> tuple[list[str], list[dict[str, str]]]:
    with path.open(newline="", encoding="utf-8") as stream:
        reader = csv.DictReader(stream)
        return list(reader.fieldnames or []), list(reader)


def _ensure_progress(plan_path: Path, progress_path: Path) -> list[dict[str, str]]:
    _, plan_rows = _read_rows(plan_path)
    if not progress_path.exists():
        progress_path.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(plan_path, progress_path)
    _, progress_rows = _read_rows(progress_path)
    if [row["run_id"] for row in progress_rows] != [
        row["run_id"] for row in plan_rows
    ]:
        raise SystemExit(
            "Collection progress does not match the immutable plan. Preserve the "
            "progress file and reconcile it manually; do not overwrite collected state."
        )
    return progress_rows


def _matches(row: dict[str, str], args: argparse.Namespace) -> bool:
    if row["platform_id"] != args.platform_id:
        return False
    if row["status"] != "planned":
        return False
    for field in ("run_id", "run_kind", "workload", "scenario", "planned_split"):
        expected = getattr(args, field)
        if expected and row[field].upper() != expected.upper():
            return False
    if row["planned_split"] == "locked_test" and not args.unlock_locked_test:
        return False
    return True


def _command(row: dict[str, str]) -> list[str]:
    command = [
        "python3",
        "scripts/collect_run.py",
        "--platform-id",
        row["platform_id"],
        "--workload",
        row["workload"],
        "--scenario",
        row["scenario"],
        "--repetition",
        row["repetition"],
        "--split",
        row["planned_split"],
        "--purpose",
        row["purpose"],
        "--profile",
        row["profile"],
        "--run-id",
        row["run_id"],
        "--duration-seconds",
        row["duration_seconds"],
        "--sampling-hz",
        row["sampling_hz"],
        "--warmup-seconds",
        row["warmup_seconds"],
    ]
    if float(row["interruption_seconds"]) > 0:
        command.extend(["--interruption-seconds", row["interruption_seconds"]])
    return command


def main() -> int:
    root = Path(__file__).resolve().parents[1]
    parser = argparse.ArgumentParser()
    parser.add_argument("--platform-id", default=_default_platform())
    parser.add_argument("--run-id")
    parser.add_argument("--run-kind")
    parser.add_argument("--workload")
    parser.add_argument("--scenario")
    parser.add_argument("--planned-split")
    parser.add_argument(
        "--plan",
        type=Path,
        default=root / "data/collection-plan.csv",
    )
    parser.add_argument(
        "--progress",
        type=Path,
        default=root / "data/collection-progress.csv",
    )
    parser.add_argument("--output-root", type=Path, default=root / "data/raw")
    parser.add_argument(
        "--execute",
        action="store_true",
        help="Run the selected production cell; without this flag only preview it",
    )
    parser.add_argument(
        "--unlock-locked-test",
        action="store_true",
        help="Allow a predeclared locked-test row after the method is frozen",
    )
    args = parser.parse_args()

    rows = _ensure_progress(args.plan, args.progress)
    selected = next((row for row in rows if _matches(row, args)), None)
    if selected is None:
        raise SystemExit(
            "No matching planned run is available. Locked-test rows are hidden "
            "unless --unlock-locked-test is supplied."
        )

    print("Selected predeclared run:")
    for field in (
        "run_id",
        "platform_id",
        "run_kind",
        "workload",
        "scenario",
        "planned_split",
        "duration_seconds",
        "sampling_hz",
        "warmup_seconds",
        "interruption_seconds",
    ):
        print(f"  {field}: {selected[field]}")
    print("\nEquivalent low-level command (does not update progress):")
    print(shlex.join(_command(selected)))
    if not args.execute:
        print("\nPreview only. Re-run with --execute after reviewing the selection.")
        return 0

    run_dir = collect(
        CollectionRequest(
            platform_id=selected["platform_id"],
            workload=selected["workload"],
            scenario=selected["scenario"],
            repetition=int(selected["repetition"]),
            split=selected["planned_split"],
            duration_seconds=int(selected["duration_seconds"]),
            sampling_hz=float(selected["sampling_hz"]),
            warmup_seconds=float(selected["warmup_seconds"]),
            interruption_seconds=float(selected["interruption_seconds"]),
            purpose=selected["purpose"],
            profile=selected["profile"],
            output_root=args.output_root,
            run_id=selected["run_id"],
        )
    )
    update_collection_plan(args.progress, run_dir)
    print(f"Valid PRISM run: {run_dir}")
    print(f"Progress updated: {args.progress}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
