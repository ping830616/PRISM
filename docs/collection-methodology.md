# Historical data-collection methodology

This document explains how the reported PRISM evidence was acquired and how a
reviewer can inspect its provenance. It does not request new experiments.
Collection is disabled by default. For the paper's saved figures and tables,
follow [the reviewer workflow](reviewer-reproduction.md); raw telemetry and a collection
host are not required for that workflow.

The implementation described here is the collection code embedded in
[`PRISM_Complete_Experiment.ipynb`](../notebooks/PRISM_Complete_Experiment.ipynb),
especially Section 2's `workload_harness.py` and `collection.py` cells. The
notebook materializes these cells into a disposable `.prism_runtime/` directory.
That generated directory is not an independent source of historical provenance.
Later `experiments/trel_*` collectors and their phase/freshness smoke tests are
separate work; their measurements must not be attributed to the paper's original
collection.

## Reported inventory versus the original plan

The original [matrix](../configs/experiment-matrix.toml) and
[collection plan](../data/collection-plan.csv) declared 252 runs: 192 required
matrix runs, 36 targeted proxy runs, and 24 long-benign sessions. This was a
64.8 machine-hour plan, including 92 reserved rows. It is not a statement that
252 runs were collected or that every scenario has three admitted repetitions.

The paper instead reports the following inventory:

| Evidence | Runs | Role in the reported v3 study |
| --- | ---: | --- |
| Original admitted inventory | 160 | 8 calibration and 152 development runs; 80 per host |
| Balanced benign supplement | 16 | Additional development evidence |
| Completed v2 benign confirmation | 16 | Its failed confirmation result was preserved before reuse in the separately declared v3 development revision |
| Fresh v3 benign confirmation | 16 | Confirmation of the unchanged v3 candidate only |
| Total outside the reserved partition | 208 | 192 for declared development revisions, 16 for v3 confirmation |

The 92 original reserved rows remain outside these 208; the reported study did
not collect, inspect, or score them. The frozen DICE baseline's 24 historical
cases are also outside this count. DICE supports baseline reproduction and
retrospective comparison, not additional independent PRISM repetitions.
See [paper-results.md](paper-results.md) for the reported denominators and
[data/README.md](../data/README.md) for evidence roles across revisions.

## Hosts, measurements, and sampling cadence

The reported platforms are one Apple M2 Pro host running macOS (`M2_MACOS`,
ARM64) and one AMD EPYC 9354 host running Ubuntu (`EPYC_LINUX`, x86-64).
This is evidence from two physical hosts, not a sample of a fleet.

| Source | Recorded behavior in the embedded collector |
| --- | --- |
| Portable host channels on both hosts | `psutil` supplies CPU activity, memory/swap, load, disk/network counters and rates, process count, and uptime. Canonical portable CPU utilization is the mean of the simultaneously read logical-CPU percentages; the aggregate `psutil` value is retained separately for audit. |
| Apple enriched channels | `macmon pipe -i 200` is requested for a 5 Hz run. Its asynchronous JSON output is preserved in `macmon-raw.jsonl`; each host row copies the latest available sample and sanitizes impossible values. |
| Linux enriched channels | Readable hwmon temperature/power/energy/fan files and powercap energy/power files are sampled through sysfs. CPU frequency uses a bounded, distributed subset of at most four paths, recording discovered and sampled path counts. Values and source/unit metadata are retained in the synchronized telemetry and channel registry. |
| Optional capability | Apple `xctrace` Time Profiler capture is opt-in and recorded per run. Linux `perf` is probed; this does not establish that hardware performance counters were collected. Neither capability should be assumed present in every run. |

The requested **host-loop cadence is 5 Hz**, or one row every 0.2 s. It does
not mean that every native sensor updates independently at 5 Hz. The Apple
collector can reuse a native sample across host rows; reading a Linux sysfs
file likewise does not establish the device's internal update frequency.
`channels.json` records the requested sampling period, not a measured native
refresh guarantee. Native timestamps and original output must be inspected
when making freshness claims. Do not substitute a later extension's measured
native rate for a measurement of these historical runs.

Linux availability is explicit: an absent CPU-package temperature or power
channel stays absent. An NVMe or other peripheral temperature is not a CPU
temperature measurement. Missing or unreadable values remain null, not zero.
The historical Linux implementation does not create an independent raw sysfs
JSONL sidecar analogous to Apple's `macmon-raw.jsonl`.

Each run's `platform.json` records the observed CPU/chip, architecture,
OS/kernel release and version, memory and CPU counts, Python and `psutil`
versions, and probed tool versions. Exact historical versions must be read
from those files; the repository's current dependency installation is not a
substitute. The [source environment snapshot](../reproduction/requirements-source.txt)
is a reproduction reference, not evidence that every collection used that
identical environment. Platform snapshots omit hostname, username, serial
number, and hardware UUID.

## Workloads and controlled scenarios

Each independent execution restarts the workload and collector and has a
unique `run_id`. Workload and pressure harnesses run as separate child
processes. The embedded harness uses seed `830616` where random input is
needed. `PRISM_NUM_THREADS=1` is the declared numerical-library thread setting,
applied to OpenMP, OpenBLAS, MKL, Accelerate, and NumExpr environment variables.
It does not constrain the separately defined contention harness to one thread.
`PRISM_STRESS_MB=128` is the default pressure-buffer setting; the helper bounds
an overridden value to 16–1024 MiB. The recorded environment must be checked
before claiming two runs used identical settings.

| Workload | Exact implemented operation |
| --- | --- |
| `PY_STATS` | Repeated mean, standard deviation, and 95th percentile over an 8,000,000-element `float32` normal array; percentile uses every 16th element and every 1024th value is incremented between iterations. |
| `PY_AI` | Repeated multiplication of two 768 × 768 `float32` matrices followed by `tanh`, rotating the operands. |
| `BROWSER` | A deterministic 512-article HTML document is compressed with zlib level 3, decompressed, sparsely URL-parsed, and SHA-256 hashed. It makes no network requests. |
| `VIDEO_SW` | A seeded 720 × 1280 RGB frame is converted to grayscale, subsampled by two on each spatial axis, compressed/decompressed with zlib level 1, and shifted by one pixel. |

`BROWSER` and `VIDEO_SW` are processing proxies, not measurements of a named
browser, video player, codec, or hardware media decoder. `PY_AI` is a numerical
matrix workload, not a specified trained neural-network application.

| Scenario | Implemented intervention |
| --- | --- |
| `NOMINAL` | Workload runs without an added pressure child or injected interruption. |
| `ATOMIC` | Python threads repeatedly increment a shared counter while holding a `threading.Lock`; thread count is `max(2, logical_cpu_count // 2)`. This is a contention proxy, not an isolated hardware atomic-instruction benchmark. |
| `BRANCH` | Seeded random bits drive an `if`/`elif` arithmetic and bitwise loop. |
| `CACHE` | Random indexed sums over a pressure-sized `float32` array, with up to 1,000,000 indices rotated between iterations. |
| `MEMBW` | Two pressure-sized byte arrays are repeatedly copied, incremented, and exchanged. The setting is per array, not a total process-memory limit. |
| `TLB` | Page-spaced byte locations (4096-byte spacing) are shuffled and updated in chunks. |
| `CONTROLLED_CRASH` | The collector sends `SIGKILL` to its own workload child and records the exit; the host and collector continue. |
| `TELEMETRY_INTERRUPTION` | The synchronized enriched branch is masked for the declared interval; portable host sampling and the research clock continue, then enriched visibility returns. This is an injected data-availability fault, not proof of a real sensor or operating-system failure. |
| `THERMAL_SHIFT` | Repeated 512 × 512 matrix/tanh bursts with 2.0 s active and 0.02 s idle periods. |
| `POWER_SHIFT` | The same burst kernel with 0.35 s active and 0.15 s idle periods. |
| `DEGRADATION_PROXY` | Matrix/tanh duty cycle rises every 30 s: active time starts at 0.10 s, increases by 0.08 s per stage up to 0.90 s, with complementary idle time of at least 0.10 s. |

The first eight scenarios form the full workload matrix. The last three are
targeted to `PY_STATS` and `PY_AI`. Pressure names describe intended mechanisms;
the harness does not establish isolation of a particular microarchitectural
resource. Thermal/power scenarios are workload-induced condition and demand
shifts, not OS power-policy changes. The degradation proxy is not physical
silicon aging, wear-out, or remaining-useful-life evidence.

## Timing and acquisition sequence

Required and targeted production rows request 720 s and 3600 host samples.
Anomalous rows have a 120 s pre-intervention interval. Nominal rows declare
zero intervention warm-up. The telemetry-interruption scenario masks enriched
data for 60 s, nominally from 120 to 180 s. Original long-benign and balanced
supplement sessions last 2880 s (48 min; 14,400 requested samples). Each v2/v3
confirmation session lasts 3900 s (65 min; 19,500 requested samples).

The research clock begins after platform collectors are ready. Interventions
are triggered on the first host-loop iteration at or after the requested
warm-up. `events.jsonl` records the actual relative onset; analysis must use
that event rather than assume an exactly timed 120.000 s transition. A
`stressor_started` event marks child launch, not completion of the child's
allocation/setup. The collector stops its child processes at run completion
and preserves partial evidence on failure.

The documented historical operator sequence is preserved below so a reviewer
can find the controls without enabling them:

| Notebook section | Historical purpose |
| --- | --- |
| 1–5 | Locate checkout, materialize embedded source, wire data/configuration, and run preflight and embedded tests. |
| 7 | Record platform capability with `RUN_CAPABILITY_PROBE`. |
| 8 | Collect 30 s nominal and atomic smoke runs with a 10 s atomic pre-onset interval; invoke `check_collection_readiness.py`. Smoke runs do not count as production repetitions. |
| 9 | Revalidate a selected run or compare valid cross-platform smoke pairs at a shared clean collection commit. |
| 10–11 | Preview a predeclared row, then explicitly execute it with `EXECUTE_PRODUCTION`; reserved selection additionally requires `UNLOCK_LOCKED_TEST`. |
| 12–14 | Summarize progress/quality, state acquisition scope, and audit original calibration/development admission. |
| 17B.5, 17B.6, 17B.8 | Historical supplement and v2/v3 confirmation controls; use the corresponding tracked plans and protocols to interpret their evidence. |
| 17D–17E | Display/rebuild saved paper summaries; these are the reviewer entry points. |

The protocol required idle collection hosts, stable operating conditions, and
an authorized quiet/exclusive Linux allocation. It required a clean collection
revision, successful same-revision smoke checks, and the cross-platform schema
review before production. These are acquisition requirements, not facts proved
solely by a saved plot. The embedded production collector enforces clean Git
state; smoke matching is performed by the separate readiness/comparison steps.
Documented notebook switch changes and execution outputs are excluded from
the source-change comparison. Ordinary source changes are not.

For reproduction, retain the disabled defaults, including
`RUN_CAPABILITY_PROBE=False`, `RUN_SMOKE_PAIR=False`,
`EXECUTE_PRODUCTION=False`, and `UNLOCK_LOCKED_TEST=False`, and leave supplement,
confirmation, redesign, and method-freeze execution disabled. The historical
[Apple guide](apple-collection.md), [Linux guide](linux-asu-collection.md),
[roadmap](data-collection-roadmap.md), and
[original contract](extension-collection-contract.md) explain the acquisition
procedure; their imperative instructions and full-plan targets are not the
current paper reproduction checklist.

## Per-run evidence, checksums, and validation

Run folders use `data/raw/<platform_id>/<UTC-date>/<run_id>/`, under the
selected `PRISM_DATA_ROOT` when external data are supplied.

| File | Audit purpose |
| --- | --- |
| `telemetry.jsonl` | Sequence number, UTC/monotonic-relative time, portable host channels, sanitized enriched values, and availability/quality flags. |
| `macmon-raw.jsonl` on Apple | Original native JSON lines, including values later nulled in the synchronized output. |
| `events.jsonl` | Collector/workload lifecycle, intervention onset/recovery, completion/failure, and child exits. |
| `platform.json` | Sanitized observed hardware, OS, Python/package, and tool metadata. |
| `collection.json` | Run identity, scenario, split, requested timing, profile, command, Git revision/dirty status, workload settings, quality contract, completion/error state, and collection CPU/byte costs. |
| `channels.json` | Channel names, units, semantic groups, sources, requested period, and missingness rules; Linux native source metadata. |
| `validation.json` | Validation outcome, failures/warnings, sample count/span, critical-channel coverage, quality flags, and whether hashes were checked. |
| `checksums.sha256` | SHA-256 hashes of run files, including logs and any optional trace files; excludes the manifest itself and `validation.json`. |
| Logs and optional `xctrace.trace/` | Workload/stressor/native collector diagnostics and opt-in trace output. |

The embedded validator checks required files, exact expected row count,
strictly increasing relative times, completed collection state, scenario
events, and checksum targets. At 5 Hz it accepts a median sample interval
between 0.1 and 0.3 s, rejects a gap above 0.6 s, and checks the observed span
against `(expected_samples - 1) / sampling_hz` with tolerance
`max(0.5 s, 5% of expected span)`. The collection loop separately aborts if it
falls more than five periods behind after startup. These bounds concern host
rows, not independent native refreshes.

For production, critical portable CPU/memory/load channels and applicable
Apple power/utilization channels require at least 95% valid coverage. Apple
CPU-temperature coverage requires at least 70%. Impossible Apple temperature
values outside 15–125 °C, negative power, and out-of-range normalized usage
are nulled and flagged. Declared interruption rows are excluded from the
critical-channel coverage denominator. For controlled crashes, Apple CPU
temperature is assessed before injection; its post-crash impossible-value
flags remain recorded as expected control effects. Other critical channels
retain their applicable full-run coverage requirements. More than 25% of
rows carrying gating quality flags fails validation.

For an existing admitted run, the following commands inspect records and
check file integrity without collecting or rewriting its validation report.
Use the supplied run directory in place of the placeholder:

```bash
cd "/path/to/existing/run_id"
jq '{run_id, platform_id, workload, scenario, planned_split, duration_seconds,
     sampling_hz, warmup_seconds, interruption_seconds, status, software,
     workload_protocol}' collection.json
jq '{valid, failures, warnings, sample_count, expected_samples,
     duration_observed_seconds, checksums_verified}' validation.json
shasum -a 256 -c checksums.sha256
```

On Linux, `sha256sum -c checksums.sha256` provides the corresponding manifest
check. The notebook's Section 9 `VALIDATE_RUN` path invokes `validate_run.py`,
which **refreshes `validation.json`**. Preserve the archived report and use a
separate working copy if rerunning that path. A checksum pass establishes
agreement with the supplied manifest; it does not independently authenticate
the origin of that manifest or prove that the current notebook's generated
runtime bytes were the bytes executed historically. Establishing historical
software provenance requires the run's recorded collection revision and the
corresponding archived source and records.

## Admission, exclusions, and evidence gates

The immutable plans declare identities and roles; ignored progress trackers
record execution status and exclusions. They are separate artifacts. An
admission audit reconciles the appropriate tracker, raw folder, collection
record, validation outcome, and manifest for each complete run. The original
Section 14 audit requires 80 valid original runs per host (4 calibration and
76 development), rejects already-valid reserved rows and duplicate production
run IDs, checks split agreement and clean collection provenance, and records
a fingerprint of platform, run ID, split, collection commit, and manifest
hash. Its balanced-supplement path admits all eight supplement runs per host
or fails; it does not select a favorable subset. Full raw reanalysis requires
the explicit `VERIFY_ALL_RAW_CHECKSUMS` check in addition to saved validity.
Later revisions add the separately declared evidence described above.

The original plan assigns repetition-1 nominal matrix rows to calibration,
repetition-1 anomalous and repetition-2 rows to development, and repetition-3
matrix/targeted rows to reserved evaluation. Long-benign assignments are in
the CSV plan. A complete run retains one role within an analysis revision;
windows from one execution cannot be distributed across fitting and its
excluded evaluation fold. Re-windowing creates no new independent runs.

Interrupted, contaminated, or technically invalid attempts must be preserved
with their exclusion reason. A replacement needs a distinct recorded identity
and the same split/fold as the failed row. Neither an alert nor a missed event
is a permissible reason to remove an otherwise admissible run. The paper's
80-valid/0-invalid-per-host original inventory describes the admitted set;
it is not evidence that no failed acquisition attempts ever occurred.

The [balanced supplement protocol](../configs/development-benign-supplement.toml)
declares 16 nominal 48-minute sessions, with complete-run fold assignments.
The [v2](../configs/v2-independent-confirmation.toml) and
[v3](../configs/v3-independent-confirmation.toml) confirmation protocols each
declare a separate set of 16 nominal 65-minute sessions, two per workload per
host. Their plan rows retain `planned_split=development`; the separate
`run_kind`, plan, and analysis firewall establish their confirmation role.
The v3 confirmation IDs must not enter v3 fitting, search, or threshold
selection. Reuse in a later explicitly declared development revision does
not create another independent confirmation.

The 120 s analysis startup exclusion is distinct from acquisition warm-up.
For each 65-minute confirmation session it leaves 63 eligible minutes,
yielding 16.80 h across 16 runs when all eligible time is valid. The
predeclared confirmation requires all sessions, at least 95% valid monitoring
per run, and the 0.25 false-alerts/hour criterion on pooled, platform, and fold
views, while retaining the frozen development detection requirement. It is
benign-only confirmation and cannot re-estimate controlled-event detection.

v2 recorded 17 false-alert episodes over 16.80 h. The fresh v3 set recorded
6 over 16.80 h (0.357/hour), exceeding its limit. Development feasibility did
not overturn that failure. Final method freeze and reserved evaluation remain
closed, and the paper requires no additional confirmation collection. All
telemetry was acquired continuously; the reported adaptive-telemetry duty
cycle comes from offline replay, not measured collection or energy savings.

Bundled summaries allow paper reproduction, while raw-byte revalidation also
needs externally supplied raw runs, manifests, progress trackers, recorded
source revisions, and exclusion records. Their absence should be reported as
an access limitation, not repaired by recollecting the experiment or silently
substituting later runs. Follow the
[recorded analysis sequence](drift-aware-analysis.md) for a separately stored
raw reanalysis.
