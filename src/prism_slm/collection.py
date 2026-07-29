"""Synchronized, provenance-safe telemetry collection for PRISM."""

from __future__ import annotations

import csv
import hashlib
import json
import math
import os
import platform
import re
import shutil
import statistics
import subprocess
import sys
import threading
import time
import traceback
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable

import psutil

from .contracts import SemanticGroup
from .workload_harness import SCENARIOS, STRESSORS, WORKLOADS


QUALITY_CONTRACT = {
    "primary_channel_minimum_fraction": 0.95,
    "apple_temperature_minimum_fraction": 0.70,
    "apple_temperature_min_celsius": 15.0,
    "apple_temperature_max_celsius": 125.0,
    "maximum_quality_flag_fraction": 0.25,
}


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def utc_date() -> str:
    return datetime.now(timezone.utc).date().isoformat()


def safe_json(value: Any) -> Any:
    if isinstance(value, float) and not math.isfinite(value):
        return None
    if isinstance(value, dict):
        return {str(key): safe_json(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [safe_json(item) for item in value]
    return value


def dump_json(path: Path, value: Any) -> None:
    path.write_text(
        json.dumps(safe_json(value), indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )


def append_jsonl(stream: Any, value: dict[str, Any]) -> None:
    stream.write(json.dumps(safe_json(value), sort_keys=True) + "\n")
    stream.flush()


def _rate(current: float | None, previous: float | None, elapsed: float) -> float | None:
    if current is None or previous is None or elapsed <= 0:
        return None
    delta = current - previous
    return delta / elapsed if delta >= 0 else None


class HostSampler:
    """Portable host telemetry backed by psutil."""

    def __init__(self) -> None:
        psutil.cpu_percent(interval=None)
        psutil.cpu_times_percent(interval=None)
        self.previous_time: float | None = None
        self.previous_cpu_times: Any = None
        self.previous_disk: Any = None
        self.previous_net: Any = None

    def sample(self) -> dict[str, Any]:
        now = time.monotonic()
        elapsed = now - self.previous_time if self.previous_time is not None else 0.0
        output: dict[str, Any] = {}

        output["cpu_percent"] = psutil.cpu_percent(interval=None)
        output["cpu_percent_per_logical"] = psutil.cpu_percent(interval=None, percpu=True)
        try:
            cumulative_cpu = psutil.cpu_times()
        except (OSError, PermissionError):
            cumulative_cpu = None
        derived_utilization = None
        if cumulative_cpu is not None and self.previous_cpu_times is not None:
            fields = (
                "user",
                "nice",
                "system",
                "idle",
                "iowait",
                "irq",
                "softirq",
                "steal",
            )
            total_delta = sum(
                max(
                    0.0,
                    float(getattr(cumulative_cpu, field, 0.0))
                    - float(getattr(self.previous_cpu_times, field, 0.0)),
                )
                for field in fields
            )
            idle_delta = max(
                0.0,
                float(getattr(cumulative_cpu, "idle", 0.0))
                - float(getattr(self.previous_cpu_times, "idle", 0.0)),
            ) + max(
                0.0,
                float(getattr(cumulative_cpu, "iowait", 0.0))
                - float(getattr(self.previous_cpu_times, "iowait", 0.0)),
            )
            if total_delta > 0:
                derived_utilization = 100.0 * (1.0 - min(idle_delta, total_delta) / total_delta)
        output["cpu_utilization_derived_percent"] = derived_utilization
        cpu_times = psutil.cpu_times_percent(interval=None)
        output["cpu_times_percent"] = {
            name: getattr(cpu_times, name, None)
            for name in (
                "user",
                "system",
                "idle",
                "nice",
                "iowait",
                "irq",
                "softirq",
                "steal",
            )
        }
        try:
            output["load_average"] = list(psutil.getloadavg())
        except (AttributeError, OSError):
            output["load_average"] = None

        try:
            stats = psutil.cpu_stats()
        except (OSError, PermissionError):
            stats = None
        output["context_switches_total"] = getattr(stats, "ctx_switches", None)
        output["interrupts_total"] = getattr(stats, "interrupts", None)
        output["soft_interrupts_total"] = getattr(stats, "soft_interrupts", None)
        output["syscalls_total"] = getattr(stats, "syscalls", None)

        try:
            frequency = psutil.cpu_freq()
        except (OSError, PermissionError):
            frequency = None
        output["cpu_frequency_mhz"] = (
            {
                "current": frequency.current,
                "minimum": frequency.min,
                "maximum": frequency.max,
            }
            if frequency is not None
            else None
        )

        try:
            memory = psutil.virtual_memory()
        except (OSError, PermissionError):
            memory = None
        output["memory"] = (
            {
                name: getattr(memory, name, None)
                for name in (
                    "total",
                    "available",
                    "used",
                    "free",
                    "active",
                    "inactive",
                    "wired",
                    "cached",
                    "percent",
                )
            }
            if memory is not None
            else None
        )
        try:
            swap = psutil.swap_memory()
        except (OSError, PermissionError):
            swap = None
        output["swap"] = (
            {
                name: getattr(swap, name, None)
                for name in ("total", "used", "free", "percent", "sin", "sout")
            }
            if swap is not None
            else None
        )

        try:
            disk = psutil.disk_io_counters(perdisk=False)
        except (OSError, PermissionError):
            disk = None
        if disk is not None:
            output["disk"] = {
                "read_bytes_total": disk.read_bytes,
                "write_bytes_total": disk.write_bytes,
                "read_count_total": disk.read_count,
                "write_count_total": disk.write_count,
                "read_bytes_per_second": _rate(
                    disk.read_bytes,
                    self.previous_disk.read_bytes if self.previous_disk else None,
                    elapsed,
                ),
                "write_bytes_per_second": _rate(
                    disk.write_bytes,
                    self.previous_disk.write_bytes if self.previous_disk else None,
                    elapsed,
                ),
            }
        else:
            output["disk"] = None

        try:
            net = psutil.net_io_counters(pernic=False)
        except (OSError, PermissionError):
            net = None
        if net is not None:
            output["network"] = {
                "bytes_sent_total": net.bytes_sent,
                "bytes_received_total": net.bytes_recv,
                "packets_sent_total": net.packets_sent,
                "packets_received_total": net.packets_recv,
                "bytes_sent_per_second": _rate(
                    net.bytes_sent,
                    self.previous_net.bytes_sent if self.previous_net else None,
                    elapsed,
                ),
                "bytes_received_per_second": _rate(
                    net.bytes_recv,
                    self.previous_net.bytes_recv if self.previous_net else None,
                    elapsed,
                ),
            }
        else:
            output["network"] = None

        try:
            output["process_count"] = len(psutil.pids())
        except (OSError, PermissionError):
            output["process_count"] = None
        try:
            output["uptime_seconds"] = time.time() - psutil.boot_time()
        except (OSError, PermissionError):
            output["uptime_seconds"] = None
        self.previous_time = now
        self.previous_cpu_times = cumulative_cpu
        self.previous_disk = disk
        self.previous_net = net
        return safe_json(output)


class MacmonStream:
    def __init__(
        self,
        executable: str,
        interval_ms: int,
        log_path: Path,
        raw_path: Path,
    ) -> None:
        self.executable = executable
        self.interval_ms = interval_ms
        self.log_handle = log_path.open("w", encoding="utf-8")
        self.raw_handle = raw_path.open("w", encoding="utf-8")
        self.process: subprocess.Popen[str] | None = None
        self.thread: threading.Thread | None = None
        self.lock = threading.Lock()
        self.latest_sample: dict[str, Any] | None = None
        self.sample_count = 0

    def start(self, timeout_seconds: float = 10.0) -> None:
        self.process = subprocess.Popen(
            [self.executable, "pipe", "-i", str(self.interval_ms)],
            stdout=subprocess.PIPE,
            stderr=self.log_handle,
            text=True,
            bufsize=1,
        )

        def read() -> None:
            assert self.process is not None and self.process.stdout is not None
            for line in self.process.stdout:
                self.raw_handle.write(line)
                self.raw_handle.flush()
                try:
                    sample = json.loads(line)
                except json.JSONDecodeError:
                    continue
                if isinstance(sample, dict):
                    with self.lock:
                        self.latest_sample = sample
                        self.sample_count += 1

        self.thread = threading.Thread(target=read, daemon=True)
        self.thread.start()
        deadline = time.monotonic() + timeout_seconds
        while time.monotonic() < deadline:
            with self.lock:
                if self.latest_sample is not None:
                    return
            if self.process.poll() is not None:
                break
            time.sleep(0.05)
        self.stop()
        raise RuntimeError("macmon produced no JSON telemetry during its startup probe")

    def latest(self) -> dict[str, Any] | None:
        with self.lock:
            return safe_json(dict(self.latest_sample)) if self.latest_sample else None

    def stop(self) -> None:
        if self.process is not None and self.process.poll() is None:
            self.process.terminate()
            try:
                self.process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                self.process.kill()
                self.process.wait(timeout=5)
        if self.thread is not None:
            self.thread.join(timeout=2)
        if not self.log_handle.closed:
            self.log_handle.close()
        if not self.raw_handle.closed:
            self.raw_handle.close()


@dataclass(frozen=True)
class SysfsChannel:
    key: str
    path: Path
    unit: str
    divisor: float


def _slug(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", "_", value.lower()).strip("_") or "unknown"


class LinuxSysfsSampler:
    def __init__(self) -> None:
        self.channels = self._discover()
        self.frequency_paths = sorted(
            Path("/sys/devices/system/cpu").glob("cpu[0-9]*/cpufreq/scaling_cur_freq")
        )

    @staticmethod
    def _discover() -> list[SysfsChannel]:
        result: list[SysfsChannel] = []
        seen: set[str] = set()

        def add_channel(
            *,
            base: str,
            path: Path,
            unit: str,
            divisor: float,
        ) -> None:
            key = base
            suffix = 2
            while key in seen:
                key = f"{base}_{suffix}"
                suffix += 1
            seen.add(key)
            result.append(SysfsChannel(key, path, unit, divisor))

        specifications = (
            ("temp", "celsius", 1000.0),
            ("power", "watts", 1_000_000.0),
            ("energy", "joules", 1_000_000.0),
            ("fan", "rpm", 1.0),
        )
        for hwmon in sorted(Path("/sys/class/hwmon").glob("hwmon*")):
            try:
                chip = (hwmon / "name").read_text().strip()
            except OSError:
                chip = hwmon.name
            for prefix, unit, divisor in specifications:
                for path in sorted(hwmon.glob(f"{prefix}[0-9]*_input")):
                    stem = path.name.removesuffix("_input")
                    label_path = path.with_name(f"{stem}_label")
                    try:
                        label = label_path.read_text().strip()
                    except OSError:
                        label = stem
                    add_channel(
                        base=f"hwmon.{_slug(chip)}.{_slug(label)}",
                        path=path,
                        unit=unit,
                        divisor=divisor,
                    )
        powercap = Path("/sys/class/powercap")
        if powercap.is_dir():
            for path in sorted(powercap.rglob("energy_uj")):
                try:
                    zone = (path.parent / "name").read_text().strip()
                except OSError:
                    zone = path.parent.name
                add_channel(
                    base=f"powercap.{_slug(zone)}.energy",
                    path=path,
                    unit="joules",
                    divisor=1_000_000.0,
                )
            for path in sorted(powercap.rglob("power_uw")):
                try:
                    zone = (path.parent / "name").read_text().strip()
                except OSError:
                    zone = path.parent.name
                add_channel(
                    base=f"powercap.{_slug(zone)}.power",
                    path=path,
                    unit="watts",
                    divisor=1_000_000.0,
                )
        return result

    def sample(self) -> dict[str, Any]:
        values: dict[str, Any] = {}
        for channel in self.channels:
            try:
                values[channel.key] = float(channel.path.read_text().strip()) / channel.divisor
            except (OSError, ValueError):
                values[channel.key] = None
        frequencies: list[float] = []
        for path in self.frequency_paths:
            try:
                frequencies.append(float(path.read_text().strip()) / 1000.0)
            except (OSError, ValueError):
                continue
        values["cpu_frequency_average_mhz"] = (
            statistics.fmean(frequencies) if frequencies else None
        )
        return values

    def metadata(self) -> list[dict[str, str]]:
        return [
            {
                "native_name": channel.key,
                "unit": channel.unit,
                "source": str(channel.path),
            }
            for channel in self.channels
        ]


def _command_version(command: list[str]) -> str | None:
    try:
        result = subprocess.run(
            command,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            timeout=15,
            check=False,
        )
    except (OSError, subprocess.TimeoutExpired):
        return None
    text = (result.stdout or "").strip()
    return text.splitlines()[0] if text else None


def repository_state() -> dict[str, Any]:
    root = Path(__file__).resolve().parents[2]
    try:
        commit = subprocess.check_output(
            ["git", "-C", str(root), "rev-parse", "HEAD"],
            text=True,
            stderr=subprocess.DEVNULL,
        ).strip()
        status = subprocess.check_output(
            ["git", "-C", str(root), "status", "--porcelain", "--untracked-files=normal"],
            text=True,
            stderr=subprocess.DEVNULL,
        )
        return {
            "repository": root.name,
            "git_commit": commit,
            "git_dirty": bool(status.strip()),
        }
    except (OSError, subprocess.CalledProcessError):
        return {
            "repository": root.name,
            "git_commit": None,
            "git_dirty": None,
        }


def sanitized_platform_snapshot(platform_id: str) -> dict[str, Any]:
    snapshot: dict[str, Any] = {
        "platform_id": platform_id,
        "architecture": platform.machine(),
        "operating_system": platform.system(),
        "operating_system_release": platform.release(),
        "operating_system_version": platform.version(),
        "logical_cpu_count": psutil.cpu_count(logical=True),
        "physical_cpu_count": psutil.cpu_count(logical=False),
        "memory_bytes": psutil.virtual_memory().total,
        "python_version": platform.python_version(),
        "psutil_version": psutil.__version__,
        "capture_utc": utc_now(),
        "privacy": "serial numbers, hardware UUIDs, hostname, and user identity omitted",
    }
    if platform.system() == "Darwin":
        try:
            result = subprocess.run(
                ["system_profiler", "-json", "SPHardwareDataType"],
                stdout=subprocess.PIPE,
                stderr=subprocess.DEVNULL,
                text=True,
                timeout=30,
                check=False,
            )
            payload = json.loads(result.stdout)
            hardware = payload.get("SPHardwareDataType", [{}])[0]
            snapshot["hardware"] = {
                "model_name": hardware.get("machine_name"),
                "model_identifier": hardware.get("machine_model"),
                "chip": hardware.get("chip_type"),
                "physical_memory": hardware.get("physical_memory"),
            }
        except (OSError, ValueError, subprocess.TimeoutExpired):
            snapshot["hardware"] = {}
        snapshot["tools"] = {
            "macmon": _command_version(["macmon", "--version"]),
            "xctrace": _command_version(["xcrun", "xctrace", "version"]),
        }
    elif platform.system() == "Linux":
        model = None
        try:
            for line in Path("/proc/cpuinfo").read_text().splitlines():
                if line.lower().startswith("model name"):
                    model = line.split(":", 1)[1].strip()
                    break
        except OSError:
            pass
        os_release: dict[str, str] = {}
        try:
            for line in Path("/etc/os-release").read_text().splitlines():
                if "=" in line:
                    key, value = line.split("=", 1)
                    if key in {"ID", "VERSION_ID", "PRETTY_NAME"}:
                        os_release[key.lower()] = value.strip().strip('"')
        except OSError:
            pass
        snapshot["hardware"] = {"cpu_model": model}
        snapshot["linux_distribution"] = os_release
        snapshot["tools"] = {
            "perf": _command_version(["perf", "--version"]),
            "sensors": _command_version(["sensors", "--version"]),
        }
    return safe_json(snapshot)


def flatten_leaves(value: Any, prefix: str = "") -> dict[str, Any]:
    output: dict[str, Any] = {}
    if isinstance(value, dict):
        for key, item in value.items():
            child = f"{prefix}.{key}" if prefix else str(key)
            output.update(flatten_leaves(item, child))
    elif isinstance(value, list):
        for index, item in enumerate(value):
            child = f"{prefix}.{index}" if prefix else str(index)
            output.update(flatten_leaves(item, child))
    else:
        output[prefix] = value
    return output


def sanitize_enriched_sample(
    platform_id: str,
    value: dict[str, Any] | None,
) -> tuple[dict[str, Any] | None, list[str]]:
    """Preserve raw collector output separately and null impossible derived values."""

    if value is None:
        return None, []
    sample = safe_json(value)
    flags: list[str] = []
    if platform_id == "M2_MACOS":
        temperatures = sample.get("temp")
        if isinstance(temperatures, dict):
            for name, raw in list(temperatures.items()):
                if isinstance(raw, (int, float)) and not (
                    QUALITY_CONTRACT["apple_temperature_min_celsius"]
                    <= float(raw)
                    <= QUALITY_CONTRACT["apple_temperature_max_celsius"]
                ):
                    temperatures[name] = None
                    flags.append(f"out_of_range:enriched.temp.{name}")
        for name in (
            "all_power",
            "ane_power",
            "cpu_power",
            "gpu_power",
            "gpu_ram_power",
            "ram_power",
            "sys_power",
        ):
            raw = sample.get(name)
            if isinstance(raw, (int, float)) and float(raw) < 0:
                sample[name] = None
                flags.append(f"out_of_range:enriched.{name}")
        for name in ("pcpu_usage", "ecpu_usage", "gpu_usage"):
            raw = sample.get(name)
            if (
                isinstance(raw, list)
                and len(raw) > 1
                and isinstance(raw[1], (int, float))
                and not (0.0 <= float(raw[1]) <= 1.0)
            ):
                raw[1] = None
                flags.append(f"out_of_range:enriched.{name}.1")
    return sample, flags


def channel_group(name: str) -> SemanticGroup:
    lower = name.lower()
    if any(token in lower for token in ("gpu", "ane", "accelerator")):
        return SemanticGroup.ACCELERATOR
    if any(token in lower for token in ("temperature", "temp", "power", "energy", "fan")):
        return SemanticGroup.THERMAL_POWER
    if any(token in lower for token in ("memory", "swap", "ram")):
        return SemanticGroup.MEMORY
    if any(token in lower for token in ("disk", "network", "io", "bytes_", "packets_")):
        return SemanticGroup.IO
    if "availability" in lower or "missing" in lower:
        return SemanticGroup.AVAILABILITY
    return SemanticGroup.COMPUTE


def channel_unit(name: str) -> str:
    lower = name.lower()
    if lower.endswith("timestamp") or lower.endswith("ts_utc"):
        return "ISO-8601"
    if "temperature" in lower or "_temp" in lower or ".temp" in lower:
        return "celsius"
    if "power" in lower:
        return "watts"
    if "energy" in lower:
        return "joules"
    if "frequency" in lower or lower.endswith("_mhz") or lower.endswith("usage.0"):
        return "megahertz"
    if "percent" in lower:
        return "percent"
    if lower.endswith("usage.1"):
        return "fraction"
    if "bytes_per_second" in lower:
        return "bytes/second"
    if ("memory." in lower or "swap." in lower) and not lower.endswith(".percent"):
        return "bytes"
    if "bytes" in lower or "ram_" in lower:
        return "bytes"
    if "seconds" in lower or lower.endswith("_s"):
        return "seconds"
    if "fan" in lower:
        return "rpm"
    return "count_or_native"


def channel_registry(samples: Iterable[dict[str, Any]], period: float) -> list[dict[str, Any]]:
    names: set[str] = set()
    for sample in samples:
        for branch in ("host", "enriched"):
            value = sample.get(branch)
            if value is not None:
                names.update(f"{branch}.{name}" for name in flatten_leaves(value))
    registry = []
    for name in sorted(names):
        registry.append(
            {
                "native_name": name,
                "unit": channel_unit(name),
                "semantic_group": channel_group(name).value,
                "source": "psutil" if name.startswith("host.") else "platform_native",
                "sampling_period_seconds": period,
                "missingness": "null means unavailable or unreadable; never imputed as zero",
            }
        )
    return registry


def write_checksums(run_dir: Path) -> None:
    excluded = {"checksums.sha256", "validation.json"}
    lines: list[str] = []
    for path in sorted(item for item in run_dir.rglob("*") if item.is_file()):
        if path.name in excluded:
            continue
        lines.append(f"{file_sha256(path)}  {path.relative_to(run_dir).as_posix()}")
    (run_dir / "checksums.sha256").write_text("\n".join(lines) + "\n", encoding="utf-8")


def file_sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _nested_value(value: Any, dotted_name: str) -> Any:
    current = value
    for part in dotted_name.split("."):
        if isinstance(current, dict):
            current = current.get(part)
        elif isinstance(current, list) and part.isdigit():
            index = int(part)
            current = current[index] if index < len(current) else None
        else:
            return None
    return current


def telemetry_quality_summary(
    samples: list[dict[str, Any]],
    platform_id: str,
    profile: str = "enriched",
) -> dict[str, Any]:
    usable_samples = [
        sample
        for sample in samples
        if not sample.get("availability", {}).get("interruption_injected", False)
    ]
    critical = (
        (
            "enriched.cpu_power",
            "enriched.sys_power",
            "enriched.pcpu_usage.1",
            "enriched.temp.cpu_temp_avg",
        )
        if platform_id == "M2_MACOS" and profile == "enriched"
        else (
            "host.cpu_percent",
            "host.memory.percent",
            "host.load_average.0",
        )
    )
    channels: dict[str, Any] = {}
    denominator = len(usable_samples)
    for name in critical:
        values = [_nested_value(sample, name) for sample in usable_samples]
        if name == "enriched.temp.cpu_temp_avg":
            valid = [
                isinstance(value, (int, float))
                and QUALITY_CONTRACT["apple_temperature_min_celsius"]
                <= float(value)
                <= QUALITY_CONTRACT["apple_temperature_max_celsius"]
                for value in values
            ]
        elif name in {"enriched.cpu_power", "enriched.sys_power"}:
            valid = [
                isinstance(value, (int, float)) and float(value) >= 0
                for value in values
            ]
        elif name == "enriched.pcpu_usage.1":
            valid = [
                isinstance(value, (int, float)) and 0.0 <= float(value) <= 1.0
                for value in values
            ]
        else:
            valid = [value is not None for value in values]
        count = sum(valid)
        channels[name] = {
            "non_null_samples": count,
            "eligible_samples": denominator,
            "non_null_fraction": count / denominator if denominator else 0.0,
        }
    flag_counts: dict[str, int] = {}
    for sample in samples:
        for flag in sample.get("availability", {}).get("quality_flags", []):
            flag_counts[str(flag)] = flag_counts.get(str(flag), 0) + 1
    if platform_id == "M2_MACOS":
        recorded_temperature_flags = flag_counts.get(
            "out_of_range:enriched.temp.cpu_temp_avg",
            0,
        )
        observed_temperature_flags = sum(
            isinstance(value, (int, float))
            and not (
                QUALITY_CONTRACT["apple_temperature_min_celsius"]
                <= float(value)
                <= QUALITY_CONTRACT["apple_temperature_max_celsius"]
            )
            for value in (
                _nested_value(sample, "enriched.temp.cpu_temp_avg")
                for sample in usable_samples
            )
        )
        if observed_temperature_flags > recorded_temperature_flags:
            flag_counts["out_of_range:enriched.temp.cpu_temp_avg"] = (
                observed_temperature_flags
            )
    return {
        "critical_channels": channels,
        "quality_flag_counts": flag_counts,
        "interruption_masked_samples": len(samples) - len(usable_samples),
    }


def verify_checksums(run_dir: Path) -> list[str]:
    failures: list[str] = []
    manifest = run_dir / "checksums.sha256"
    if not manifest.is_file():
        return ["checksums.sha256 is missing"]
    for line in manifest.read_text().splitlines():
        expected, relative = line.split("  ", 1)
        path = run_dir / relative
        if not path.is_file():
            failures.append(f"missing checksum target: {relative}")
            continue
        actual = file_sha256(path)
        if actual != expected:
            failures.append(f"checksum mismatch: {relative}")
    return failures


def validate_run(run_dir: Path, verify_hashes: bool = True) -> dict[str, Any]:
    failures: list[str] = []
    warnings: list[str] = []
    required = (
        "platform.json",
        "collection.json",
        "telemetry.jsonl",
        "events.jsonl",
        "channels.json",
    )
    for filename in required:
        if not (run_dir / filename).is_file():
            failures.append(f"missing required file: {filename}")
    if failures:
        return {"valid": False, "failures": failures, "validated_utc": utc_now()}

    collection = json.loads((run_dir / "collection.json").read_text())
    samples = [
        json.loads(line)
        for line in (run_dir / "telemetry.jsonl").read_text().splitlines()
        if line.strip()
    ]
    events = [
        json.loads(line)
        for line in (run_dir / "events.jsonl").read_text().splitlines()
        if line.strip()
    ]
    expected = int(collection["expected_samples"])
    if len(samples) != expected:
        failures.append(f"sample count {len(samples)} does not equal expected {expected}")
    relative = [float(sample["t_rel_seconds"]) for sample in samples]
    if any(right <= left for left, right in zip(relative, relative[1:])):
        failures.append("sample relative timestamps are not strictly increasing")
    if len(relative) > 2:
        deltas = [right - left for left, right in zip(relative, relative[1:])]
        median = statistics.median(deltas)
        target = 1.0 / float(collection["sampling_hz"])
        if not (target * 0.5 <= median <= target * 1.5):
            failures.append(
                f"median sampling interval {median:.4f}s is outside tolerance around {target:.4f}s"
            )
        if max(deltas) > target * 3:
            failures.append(
                f"maximum sampling gap {max(deltas):.4f}s exceeds three periods"
            )
        expected_span = (expected - 1) * target
        observed_span = relative[-1] - relative[0]
        span_tolerance = max(0.5, expected_span * 0.05)
        if abs(observed_span - expected_span) > span_tolerance:
            failures.append(
                f"observed sample span {observed_span:.4f}s differs from expected "
                f"{expected_span:.4f}s by more than {span_tolerance:.4f}s"
            )
    event_names = {event.get("event") for event in events}
    if "workload_started" not in event_names:
        failures.append("workload_started event is missing")
    scenario = collection["scenario"]
    if scenario == "CONTROLLED_CRASH":
        if "controlled_crash_injected" not in event_names:
            failures.append("controlled_crash_injected event is missing")
    elif scenario == "TELEMETRY_INTERRUPTION":
        for required_event in (
            "telemetry_interruption_started",
            "telemetry_interruption_ended",
        ):
            if required_event not in event_names:
                failures.append(f"{required_event} event is missing")
        interrupted = [
            sample
            for sample in samples
            if sample.get("availability", {}).get("interruption_injected", False)
        ]
        if not interrupted:
            failures.append("telemetry interruption produced no masked samples")
        if interrupted and len(interrupted) == len(samples):
            failures.append("telemetry interruption never recovered before run end")
    elif scenario != "NOMINAL" and "stressor_started" not in event_names:
        failures.append("stressor_started event is missing")
    if collection.get("status") != "complete":
        failures.append(f"collection status is {collection.get('status')!r}, not 'complete'")
    if verify_hashes:
        failures.extend(verify_checksums(run_dir))
    null_enriched = sum(sample.get("enriched") is None for sample in samples)
    platform_id = str(collection.get("platform_id", ""))
    quality = (
        telemetry_quality_summary(
            samples,
            platform_id,
            str(collection.get("profile", "enriched")),
        )
        if platform_id in {"M2_MACOS", "EPYC_LINUX"}
        else {
            "critical_channels": {},
            "quality_flag_counts": {},
            "interruption_masked_samples": 0,
        }
    )
    for name, metrics in quality["critical_channels"].items():
        fraction = float(metrics["non_null_fraction"])
        if name == "enriched.temp.cpu_temp_avg":
            minimum_fraction = QUALITY_CONTRACT[
                "apple_temperature_minimum_fraction"
            ]
        else:
            minimum_fraction = (
                QUALITY_CONTRACT["primary_channel_minimum_fraction"]
                if collection.get("purpose") == "production"
                else 0.70
            )
        if fraction < minimum_fraction:
            failures.append(
                f"critical channel {name} non-null fraction {fraction:.3f} "
                f"is below {minimum_fraction:.2f}"
            )
        elif fraction < 0.95:
            warnings.append(
                f"critical channel {name} non-null fraction is {fraction:.3f}"
            )
    flagged = sum(quality["quality_flag_counts"].values())
    flagged_fraction = flagged / len(samples) if samples else 0.0
    if flagged_fraction > QUALITY_CONTRACT["maximum_quality_flag_fraction"]:
        failures.append(
            f"quality flags affect {flagged_fraction:.3f} of samples, above "
            f"{QUALITY_CONTRACT['maximum_quality_flag_fraction']:.2f}"
        )
    elif flagged:
        warnings.append(
            f"detected {flagged} impossible enriched values; they are excluded "
            "from critical-channel quality coverage"
        )
    return {
        "valid": not failures,
        "failures": failures,
        "warnings": warnings,
        "validated_utc": utc_now(),
        "sample_count": len(samples),
        "expected_samples": expected,
        "duration_observed_seconds": relative[-1] - relative[0] if len(relative) > 1 else 0,
        "enriched_missing_samples": null_enriched,
        "quality": quality,
        "checksums_verified": verify_hashes,
    }


def _event(stream: Any, start: float, name: str, **details: Any) -> None:
    append_jsonl(
        stream,
        {
            "event": name,
            "ts_utc": utc_now(),
            "t_rel_seconds": time.monotonic() - start,
            **details,
        },
    )


def _start_harness(role: str, name: str, log_path: Path) -> tuple[subprocess.Popen[str], Any]:
    log_handle = log_path.open("w", encoding="utf-8")
    environment = os.environ.copy()
    threads = environment.get("PRISM_NUM_THREADS", "1")
    environment.update(
        {
            "OMP_NUM_THREADS": threads,
            "OPENBLAS_NUM_THREADS": threads,
            "MKL_NUM_THREADS": threads,
            "VECLIB_MAXIMUM_THREADS": threads,
            "NUMEXPR_NUM_THREADS": threads,
        }
    )
    process = subprocess.Popen(
        [
            sys.executable,
            "-m",
            "prism_slm.workload_harness",
            "--role",
            role,
            "--name",
            name,
        ],
        stdout=log_handle,
        stderr=subprocess.STDOUT,
        text=True,
        env=environment,
    )
    return process, log_handle


def _stop_process(process: subprocess.Popen[str] | None, log_handle: Any = None) -> int | None:
    code = None
    if process is not None:
        if process.poll() is None:
            process.terminate()
            try:
                process.wait(timeout=10)
            except subprocess.TimeoutExpired:
                process.kill()
                process.wait(timeout=10)
        code = process.returncode
    if log_handle is not None:
        log_handle.close()
    return code


@dataclass(frozen=True)
class CollectionRequest:
    platform_id: str
    workload: str
    scenario: str
    repetition: int
    split: str
    duration_seconds: int
    sampling_hz: float
    warmup_seconds: float
    interruption_seconds: float
    purpose: str
    profile: str
    output_root: Path
    run_id: str | None = None
    macmon_executable: str = "macmon"
    enable_xctrace: bool = False
    xctrace_template: str = "Time Profiler"


def collect(request: CollectionRequest) -> Path:
    workload = request.workload.upper()
    scenario = request.scenario.upper()
    current_system = platform.system()
    expected_systems = {"M2_MACOS": "Darwin", "EPYC_LINUX": "Linux"}
    if request.platform_id not in expected_systems:
        raise ValueError(f"unsupported platform_id: {request.platform_id}")
    if current_system != expected_systems[request.platform_id]:
        raise ValueError(
            f"platform_id {request.platform_id} requires {expected_systems[request.platform_id]}, "
            f"but the current system is {current_system}"
        )
    if request.profile not in {"portable", "enriched"}:
        raise ValueError(f"unsupported collection profile: {request.profile}")
    if request.purpose not in {"smoke", "production"}:
        raise ValueError(f"unsupported collection purpose: {request.purpose}")
    if workload not in WORKLOADS:
        raise ValueError(f"unsupported workload: {workload}")
    if scenario not in SCENARIOS:
        raise ValueError(f"unsupported executable scenario: {scenario}")
    if request.duration_seconds < 5:
        raise ValueError("duration_seconds must be at least 5")
    if request.sampling_hz <= 0 or request.sampling_hz > 20:
        raise ValueError("sampling_hz must be in (0, 20]")
    if scenario != "NOMINAL" and not (0 <= request.warmup_seconds < request.duration_seconds):
        raise ValueError("warmup_seconds must be within the run for anomalous scenarios")
    if scenario == "TELEMETRY_INTERRUPTION" and not (
        0 < request.interruption_seconds
        < request.duration_seconds - request.warmup_seconds
    ):
        raise ValueError(
            "interruption_seconds must be positive and leave time for recovery"
        )
    if scenario == "TELEMETRY_INTERRUPTION" and request.profile != "enriched":
        raise ValueError("TELEMETRY_INTERRUPTION requires the enriched profile")
    software_state = repository_state()
    if request.purpose == "production" and software_state.get("git_dirty") is not False:
        raise RuntimeError(
            "production collection requires a clean, committed Git checkout"
        )

    timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    run_id = request.run_id or (
        f"{request.purpose}__{request.platform_id.lower()}__{workload.lower()}__"
        f"{scenario.lower()}__r{request.repetition:02d}__{timestamp}"
    )
    run_dir = request.output_root / request.platform_id / utc_date() / run_id
    if run_dir.exists():
        raise FileExistsError(f"run directory already exists: {run_dir}")
    run_dir.mkdir(parents=True)

    period = 1.0 / request.sampling_hz
    expected_samples = int(round(request.duration_seconds * request.sampling_hz))
    collector_process = psutil.Process(os.getpid())
    collector_cpu_start = collector_process.cpu_times()
    collection_record: dict[str, Any] = {
        "run_id": run_id,
        "platform_id": request.platform_id,
        "workload": workload,
        "scenario": scenario,
        "repetition": request.repetition,
        "planned_split": request.split,
        "purpose": request.purpose,
        "profile": request.profile,
        "duration_seconds": request.duration_seconds,
        "sampling_hz": request.sampling_hz,
        "warmup_seconds": request.warmup_seconds,
        "interruption_seconds": request.interruption_seconds,
        "expected_samples": expected_samples,
        "start_utc": utc_now(),
        "status": "collecting",
        "command": sys.argv,
        "software": software_state,
        "workload_protocol": {
            "num_threads": int(os.environ.get("PRISM_NUM_THREADS", "1")),
            "stress_memory_mb": int(os.environ.get("PRISM_STRESS_MB", "128")),
        },
        "quality_contract": QUALITY_CONTRACT,
    }
    dump_json(run_dir / "platform.json", sanitized_platform_snapshot(request.platform_id))
    dump_json(run_dir / "collection.json", collection_record)

    host = HostSampler()
    macmon: MacmonStream | None = None
    linux_sysfs: LinuxSysfsSampler | None = None
    workload_process: subprocess.Popen[str] | None = None
    workload_log: Any = None
    stressor_process: subprocess.Popen[str] | None = None
    stressor_log: Any = None
    trace_process: subprocess.Popen[str] | None = None
    trace_log: Any = None
    samples_for_registry: list[dict[str, Any]] = []
    setup_start = time.monotonic()
    start = setup_start
    collection_error: str | None = None
    controlled_crash_injected = False
    telemetry_interruption_started = False
    telemetry_interruption_ended = False

    with (run_dir / "events.jsonl").open("w", encoding="utf-8") as events, (
        run_dir / "telemetry.jsonl"
    ).open("w", encoding="utf-8") as telemetry:
        try:
            enriched_event: dict[str, Any] | None = None
            if platform.system() == "Darwin" and request.profile == "enriched":
                executable = shutil.which(request.macmon_executable)
                if executable is None:
                    raise RuntimeError(f"macmon not found: {request.macmon_executable}")
                macmon = MacmonStream(
                    executable,
                    int(round(period * 1000)),
                    run_dir / "macmon.log",
                    run_dir / "macmon-raw.jsonl",
                )
                macmon.start()
                enriched_event = {"source": "macmon"}
            elif platform.system() == "Linux" and request.profile == "enriched":
                linux_sysfs = LinuxSysfsSampler()
                enriched_event = {
                    "source": "linux_sysfs",
                    "discovered_channels": len(linux_sysfs.channels),
                }

            # The research clock begins only after platform collectors are
            # ready. Setup latency must not compress early sample intervals or
            # shift the declared stressor onset.
            start = time.monotonic()
            collection_record["start_utc"] = utc_now()
            _event(events, start, "collector_started", profile=request.profile)
            if enriched_event is not None:
                _event(events, start, "enriched_collector_started", **enriched_event)
            if request.enable_xctrace:
                if platform.system() != "Darwin":
                    raise RuntimeError("xctrace is supported only on macOS")
                trace_log = (run_dir / "xctrace.log").open("w", encoding="utf-8")
                trace_process = subprocess.Popen(
                    [
                        "xcrun",
                        "xctrace",
                        "record",
                        "--template",
                        request.xctrace_template,
                        "--all-processes",
                        "--time-limit",
                        f"{request.duration_seconds}s",
                        "--output",
                        str(run_dir / "xctrace.trace"),
                        "--no-prompt",
                    ],
                    stdout=trace_log,
                    stderr=subprocess.STDOUT,
                    text=True,
                )
                _event(
                    events,
                    start,
                    "trace_collector_started",
                    source="xctrace",
                    template=request.xctrace_template,
                )

            workload_process, workload_log = _start_harness(
                "workload", workload, run_dir / "workload.log"
            )
            _event(events, start, "workload_started", workload=workload)

            next_sample = start
            for sequence in range(expected_samples):
                now = time.monotonic()
                elapsed = now - start
                if (
                    scenario == "CONTROLLED_CRASH"
                    and not controlled_crash_injected
                    and elapsed >= request.warmup_seconds
                ):
                    assert workload_process is not None
                    workload_process.kill()
                    workload_process.wait(timeout=10)
                    controlled_crash_injected = True
                    _event(
                        events,
                        start,
                        "controlled_crash_injected",
                        target="workload_child",
                        signal="SIGKILL",
                        exit_code=workload_process.returncode,
                    )
                elif (
                    scenario == "TELEMETRY_INTERRUPTION"
                    and not telemetry_interruption_started
                    and elapsed >= request.warmup_seconds
                ):
                    telemetry_interruption_started = True
                    _event(
                        events,
                        start,
                        "telemetry_interruption_started",
                        source=(
                            "macmon"
                            if macmon is not None
                            else "linux_sysfs"
                            if linux_sysfs is not None
                            else "enriched"
                        ),
                        planned_duration_seconds=request.interruption_seconds,
                    )
                elif (
                    scenario == "TELEMETRY_INTERRUPTION"
                    and telemetry_interruption_started
                    and not telemetry_interruption_ended
                    and elapsed
                    >= request.warmup_seconds + request.interruption_seconds
                ):
                    telemetry_interruption_ended = True
                    _event(
                        events,
                        start,
                        "telemetry_interruption_ended",
                        planned_duration_seconds=request.interruption_seconds,
                    )
                elif (
                    scenario in STRESSORS
                    and scenario != "NOMINAL"
                    and stressor_process is None
                ):
                    if elapsed >= request.warmup_seconds:
                        stressor_process, stressor_log = _start_harness(
                            "stressor", scenario, run_dir / "stressor.log"
                        )
                        _event(events, start, "stressor_started", scenario=scenario)

                if workload_process.poll() is not None and not (
                    scenario == "CONTROLLED_CRASH" and controlled_crash_injected
                ):
                    raise RuntimeError(
                        f"workload exited before collection ended with code {workload_process.returncode}"
                    )
                if stressor_process is not None and stressor_process.poll() is not None:
                    raise RuntimeError(
                        f"stressor exited before collection ended with code {stressor_process.returncode}"
                    )

                enriched_raw: dict[str, Any] | None = None
                source = None
                if macmon is not None:
                    enriched_raw = macmon.latest()
                    source = "macmon"
                elif linux_sysfs is not None:
                    enriched_raw = linux_sysfs.sample()
                    source = "linux_sysfs"
                enriched, quality_flags = sanitize_enriched_sample(
                    request.platform_id,
                    enriched_raw,
                )
                interruption_active = (
                    scenario == "TELEMETRY_INTERRUPTION"
                    and telemetry_interruption_started
                    and not telemetry_interruption_ended
                )
                if interruption_active:
                    enriched = None

                sample = {
                    "sequence": sequence,
                    "ts_utc": utc_now(),
                    "t_rel_seconds": time.monotonic() - start,
                    "host": host.sample(),
                    "enriched": enriched,
                    "availability": {
                        "host_available": True,
                        "enriched_available": enriched is not None,
                        "enriched_raw_available": enriched_raw is not None,
                        "enriched_source": source,
                        "interruption_injected": interruption_active,
                        "quality_flags": quality_flags,
                    },
                }
                append_jsonl(telemetry, sample)
                if len(samples_for_registry) < 10:
                    samples_for_registry.append(sample)

                next_sample += period
                time.sleep(max(0.0, next_sample - time.monotonic()))

            _event(events, start, "sampling_completed", samples=expected_samples)
        except BaseException as exc:
            collection_error = f"{type(exc).__name__}: {exc}"
            (run_dir / "collector_error.log").write_text(
                traceback.format_exc(), encoding="utf-8"
            )
            _event(events, start, "collection_failed", error=collection_error)
        finally:
            stress_code = _stop_process(stressor_process, stressor_log)
            workload_code = _stop_process(workload_process, workload_log)
            if macmon is not None:
                macmon.stop()
            trace_code = None
            if trace_process is not None:
                try:
                    trace_code = trace_process.wait(timeout=30)
                except subprocess.TimeoutExpired:
                    trace_process.terminate()
                    trace_code = trace_process.wait(timeout=10)
                if trace_code != 0 and collection_error is None:
                    collection_error = f"xctrace exited with code {trace_code}"
            if trace_log is not None:
                trace_log.close()
            _event(
                events,
                start,
                "collectors_stopped",
                workload_exit_code=workload_code,
                stressor_exit_code=stress_code,
                trace_exit_code=trace_code,
            )

    elapsed_seconds = time.monotonic() - start
    collector_cpu_end = collector_process.cpu_times()
    telemetry_bytes = (run_dir / "telemetry.jsonl").stat().st_size
    events_bytes = (run_dir / "events.jsonl").stat().st_size
    native_bytes = sum(
        path.stat().st_size
        for path in run_dir.glob("*-raw.jsonl")
        if path.is_file()
    )
    collection_record.update(
        {
            "end_utc": utc_now(),
            "elapsed_seconds": elapsed_seconds,
            "setup_elapsed_seconds": start - setup_start,
            "status": "failed" if collection_error else "complete",
            "error": collection_error,
            "xctrace_enabled": request.enable_xctrace,
            "xctrace_template": request.xctrace_template if request.enable_xctrace else None,
            "collection_cost": {
                "collector_cpu_seconds": (
                    collector_cpu_end.user
                    + collector_cpu_end.system
                    - collector_cpu_start.user
                    - collector_cpu_start.system
                ),
                "telemetry_bytes": telemetry_bytes,
                "events_bytes": events_bytes,
                "native_raw_bytes": native_bytes,
                "telemetry_bytes_per_second": (
                    telemetry_bytes / elapsed_seconds if elapsed_seconds > 0 else None
                ),
            },
        }
    )
    dump_json(run_dir / "collection.json", collection_record)
    dump_json(
        run_dir / "channels.json",
        {
            "channels": channel_registry(samples_for_registry, period),
            "linux_sysfs_channels": linux_sysfs.metadata() if linux_sysfs else [],
        },
    )
    validation = validate_run(run_dir, verify_hashes=False)
    dump_json(run_dir / "validation.json", validation)
    write_checksums(run_dir)
    validation = validate_run(run_dir, verify_hashes=True)
    dump_json(run_dir / "validation.json", validation)

    if collection_error:
        raise RuntimeError(f"collection failed; preserved run at {run_dir}: {collection_error}")
    if not validation["valid"]:
        raise RuntimeError(f"collection validation failed at {run_dir}: {validation['failures']}")
    return run_dir


def update_collection_plan(plan_path: Path, run_dir: Path) -> None:
    collection = json.loads((run_dir / "collection.json").read_text())
    validation = json.loads((run_dir / "validation.json").read_text())
    rows: list[dict[str, str]]
    with plan_path.open(newline="", encoding="utf-8") as stream:
        reader = csv.DictReader(stream)
        fieldnames = list(reader.fieldnames or [])
        rows = list(reader)
    matched = False
    for row in rows:
        if row["run_id"] == collection["run_id"]:
            row["status"] = "valid" if validation["valid"] else "replacement_required"
            row["start_utc"] = collection["start_utc"]
            row["end_utc"] = collection["end_utc"]
            row["valid_rows"] = str(validation["sample_count"])
            if collection["scenario"] == "NOMINAL" and validation["valid"]:
                row["benign_hours"] = (
                    f"{float(validation['duration_observed_seconds']) / 3600:.6f}"
                )
            row["exclusion_reason"] = "; ".join(validation["failures"])
            warnings = validation.get("warnings", [])
            if warnings:
                prefix = f"{row['notes']}; " if row.get("notes") else ""
                row["notes"] = prefix + "validation warnings: " + "; ".join(warnings)
            matched = True
            break
    if not matched:
        raise ValueError(f"run_id {collection['run_id']} is not present in {plan_path}")
    with plan_path.open("w", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, fieldnames=fieldnames, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)
