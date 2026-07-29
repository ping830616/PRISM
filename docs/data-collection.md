# PRISM Data Collection Protocol

## What to Reuse from DICE

Reuse the DICE Apple M2 Pro dataset for two purposes only:

1. reproduce the conference baseline from its exact source revision; and
2. run retrospective comparisons of new sequential scoring methods on the
   original 24 cases.

The imported baseline contains four workloads, one nominal condition and five
stressor conditions, with one recorded execution per workload/condition cell.
It is therefore a historical baseline, not independent replication and not
evidence of cross-platform portability.

PRISM must collect new traces on both required platforms under a common,
predeclared protocol. At least some new M2 traces are essential: comparing old
M2 data with newly collected EPYC data alone would confound platform with
collection date, software version, protocol implementation, and environment.

## Local DICE Import

Run from the PRISM repository:

```bash
python3 scripts/import_dice_baseline.py --dice-root ../DICE
```

The raw payload remains outside Git history. `source.json` records the DICE
remote and commit, while `local-files.sha256` makes the local copy auditable.
Compact mixed/full result summaries are tracked as frozen baseline evidence.

## Required New Collection

The required full-cross-product matrix contains:

- 2 platforms: Apple M2 Pro/macOS and AMD EPYC 9354/Ubuntu;
- 4 workload families: `PY_STATS`, `PY_AI`, `BROWSER`, and `VIDEO_SW`;
- 8 required scenarios: nominal, five pressure mechanisms, controlled crash,
  and telemetry interruption;
- 3 independent executions per platform/workload/scenario cell.

This is 192 planned executions. At 720 seconds per execution it represents 38.4
machine-hours. To fulfill the extension memo without inflating every
workload/scenario combination, PRISM additionally requires thermal shift, power
shift, and progressive degradation-proxy runs on `PY_STATS` and `PY_AI`. Those
36 targeted runs add 7.2 machine-hours.

The 24 long-benign supplement sessions add 19.2 machine-hours. The frozen plan
therefore contains 252 rows and 64.8 machine-hours before setup, cooldown, and
invalid reruns. Running the two platforms in parallel reduces wall-clock time.

Five repetitions are preferred, but scenario breadth must be reduced before
replication falls below three. If collection pressure is severe, retain all
nominal cells and all five DICE-compatible stressors, then run controlled crash
and telemetry interruption on two representative workloads per platform.
Document this reduced matrix before inspecting final results.

## Independence Rules

An independent repetition must restart the workload and collector and receive a
new `run_id`. Re-windowing one trace or changing a random seed during analysis
does not create an independent experimental run.

Use the generated plan:

```bash
python3 scripts/make_collection_plan.py
```

The plan assigns:

- repetition 1 nominal runs to `calibration`;
- repetition 1 anomalous runs and all repetition 2 runs to `development`;
- repetitions 3 and above to `locked_test`.

If a planned run fails quality checks, preserve its record with an exclusion
reason and collect a replacement with a new run ID. Do not move a locked-test
run into development.

## Per-Run Procedure

1. Record `platform.json`: hardware, OS/kernel, firmware, drivers, power mode,
   collector versions, and available telemetry channels.
2. Record `collection.json`: run ID, workload, scenario, repetition, split,
   command lines, start/end timestamps, sampling cadence, and known event onset.
3. Start collectors and verify monotonic timestamps before workload launch.
4. Run the workload and scenario for the declared duration without interactive
   intervention.
5. Stop collectors cleanly and record exit statuses and collection failures.
6. Generate `checksums.sha256` for every raw file.
7. Run schema, row-count, timestamp, missingness, and unit checks.
8. Mark the run `valid`, `excluded`, or `replacement_required` in
   `data/collection-plan.csv`.

## Telemetry Mapping

Preserve native channels and map them into functional groups:

| Functional group | M2/macOS examples | EPYC/Linux examples |
| --- | --- | --- |
| Compute | CPU usage, load, frequency exposure | `/proc/stat`, load, `perf` counters |
| Memory | used/swap, page activity | `/proc/meminfo`, `vmstat`, memory bandwidth proxy |
| I/O | disk/network rates | `/proc/diskstats`, network counters |
| Thermal/power | `powermetrics` power/temperature | `lm-sensors`, RAPL/energy counters |
| Accelerator | GPU/ANE usage if exposed | GPU telemetry only when present |
| Availability | collector gaps and missing channels | collector gaps and missing channels |

Do not force platform-specific channels to appear equivalent. Every mapped
channel must retain its native name, units, collector, cadence, missingness
semantics, and transformation. An unavailable signal is missing—not zero.

## Long-Benign Collection

Collect at least 12 aggregate benign hours per required platform. The
predeclared plan supplies 2.4 hours through the 12-minute nominal matrix runs
and 9.6 hours through three 48-minute sessions for each workload. Spread the
sessions across system restarts or allocations and time periods.

Report:

- total monitored benign hours and number of independent sessions;
- persistent alerts and block alerts per hour;
- confidence intervals for false-alert rates;
- collector interruptions separately from detector alerts.

## Daily Quality Gate

At the end of each collection day, freeze:

1. expected, valid, excluded, and missing run counts by platform;
2. benign hours accumulated;
3. channel availability and missingness report;
4. invalid-run reasons and replacement IDs;
5. remaining machine-hours to Gate G2.

Do not wait until the end of the collection period to discover an incompatible
schema or a silent collector failure.
