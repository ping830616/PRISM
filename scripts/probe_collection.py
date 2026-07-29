#!/usr/bin/env python3
"""Report collection capabilities without recording a research run."""

from __future__ import annotations

import json
import platform
import shutil
import subprocess
from pathlib import Path

from prism_slm.collection import LinuxSysfsSampler, sanitized_platform_snapshot


def command_status(command: list[str]) -> dict[str, object]:
    executable = shutil.which(command[0])
    if executable is None:
        return {"available": False, "executable": None}
    try:
        result = subprocess.run(
            command,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            timeout=20,
            check=False,
        )
        return {
            "available": result.returncode == 0,
            "executable": executable,
            "return_code": result.returncode,
            "first_output_line": (result.stdout or "").strip().splitlines()[:1],
        }
    except subprocess.TimeoutExpired:
        return {"available": False, "executable": executable, "error": "timeout"}


def main() -> int:
    root = Path(__file__).resolve().parents[1]
    system = platform.system()
    platform_id = "M2_MACOS" if system == "Darwin" else "EPYC_LINUX"
    result: dict[str, object] = {
        "platform": sanitized_platform_snapshot(platform_id),
        "python": command_status(["python3", "--version"]),
    }
    if system == "Darwin":
        result["macmon"] = command_status(["macmon", "pipe", "-s", "1", "-i", "200"])
        result["xctrace"] = command_status(["xcrun", "xctrace", "version"])
    elif system == "Linux":
        sysfs = LinuxSysfsSampler()
        result["perf"] = command_status(["perf", "--version"])
        result["sensors"] = command_status(["sensors", "--version"])
        result["linux_sysfs"] = {
            "sensor_channels": sysfs.metadata(),
            "frequency_channel_count": len(sysfs.frequency_paths),
        }
        paranoid = Path("/proc/sys/kernel/perf_event_paranoid")
        result["perf_event_paranoid"] = (
            paranoid.read_text().strip() if paranoid.is_file() else None
        )

    destination = root / "data/collection-probes" / f"{platform_id.lower()}.json"
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(json.dumps(result, indent=2, sort_keys=True))
    print(f"Probe saved locally: {destination}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
