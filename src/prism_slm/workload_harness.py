"""Cross-platform workload and pressure harness for PRISM collection.

The harness is intentionally a separate process. Terminating a collector does
not leave a compute loop running, and every independent run starts fresh state.
"""

from __future__ import annotations

import argparse
import hashlib
import os
import random
import signal
import threading
import time
import urllib.parse
import zlib

import numpy as np


SEED = 830616
WORKLOADS = ("PY_STATS", "PY_AI", "BROWSER", "VIDEO_SW")
STRESSORS = (
    "NOMINAL",
    "ATOMIC",
    "BRANCH",
    "CACHE",
    "MEMBW",
    "TLB",
    "THERMAL_SHIFT",
    "POWER_SHIFT",
    "DEGRADATION_PROXY",
)
CONTROL_SCENARIOS = ("CONTROLLED_CRASH", "TELEMETRY_INTERRUPTION")
SCENARIOS = STRESSORS + CONTROL_SCENARIOS


def _stop_event() -> threading.Event:
    event = threading.Event()

    def stop(_signum: int, _frame: object) -> None:
        event.set()

    signal.signal(signal.SIGTERM, stop)
    signal.signal(signal.SIGINT, stop)
    return event


def _memory_mb() -> int:
    value = int(os.environ.get("PRISM_STRESS_MB", "128"))
    return min(max(value, 16), 1024)


def workload_py_stats(stop: threading.Event) -> None:
    rng = np.random.default_rng(SEED)
    values = rng.standard_normal(8_000_000, dtype=np.float32)
    while not stop.is_set():
        _ = (
            float(values.mean()),
            float(values.std()),
            float(np.percentile(values[::16], 95)),
        )
        values[::1024] += np.float32(0.0001)


def workload_py_ai(stop: threading.Event) -> None:
    rng = np.random.default_rng(SEED)
    left = rng.standard_normal((768, 768), dtype=np.float32)
    right = rng.standard_normal((768, 768), dtype=np.float32)
    while not stop.is_set():
        result = left @ right
        left, right = right, np.tanh(result).astype(np.float32, copy=False)


def workload_browser(stop: threading.Event) -> None:
    # A network-free, deterministic web-processing workload. It avoids making
    # Internet availability a hidden experimental variable.
    blocks = [
        (
            f"<article id='{idx}'><a href='/paper/{idx}?view=full'>"
            f"Telemetry article {idx}</a><p>{'silicon ' * 200}</p></article>"
        )
        for idx in range(512)
    ]
    document = ("<html><body>" + "".join(blocks) + "</body></html>").encode()
    while not stop.is_set():
        compressed = zlib.compress(document, level=3)
        restored = zlib.decompress(compressed).decode()
        for token in restored.split("href='")[1::32]:
            urllib.parse.urlparse(token.split("'", 1)[0])
        hashlib.sha256(compressed).digest()


def workload_video_sw(stop: threading.Event) -> None:
    rng = np.random.default_rng(SEED)
    frame = rng.integers(0, 256, size=(720, 1280, 3), dtype=np.uint8)
    while not stop.is_set():
        gray = (
            0.299 * frame[:, :, 0]
            + 0.587 * frame[:, :, 1]
            + 0.114 * frame[:, :, 2]
        ).astype(np.uint8)
        compressed = zlib.compress(gray[::2, ::2].tobytes(), level=1)
        zlib.decompress(compressed)
        frame = np.roll(frame, 1, axis=1)


def stress_nominal(stop: threading.Event) -> None:
    stop.wait()


def stress_atomic(stop: threading.Event) -> None:
    lock = threading.Lock()
    counter = [0]

    def worker() -> None:
        while not stop.is_set():
            with lock:
                counter[0] += 1

    count = max(2, (os.cpu_count() or 2) // 2)
    threads = [threading.Thread(target=worker, daemon=True) for _ in range(count)]
    for thread in threads:
        thread.start()
    while not stop.wait(0.1):
        pass


def stress_branch(stop: threading.Event) -> None:
    rng = random.Random(SEED)
    value = 0
    while not stop.is_set():
        bits = rng.getrandbits(32)
        if bits & 1:
            value += 3
        elif bits & 2:
            value -= 2
        elif bits & 4:
            value ^= bits
        else:
            value += 1


def stress_cache(stop: threading.Event) -> None:
    rng = np.random.default_rng(SEED)
    count = _memory_mb() * 1024 * 1024 // np.dtype(np.float32).itemsize
    values = rng.standard_normal(count, dtype=np.float32)
    indices = rng.integers(0, count, size=min(count, 1_000_000), dtype=np.int64)
    while not stop.is_set():
        _ = float(values[indices].sum())
        indices = np.roll(indices, 1024)


def stress_membw(stop: threading.Event) -> None:
    size = _memory_mb() * 1024 * 1024
    source = np.zeros(size, dtype=np.uint8)
    target = np.ones(size, dtype=np.uint8)
    while not stop.is_set():
        np.copyto(source, target)
        source += np.uint8(1)
        source, target = target, source


def stress_tlb(stop: threading.Event) -> None:
    rng = np.random.default_rng(SEED)
    size = _memory_mb() * 1024 * 1024
    values = np.zeros(size, dtype=np.uint8)
    pages = np.arange(0, size, 4096, dtype=np.int64)
    while not stop.is_set():
        rng.shuffle(pages)
        for start in range(0, len(pages), 4096):
            if stop.is_set():
                return
            block = pages[start : start + 4096]
            values[block] = values[block] + np.uint8(1)


def _matrix_burst(
    stop: threading.Event,
    *,
    active_seconds: float,
    idle_seconds: float,
) -> None:
    rng = np.random.default_rng(SEED)
    left = rng.standard_normal((512, 512), dtype=np.float32)
    right = rng.standard_normal((512, 512), dtype=np.float32)
    while not stop.is_set():
        deadline = time.monotonic() + active_seconds
        while time.monotonic() < deadline and not stop.is_set():
            result = left @ right
            left, right = right, np.tanh(result).astype(np.float32, copy=False)
        if idle_seconds > 0:
            stop.wait(idle_seconds)


def stress_thermal_shift(stop: threading.Event) -> None:
    """Sustained compute-load change used as a portable thermal-condition proxy."""

    _matrix_burst(stop, active_seconds=2.0, idle_seconds=0.02)


def stress_power_shift(stop: threading.Event) -> None:
    """Repeatable duty-cycled compute used as a portable power-demand shift."""

    _matrix_burst(stop, active_seconds=0.35, idle_seconds=0.15)


def stress_degradation_proxy(stop: threading.Event) -> None:
    """Progressively increase compute duty cycle without claiming physical aging."""

    rng = np.random.default_rng(SEED)
    left = rng.standard_normal((512, 512), dtype=np.float32)
    right = rng.standard_normal((512, 512), dtype=np.float32)
    stage = 0
    stage_started = time.monotonic()
    while not stop.is_set():
        active_seconds = min(0.10 + 0.08 * stage, 0.90)
        idle_seconds = max(1.0 - active_seconds, 0.10)
        deadline = time.monotonic() + active_seconds
        while time.monotonic() < deadline and not stop.is_set():
            result = left @ right
            left, right = right, np.tanh(result).astype(np.float32, copy=False)
        stop.wait(idle_seconds)
        if time.monotonic() - stage_started >= 30:
            stage = min(stage + 1, 10)
            stage_started = time.monotonic()


WORKLOAD_FUNCTIONS = {
    "PY_STATS": workload_py_stats,
    "PY_AI": workload_py_ai,
    "BROWSER": workload_browser,
    "VIDEO_SW": workload_video_sw,
}
STRESSOR_FUNCTIONS = {
    "NOMINAL": stress_nominal,
    "ATOMIC": stress_atomic,
    "BRANCH": stress_branch,
    "CACHE": stress_cache,
    "MEMBW": stress_membw,
    "TLB": stress_tlb,
    "THERMAL_SHIFT": stress_thermal_shift,
    "POWER_SHIFT": stress_power_shift,
    "DEGRADATION_PROXY": stress_degradation_proxy,
}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--role", choices=("workload", "stressor"), required=True)
    parser.add_argument("--name", required=True)
    args = parser.parse_args()

    name = args.name.upper()
    functions = WORKLOAD_FUNCTIONS if args.role == "workload" else STRESSOR_FUNCTIONS
    if name not in functions:
        raise SystemExit(f"Unsupported {args.role}: {name}")

    stop = _stop_event()
    functions[name](stop)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
