#!/usr/bin/env python3
"""Import the frozen DICE M2 Pro baseline without bloating PRISM Git history."""

from __future__ import annotations

import argparse
import hashlib
import json
import shutil
import subprocess
from datetime import date
from pathlib import Path


SOURCE_REL = Path("data generation/dataset/ITC_M2Pro_DATA")
RAW_ITEMS = ("tier0", "tier1_alt", "tier2", "no_nan_report.json")
SUMMARY_FILES = (
    "RESULTS_SUMMARY.md",
    "case_inventory.csv",
    "case_predictions.csv",
    "config_runtime_summary.csv",
    "overall_metrics.csv",
    "run_context.json",
    "sequential_metrics.csv",
)


def git_value(repo: Path, *args: str) -> str:
    return subprocess.check_output(
        ("git", "-C", str(repo), *args), text=True
    ).strip()


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def copy_item(source: Path, destination: Path) -> None:
    if source.is_dir():
        shutil.copytree(source, destination, dirs_exist_ok=True, copy_function=shutil.copy2)
    else:
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, destination)


def copy_summaries(source_root: Path, destination_root: Path) -> list[str]:
    copied: list[str] = []
    profiles = {
        "mixed": ("results_dice_full", "results_dice_full_holdout"),
        "full": ("results_dice_full_full", "results_dice_full_full_holdout"),
    }
    for profile, (headline_dir, holdout_dir) in profiles.items():
        target = destination_root / profile
        target.mkdir(parents=True, exist_ok=True)
        for filename in SUMMARY_FILES:
            source = source_root / headline_dir / filename
            if not source.is_file():
                raise FileNotFoundError(source)
            shutil.copy2(source, target / filename)
            copied.append(str((target / filename).relative_to(destination_root)))
        holdout = source_root / holdout_dir / "holdout_robustness_summary.csv"
        if not holdout.is_file():
            raise FileNotFoundError(holdout)
        shutil.copy2(holdout, target / "holdout_robustness_summary.csv")
        copied.append(str((target / "holdout_robustness_summary.csv").relative_to(destination_root)))
    return copied


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--dice-root",
        type=Path,
        default=Path("../DICE"),
        help="Path to the local DICE checkout (default: ../DICE)",
    )
    parser.add_argument(
        "--prism-root",
        type=Path,
        default=Path(__file__).resolve().parents[1],
        help="PRISM repository root",
    )
    args = parser.parse_args()

    dice_root = args.dice_root.resolve()
    prism_root = args.prism_root.resolve()
    source_root = dice_root / SOURCE_REL
    payload_root = prism_root / "data/external/dice_m2pro_itc/payload"
    metadata_root = payload_root.parent
    baseline_root = prism_root / "data/baselines/dice_m2pro_itc"

    if not source_root.is_dir():
        raise SystemExit(f"DICE dataset not found: {source_root}")

    for item in RAW_ITEMS:
        source = source_root / item
        if not source.exists():
            raise SystemExit(f"Required DICE baseline item missing: {source}")
        copy_item(source, payload_root / item)

    copied_summaries = copy_summaries(source_root, baseline_root)

    files = sorted(path for path in payload_root.rglob("*") if path.is_file())
    checksum_lines = [
        f"{sha256(path)}  {path.relative_to(payload_root).as_posix()}" for path in files
    ]
    (metadata_root / "local-files.sha256").write_text(
        "\n".join(checksum_lines) + "\n", encoding="utf-8"
    )

    total_bytes = sum(path.stat().st_size for path in files)
    source_record = {
        "dataset_id": "dice_m2pro_itc",
        "role": "historical_baseline_only",
        "source_remote": git_value(dice_root, "remote", "get-url", "origin"),
        "source_commit": git_value(dice_root, "rev-parse", "HEAD"),
        "source_path": SOURCE_REL.as_posix(),
        "import_date": date.today().isoformat(),
        "payload_file_count": len(files),
        "payload_bytes": total_bytes,
        "payload_sha256_manifest": "local-files.sha256",
        "copied_summary_files": copied_summaries,
        "limitations": [
            "Apple M2 Pro/macOS only",
            "24 workload-scenario cases",
            "one recorded execution per case",
            "not independent PRISM replication",
        ],
    }
    (metadata_root / "source.json").write_text(
        json.dumps(source_record, indent=2) + "\n", encoding="utf-8"
    )

    print(f"Imported {len(files)} payload files ({total_bytes / 1024**2:.1f} MiB)")
    print(f"Source commit: {source_record['source_commit']}")
    print(f"Raw payload: {payload_root} (Git-ignored)")
    print(f"Tracked summaries: {baseline_root}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
