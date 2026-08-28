# PRISM End-to-End Data Collection Roadmap

> Acquisition reference, not the current paper reproduction checklist.
> The v3 confirmation is complete and reserved evaluation remains closed.
> Use [reproducibility.md](reproducibility.md) for saved figures and tables.

This document is the operator handbook for collecting the journal-extension
dataset. It translates the frozen experiment contract into an ordered workflow
for Apple M2 Pro/macOS and AMD EPYC 9354/Ubuntu.

Use it together with:

- [`extension-collection-contract.md`](extension-collection-contract.md) for
  empirical acceptance criteria;
- [`apple-collection.md`](apple-collection.md) for Apple setup details;
- [`linux-asu-collection.md`](linux-asu-collection.md) for ASU/Linux access,
  storage, and transfer details; and
- [`data-collection.md`](data-collection.md) for the protocol rationale and
  DICE reuse policy.

The canonical operator interface is
`notebooks/PRISM_Complete_Experiment.ipynb`. Files materialized under
`.prism_runtime/` are disposable implementations of notebook cells, not a
second source tree.

## 1. Scope and frozen inventory

PRISM collects new data under one protocol on two required platforms:

| Platform ID | Required host | Operating system | Per-platform plan |
| --- | --- | --- | ---: |
| `M2_MACOS` | Apple M2 Pro/ARM64 | macOS | 126 runs, 32.4 h |
| `EPYC_LINUX` | AMD EPYC 9354/x86-64 | Ubuntu | 126 runs, 32.4 h |

The complete primary plan contains:

- 192 required-matrix runs;
- 36 targeted-extension runs;
- 24 long-benign sessions;
- 252 total runs;
- 64.8 planned machine-hours; and
- 12 planned benign hours on each platform.

The primary matrix crosses four workload families with eight scenarios:

- workloads: `PY_STATS`, `PY_AI`, `BROWSER`, and `VIDEO_SW`;
- scenarios: `NOMINAL`, `ATOMIC`, `BRANCH`, `CACHE`, `MEMBW`, `TLB`,
  `CONTROLLED_CRASH`, and `TELEMETRY_INTERRUPTION`.

Three targeted scenarios run on `PY_STATS` and `PY_AI`:

- `THERMAL_SHIFT` is a workload-induced thermal-condition proxy;
- `POWER_SHIFT` is a workload-induced power-demand proxy; and
- `DEGRADATION_PROXY` progressively changes duty cycle and is not physical
  aging or remaining-useful-life evidence.

`BROWSER` and `VIDEO_SW` are deterministic, network-free web-processing and
software-frame-processing proxies. Do not describe them as measurements of a
specific browser or media application.

## 2. Non-negotiable collection rules

1. **Keep the collection revision fixed.** Production runs must record a clean
   committed Git revision with matching smoke evidence. Notebook outputs and
   documented run switches are execution state; source changes are not.
2. **Use the correct machine.** Run `M2_MACOS` only on the physical Apple host
   and `EPYC_LINUX` only on the authorized EPYC host. A remote notebook runs on
   the remote machine, regardless of which browser displays it.
3. **Do not interact with a host during a run.** Browsing, writing, video calls,
   downloads, backups, updates, or other work changes the host-wide telemetry.
4. **Keep locked tests closed.** `UNLOCK_LOCKED_TEST` remains `False` until the
   method, features, thresholds, calibration policy, and analysis code are
   frozen.
5. **Split by complete run ID.** Never split windows from one trace across
   calibration, development, and test.
6. **Preserve raw evidence.** Do not edit telemetry, events, manifests,
   validation files, or checksums in place. Missing signals remain missing,
   never zero-filled merely for convenience.
7. **Stop on quality failure.** Do not continue a batch after an invalid run,
   schema change, cadence failure, or repository-readiness failure.
8. **Do not commit raw data.** `data/raw/`, progress trackers, processed data,
   and artifacts remain machine-local and Git-ignored.

## 3. Understand the two collection phases

Each required platform has 80 unlocked rows followed by 46 locked-test rows:

| Phase | Required matrix | Targeted extension | Long benign | Total rows | Hours/platform |
| --- | ---: | ---: | ---: | ---: | ---: |
| Calibration/development | 64 | 12 | 4 | 80 | 18.4 |
| Locked test | 32 | 6 | 8 | 46 | 14.0 |
| **Total** | **96** | **18** | **12** | **126** | **32.4** |

The split assignment is predeclared:

- repetition 1 nominal runs are calibration;
- repetition 1 anomalous runs and all repetition 2 runs are development;
- repetition 3 required/targeted runs are locked test;
- the long-benign session split is predeclared in
  `data/collection-plan.csv`.

Finish calibration/development on both platforms before method selection.
Collect locked-test rows only after the method-freeze gate in Section 12.

## 4. Phase 0 — prepare and freeze the collection environment

Perform these steps once for each physical host.

1. Clone or update PRISM to the approved collection commit.
2. Create the Python environment and install notebook dependencies.
3. Open `notebooks/PRISM_Complete_Experiment.ipynb` locally on that host.
4. Run notebook Sections 1–5 to materialize the runtime and pass preflight and
   tests.
5. Keep all operational switches `False` until their documented step.
6. Record the exact commit and do not merge, pull, edit source, or change the
   experiment plan during collection.

Safe defaults are:

```python
RUN_DICE_IMPORT = False
RUN_CAPABILITY_PROBE = False
RUN_SMOKE_PAIR = False
COMPARE_SMOKE_PAIR = False
PREVIEW_NEXT_RUN = False
EXECUTE_PRODUCTION = False
UNLOCK_LOCKED_TEST = False
RUN_DAILY_REPORT = False
```

The tracked `data/collection-plan.csv` is immutable after production starts.
Machine-local state is stored in the ignored
`data/collection-progress.csv`.

## 5. Phase 1 — retain DICE only as a historical baseline

DICE data is not a substitute for the new PRISM Apple data.

1. Freeze the DICE source repository and commit.
2. Import its Apple baseline through notebook Section 6.
3. Preserve the source revision and SHA-256 inventory.
4. Use it to reproduce the conference baseline and run retrospective method
   comparisons.
5. Do not treat its single executions as independent PRISM repetitions or
   cross-platform evidence.

The DICE payload remains outside Git history. Do not copy legacy tier folders
into tracked PRISM paths.

## 6. Phase 2 — capability probe, smoke pair, and cross-platform gate

### 6.1 Probe each platform

On the target host, run notebook Section 7 with its platform ID. Confirm the
hardware, OS, sensor inventory, collector versions, disk capacity, and
permissions.

For Linux, absent CPU-package temperature or power is a capability result, not
a zero. Peripheral temperatures must not be relabeled as CPU temperature.

### 6.2 Run one smoke pair per platform

Run Section 8 on the physical target platform. It collects:

- a 30-second `PY_STATS/NOMINAL` smoke run; and
- a 30-second `PY_STATS/ATOMIC` smoke run with a clean pre-onset window.

The readiness output must end with:

```text
<PLATFORM_ID> is ready for predeclared production collection
```

### 6.3 Match Apple and Linux smoke evidence

Transfer Linux smoke data to the analysis host and run Section 9. The matched
comparison must use the same Git commit and protocol and end with `PASS`.

Smoke data validates instrumentation and schema. It does not count toward the
production tracker or replace independent production repetitions.

## 7. Phase 3 — Apple calibration/development collection

### 7.1 Prepare the Mac before every collection period

- connect AC power;
- keep the lid open;
- prevent system sleep;
- close browsers, editors, video calls, downloads, backups, and updates;
- keep ambient and power conditions reasonably stable; and
- reserve the Mac for collection only.

Do not use a second macOS user session as an isolation mechanism. PRISM records
host-wide activity, so other local sessions still contaminate the trace.

### 7.2 Preview before execution

Use notebook Section 10:

```python
PREVIEW_NEXT_RUN = True
PLATFORM_ID = "M2_MACOS"
RUN_KIND = None
WORKLOAD = None
SCENARIO = None
```

Verify the run ID, platform, split, workload, scenario, duration, cadence,
warm-up, and interruption duration. Reset `PREVIEW_NEXT_RUN=False` after
reviewing the selection.

### 7.3 Execute exactly the selected row

Use Section 11:

```python
EXECUTE_PRODUCTION = True
UNLOCK_LOCKED_TEST = False
```

Wait for both:

```text
Valid PRISM run: ...
Progress updated: ...
```

Then immediately reset `EXECUTE_PRODUCTION=False`.

### 7.4 Use bounded unattended batches only when the Mac is idle

Batching may repeatedly execute the same guarded `collect_next` operation, but
it must:

- omit `--unlock-locked-test`;
- stop on the first nonzero exit or invalid run;
- update and print progress after every valid row;
- preserve a safe pause between rows; and
- keep the machine awake without inviting interactive use.

Use modest matrix batches, for example 30 twelve-minute rows (approximately
six hours), and review quality between batches. Do not collect all long-benign
sessions consecutively merely because batching makes it possible.

If the Mac is needed for other work, use one-row or short batches and use the
Mac only after the batch has ended. Do not interrupt an active production run.

### 7.5 Schedule the four unlocked long-benign sessions

The unlocked phase contains one 48-minute long-benign session per workload.
Spread these sessions across different collection periods and preferably
system restarts. Do not run all four back-to-back.

## 8. Phase 4 — Linux calibration/development collection

### 8.1 Obtain authorization before production

The ASU EPYC host must be in an approved compute allocation or quiet/exclusive
window. A low load average does not itself establish authorization or
experimental isolation. Do not launch production stressors on a shared login
or actively shared host.

Before the approved window, record:

```bash
hostname -f
whoami
date -Is
lscpu
free -h
df -hT / /home
vmstat 1 10
```

Confirm sufficient disk space and no active swapping (`si` and `so` should
remain zero). Preserve the platform snapshot in the run metadata.

### 8.2 Open the notebook on the Linux host

Use an SSH tunnel only to display the remote Jupyter interface. The kernel and
collection code must run from the same PRISM checkout on the EPYC host; the
checkout may live anywhere writable (for example, `/home/<user>/PRISM`). Set
`PRISM_REPO_ROOT` only if Jupyter is launched outside that checkout, and set
`PRISM_DATA_ROOT` when telemetry must reside on a separate approved volume.

Confirm:

```python
PLATFORM_ID = "EPYC_LINUX"
UNLOCK_LOCKED_TEST = False
```

### 8.3 Preview, execute, and report

Follow the same Section 10 preview and Section 11 one-row execution gates used
on Apple. Start with matched `PY_STATS/NOMINAL` calibration/development rows,
then proceed through the predeclared order. Run only inside the authorized
window and stop if another workload compromises isolation.

### 8.4 Respect Linux sensor availability

If CPU-package temperature, CPU power, RAPL/energy, or performance counters are
unavailable, preserve explicit missingness. Do not infer CPU thermal behavior
from NVMe, network-controller, or other peripheral temperature channels.
Targeted thermal and power experiments must be described as workload-induced
condition/demand shifts unless the corresponding CPU measurement exists.

### 8.5 Schedule Linux long-benign sessions across allocations

Spread long-benign sessions across approved time periods or allocations.
This provides temporal and operational variation without mixing unrelated user
activity into a nominal PRISM trace.

## 9. Phase 5 — daily validation, transfer, and backup

### 9.1 Run the daily report after a batch or collection day

Use notebook Section 12 only when no collection cell is active:

```python
RUN_DAILY_REPORT = True
```

Record:

- planned, valid, excluded, and missing rows by platform;
- valid benign hours;
- scenario counts;
- channel availability and missingness;
- warnings and failures; and
- remaining machine-hours.

Then reset `RUN_DAILY_REPORT=False`.

The progress tracker is authoritative for production counts. A quality report
run with smoke included may show additional valid runs and benign minutes that
do not count toward production completion.

### 9.2 Per-run acceptance

A valid run must have:

- the exact predeclared ID, split, duration, cadence, and scenario;
- clean-revision provenance;
- the expected sample count and bounded cadence gaps;
- the required workload/scenario events;
- complete raw/native and sanitized telemetry metadata;
- checksums;
- no validation failures; and
- critical-channel coverage at or above the declared threshold.

Production thresholds are 95% for primary utilization/power channels and 70%
for the known-flaky Apple CPU-temperature channel. Impossible values are nulled
and excluded from coverage rather than silently retained.

### 9.3 Transfer Linux data without deleting either side

After a Linux collection period, copy data to the analysis/backup host using a
checksum-aware, non-deleting transfer. For example:

```bash
rsync -av --partial --checksum \
  <user>@<epyc-host>:~/PRISM/data/raw/EPYC_LINUX/ \
  "/path/to/local/PRISM/data/raw/EPYC_LINUX/"
```

Do not use `--delete`. Revalidate checksums after transfer and retain an
access-controlled second copy of raw data and the progress tracker.

## 10. Interrupted and invalid-run handling

### 10.1 Operator interruption before a run completes

1. Stop the batch; do not continue to later rows.
2. Confirm the tracker did not mark the row valid.
3. Preserve the partial directory in a timestamped rejected-run archive.
4. Record that the attempt was interrupted or contaminated by interactive use.
5. Clear the official raw run-ID path only after the preserved archive is
   verified.
6. Pass readiness again before retrying the predeclared row from the start.

Never present a partial or interactively contaminated trace as paper evidence.

### 10.2 Completed run that fails validation

1. Preserve the failed run and its validation report.
2. Mark the planned row excluded or replacement-required with an explicit
   reason.
3. Create a documented replacement with a new run ID; do not overwrite the
   failed evidence.
4. Keep the replacement in the same split as the failed row.
5. Do not move locked-test evidence into development.

Do not delete failures merely to make aggregate quality reports pass. Reports
may distinguish official raw evidence from a clearly labeled rejected-attempt
archive, but the audit record must remain available.

## 11. Phase 6 — calibration/development completion gate

Before method selection, verify on both platforms:

- every unlocked required-matrix and targeted-extension row is valid or has a
  documented replacement;
- the unlocked long-benign sessions are complete and distributed over time;
- data-quality reports have no unresolved failures;
- Apple and Linux use the same frozen collection protocol;
- DICE baseline reproduction is frozen; and
- locked-test rows remain planned and unseen.

At this point, assemble calibration/development datasets using complete run
IDs. Do not infer that the notebook named “Complete Experiment” already
contains the paper's model fitting and evaluation: the tracked canonical
notebook currently implements collection, validation, and status reporting.
Keep modeling and paper-result generation in a separate analysis workflow so
the collection implementation remains frozen.

## 12. Phase 7 — method development and freeze

Using calibration/development rows only:

1. reproduce the DICE ridge/split-conformal/fixed-persistence baseline;
2. fit and compare platform-local Ridge and VAR micro-twins;
3. implement EWMA/CUSUM and the selected sequential conformal evidence method;
4. select dependence treatment and all block/persistence/evidence parameters;
5. freeze semantic mappings, feature sets, missingness behavior, calibration
   minutes, thresholds, alert logic, diagnosis logic, and abstention policy;
6. freeze guarded-update and adaptive-telemetry claims or remove them from the
   headline scope if their gates fail;
7. record the analysis commit, environment, configuration hashes, and planned
   final metrics; and
8. obtain the method-freeze approval before exposing locked data.

The 12 benign hours per platform are the primary-plan minimum. If the paper
needs a stronger upper confidence bound for a very low false-alert rate,
predeclare additional benign monitoring as a separate supplement. Do not alter
the frozen primary plan after inspecting results.

## 13. Phase 8 — locked-test collection and one-pass evaluation

Only after Section 12 is complete:

1. return each physical collector to the approved frozen collection revision;
2. pass readiness and matching smoke evidence again if the collection revision
   changed;
3. confirm the analysis method is frozen and documented;
4. preview the next locked row;
5. set `UNLOCK_LOCKED_TEST=True` only for the authorized locked collection;
6. collect locked rows without fitting, tuning, threshold changes, or feature
   changes;
7. transfer and validate locked data exactly like earlier data;
8. execute the frozen evaluation once; and
9. report all locked results, including failures and negative outcomes.

Reset `UNLOCK_LOCKED_TEST=False` immediately after the locked collection
period. If a locked run fails technically, follow the replacement protocol
without examining model performance to decide whether to rerun it.

## 14. Phase 9 — final completion checklist

The primary collection is complete only when all boxes below are satisfied.

- [ ] 126 planned/reconciled Apple rows are accounted for.
- [ ] 126 planned/reconciled EPYC rows are accounted for.
- [ ] Each platform has at least 12 valid benign hours.
- [ ] Required and targeted cells have three independent valid repetitions or
      documented replacements.
- [ ] Long-benign sessions are distributed over time/allocations.
- [ ] Locked rows were not used before the method freeze.
- [ ] Every accepted run has manifests, events, channel metadata, validation,
      and checksums.
- [ ] Invalid/interrupted attempts have an explicit audit trail.
- [ ] Platform-specific missing sensors are reported honestly.
- [ ] Raw data and progress state have verified access-controlled backups.
- [ ] DICE is used only as a frozen historical baseline.
- [ ] Paper tables and figures trace back to run IDs and immutable artifacts.

Optional L40S data, guarded online adaptation, and live adaptive-telemetry cost
experiments are P1 supplements. They must not delay or weaken the dual-platform
P0 dataset.

## 15. Git and documentation during active collection

Do not merge documentation or analysis changes into the active collection
branch merely for convenience. A new `HEAD` no longer matches smoke evidence
recorded at the frozen collection commit and therefore requires a new smoke pair
on each platform before more production collection.

Maintain collection documentation on a separate branch or draft pull request
until one of the following is intentional:

- collection pauses and both platform smoke pairs will be repeated on the new
  commit; or
- the documentation is merged after primary collection completes.

This rule applies even when the changed file does not alter sensor code: the
provenance gate deliberately binds production evidence to an exact repository
revision.
