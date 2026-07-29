# Apple M2 PRISM Collection

This workflow collects **new PRISM evidence**. It does not modify the frozen
DICE baseline. Each run synchronizes portable `psutil` counters with `macmon`
power/temperature telemetry and can capture an `xctrace` Time Profiler trace.

## 1. One-time setup

```bash
cd '/path/to/PRISM'
python3 -m venv .venv
source .venv/bin/activate
python3 -m pip install --upgrade pip
python3 -m pip install -e .
```

Required:

- Apple Silicon macOS;
- Python 3.10 or newer;
- `macmon` for the enriched profile;
- Xcode command-line tooling for optional `xctrace`.

The collector deliberately omits the hostname, username, serial number,
hardware UUID, and provisioning identifiers from `platform.json`.

## 2. Capability probe

Run this in a normal Terminal—not through an IDE sandbox:

```bash
source .venv/bin/activate
python3 scripts/probe_collection.py
```

Confirm that:

- the chip is Apple M2 Pro;
- `macmon.available` is `true`;
- `xctrace.available` is `true` if full traces will be used.

The probe is local and Git-ignored under `data/collection-probes/`.

## 3. Required smoke pair

Collect a 30-second nominal run:

```bash
python3 scripts/collect_run.py \
  --platform-id M2_MACOS \
  --workload PY_STATS \
  --scenario NOMINAL \
  --repetition 0 \
  --split smoke \
  --purpose smoke \
  --profile enriched \
  --duration-seconds 30 \
  --sampling-hz 5
```

Collect a matched 30-second atomic-pressure run with a 10-second pre-onset
window:

```bash
python3 scripts/collect_run.py \
  --platform-id M2_MACOS \
  --workload PY_STATS \
  --scenario ATOMIC \
  --repetition 0 \
  --split smoke \
  --purpose smoke \
  --profile enriched \
  --duration-seconds 30 \
  --warmup-seconds 10 \
  --sampling-hz 5
```

The pressure harness is bounded and terminates with the collector. Monitor the
machine during the smoke pair. Stop with `Ctrl-C` if the machine becomes
unresponsive; the partial run is preserved and marked invalid.

## 4. Inspect and validate

Each run appears at:

```text
data/raw/M2_MACOS/<UTC-date>/<run_id>/
```

It contains:

- `telemetry.jsonl`: synchronized host and enriched telemetry;
- `events.jsonl`: collector, workload, and known stressor-onset events;
- `platform.json`: sanitized machine and tool metadata;
- `collection.json`: experiment identity and runtime status;
- `channels.json`: units, semantic groups, sources, and missingness rules;
- `validation.json`: sample, cadence, event, and checksum validation;
- `checksums.sha256`: immutable content hashes;
- workload, stressor, macmon, and xctrace logs;
- optional `xctrace.trace/`.

Validate again at any time:

```bash
python3 scripts/validate_run.py 'data/raw/M2_MACOS/<date>/<run_id>'
```

Do not proceed to production unless both smoke runs report `"valid": true`,
150 samples, usable enriched telemetry, and a stressor-onset event in the
atomic run.

Compare the pair:

```bash
python3 scripts/summarize_smoke.py \
  'data/raw/M2_MACOS/<date>/<nominal-run-id>' \
  'data/raw/M2_MACOS/<date>/<atomic-run-id>'
```

## 5. Optional trace capability run

An all-process Time Profiler trace is much larger than the synchronized
telemetry. A 30-second trace can exceed 100 MB, so do not enable it on every
production run. Use it for a declared representative subset:

```bash
python3 scripts/collect_run.py \
  --platform-id M2_MACOS \
  --workload PY_STATS \
  --scenario NOMINAL \
  --repetition 0 \
  --split smoke \
  --purpose smoke \
  --profile enriched \
  --duration-seconds 30 \
  --sampling-hz 5 \
  --enable-xctrace
```

## 6. Production run example

Commit and push the collector before production; production mode refuses to run
from a dirty checkout. Use a run ID from `data/collection-plan.csv`. For example:

```bash
python3 scripts/collect_run.py \
  --platform-id M2_MACOS \
  --workload PY_STATS \
  --scenario NOMINAL \
  --repetition 1 \
  --split calibration \
  --purpose production \
  --run-id m2_macos__py_stats__nominal__r01 \
  --profile enriched \
  --duration-seconds 720 \
  --sampling-hz 5
```

For an anomalous production run, use `--warmup-seconds 120`. Never reuse a
production run ID. If a run fails validation, preserve it, record the exclusion,
and create a replacement ID.

## 7. Collection order

1. Complete the smoke pair.
2. Collect all M2 repetition-1 nominal cells.
3. Collect repetition-1 development stressors.
4. Collect repetition-2 development runs.
5. Freeze the method before touching repetition-3 locked-test results.
6. Schedule separate long-benign sessions until total valid benign monitoring
   reaches 12 hours.

Raw data are intentionally ignored by Git. Back them up to an access-controlled,
versioned data location before deleting any local copy.
