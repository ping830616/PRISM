# Research and Submission Plan

Target submission date: **August 30, 2026**

Planning date: **July 27, 2026**

## Status amendment — August 24, 2026

The original full-extension success definition below has not been met. The
frozen v3 detector failed independent benign confirmation at 0.357 false
alerts/hour, and the bounded v4 analysis found no operating point meeting both
G3 limits. Post-hoc nested temporal validation reached 65.0% detection but
0.327 false alerts/hour. A final bounded 36-candidate semantic-corroboration
redesign also failed the stricter development margin: its best-detecting point
reached 13.3% detection at 0.056 false alerts/hour. The stopping rule is now
active, and the 92 locked rows remain sealed.

The current defensible submission scope is a transparent pre-lock reliability
study: dual-platform collection and semantics, behavioral digital-micro-twin
monitoring, explicit telemetry-fault handling, preserved negative
confirmation, G3 boundary analysis, post-hoc nested complete-run temporal
sensitivity, and the recorded final-redesign stopping decision. This amendment
does not redefine a failure as success and does not permit
favorable-result-only reporting. No further detector tuning or confirmation
collection is planned for this manuscript. A later confirmatory study may use
the locked rows only after a new method is frozen and independently confirmed.

## Success Definition

Submit a journal manuscript whose central result is:

> A host-side behavioral micro-twin can be calibrated across heterogeneous platforms and monitored sequentially with measurable long-horizon false-alert behavior, while preserving useful anomaly detection and diagnosis.

The manuscript is submission-ready only if:

- the Apple M2 Pro and AMD EPYC studies use a shared written protocol;
- each headline result is based on independent repeated runs;
- the final detector is evaluated on locked runs not used for fitting, calibration, or tuning;
- false alerts are reported per monitored hour with confidence intervals;
- the journal-to-conference difference table demonstrates substantial new technical material;
- code, manifests, and paper values agree.

## Scope Priority

### P0 — required

1. Common functional telemetry schema and platform adapters.
2. Apple M2 Pro/macOS and AMD EPYC/Linux data under the same workload/scenario protocol.
3. Original DICE baseline reproduced from a clean environment.
4. Sequential evidence baseline comparison.
5. Independent-run evaluation and uncertainty analysis.
6. Long benign monitoring, controlled crash, and telemetry-interruption cases.

### P1 — include only after P0 passes

1. Guarded benign-only recalibration with quarantine, contamination screening, and rollback.
2. Host-side telemetry escalation using diagnostic uncertainty or evidence thresholds.
3. NVIDIA L40S/DCGM or NVML telemetry as a clearly labeled accelerator case.

### Explicitly out of scope

- RTL/FPGA synthesis, fixed-point datapaths, or area/power claims;
- causal feature-ranking novelty;
- fleet-scale claims from two machines;
- physical defect localization below the host-visible subsystem path;
- remaining useful life or aging prediction without real longitudinal aging labels;
- a claim that PRISM invents conformal martingales or e-processes.

## Calendar and Gates

### July 27–29 — Freeze the paper contract

- Confirm title, author list, target journal, and relationship to the accepted ITC paper.
- Freeze the P0 contributions and the DICE/CITADEL boundary.
- Inventory available M2, EPYC, and optional L40S sensors.
- Define a common workload/scenario protocol and platform metadata.
- Create the journal-vs-conference difference table before implementation.

**Gate G0 — July 29:** Krish approves one-sentence thesis, three P0 contributions, experiment matrix, and venue.

### July 30–August 2 — Build and smoke-test the dual-platform pipeline

- Implement platform adapters and the shared semantic schema.
- Port the workload and stressor harness to Linux.
- Run nominal and one anomaly smoke case on each platform.
- Verify timestamps, sampling cadence, missing-channel handling, and immutable manifests.
- Run original DICE end to end and freeze the baseline outputs.

**Gate G1 — August 2:** both platforms produce analyzable traces under the same protocol. If EPYC access is unavailable, substitute an identified x86-64 Linux host immediately and state the change.

### August 3–9 — Collect the primary dataset

- Run the locked matrix with at least three independent repetitions per platform/workload/scenario cell; five are preferred.
- Collect at least 12 aggregate benign monitoring hours per platform.
- Collect controlled crash and telemetry-interruption cases.
- Record collector CPU time, bytes per second, missingness, and collection failures.
- Materialize one data-quality report per platform.

**Gate G2 — August 9:** required cells have at least three valid independent runs and the benign-hour target is met. No method development may use the locked test runs.

### August 10–15 — Implement and select the core method

- Fit platform-local ridge and VAR micro-twins.
- Implement original DICE split-conformal threshold plus persistence.
- Add EWMA/CUSUM and one established conformal test-martingale/e-process.
- Use block calibration or another explicitly justified dependence treatment.
- Select the method on development runs using a predeclared utility:
  - detection at a fixed false-alert/hour budget;
  - median time-to-detect;
  - calibration and compute cost.
- Measure within-platform, zero-shot semantic transfer, and few-shot recalibration.

**Gate G3 — August 15:** PRISM must improve long-horizon false-alert behavior or detection delay at a matched operating point. If it does not, the sequential method becomes an analysis tool rather than the headline novelty.

### August 16–20 — Secondary contributions and ablations

- Test guarded online updates against benign drift and anomaly-contaminated update windows.
- Test rollback recovery and model-staleness alarms.
- Evaluate host-side telemetry escalation against always-mixed and always-full profiles.
- Add L40S telemetry only if the full P0 matrix is already complete.

**Gate G4 — August 20:** freeze all algorithmic claims. Any unpassed P1 experiment moves to future work.

### August 21–24 — Final runs and result freeze

- Execute the locked test evaluation once.
- Generate confidence intervals using independent runs or run-level bootstrap.
- Produce final figures, tables, ablations, and failure-case analysis.
- Audit every number from manuscript to CSV and run manifest.
- Create a complete journal-vs-ITC contribution and text-reuse disclosure.

**Gate G5 — August 24:** passed as a scope-freeze decision. No new model tuning,
confirmation collection, or locked access; results and paper outline are frozen.

### August 25–27 — Manuscript and advisor review

- Complete abstract, introduction, related work, methods, experiments, limitations, and conclusion.
- Explain assumptions behind sequential validity and temporal dependence.
- State that subsystem-path evidence is not transistor- or physical-defect localization.
- Send Krish a complete PDF plus the difference table and reproducibility checklist.

**Gate G6 — August 27:** advisor-ready full draft with all figures and tables.

### August 28–30 — Submission QA

- Resolve advisor comments without expanding the research scope.
- Run clean-clone reproduction for the headline artifacts.
- Check IEEE style, figure legibility, references, author metadata, and prior-publication disclosure.
- Prepare cover letter and supplemental artifact instructions.
- Submit by August 30 and tag the exact submitted commit privately.

## Experiment Design

### Platforms

- `M2_MACOS`: Apple M2 Pro/ARM64/macOS; host-level telemetry.
- `EPYC_LINUX`: AMD EPYC 9354/x86-64/Ubuntu; host-level and standard Linux telemetry.
- `L40S_OPTIONAL`: NVIDIA L40S telemetry through documented APIs; never required for P0.

### Workload families

Use comparable functions rather than identical binaries when necessary:

- CPU statistics/analytics;
- AI inference or training micro-workload;
- browser/web workload;
- software video or media workload.

### Scenario families

- nominal;
- atomic/synchronization pressure;
- branch pressure;
- cache pressure;
- memory-bandwidth pressure;
- address-translation/TLB pressure;
- controlled crash;
- telemetry interruption;
- thermal/power policy shift or another non-destructive degradation proxy.

### Minimum replication

- Minimum: 3 independent runs per required cell.
- Preferred: 5 independent runs per required cell.
- Long benign traces: at least 12 aggregate hours per platform across workload and time-of-day variation.
- Test partition: locked by complete run IDs before method selection.

## Required Baselines and Ablations

1. DICE ridge micro-twin + split conformal + fixed persistence.
2. Static VAR micro-twin + fixed persistence.
3. Static micro-twin + EWMA or CUSUM.
4. Static micro-twin + established sequential conformal evidence.
5. PRISM without platform semantics.
6. PRISM without dependence handling.
7. If used: unguarded versus guarded online updates.
8. If used: always-mixed, always-full, and adaptive telemetry escalation.

## Required Metrics

### Detection and operational reliability

- anomalous-run detection rate;
- event-level precision/recall where event labels exist;
- false alerts per monitored hour and per 100 monitored hours;
- average run length to false alarm;
- median and distribution of time-to-detect;
- detection probability by a fixed time budget;
- run-level confidence intervals and sample counts.

### Portability

- within-platform performance;
- zero-shot cross-platform semantic transfer;
- few-shot calibration curve versus benign calibration minutes;
- calibration wall time and required benign data;
- performance drop caused by unavailable versus shifted telemetry.

### Diagnosis

- macro-F1 and balanced accuracy;
- top-1/top-2 accuracy;
- selective coverage, abstention rate, and accuracy at retained coverage;
- subsystem-path stability across repetitions and platforms.

### Cost

- average active channels;
- telemetry bytes per second;
- collector CPU time and memory;
- escalation duty cycle;
- optional energy estimate with clearly documented measurement method.

### Adaptation safety, if included

- false-alert rate before and after benign drift;
- anomaly sensitivity before and after update;
- contaminated-update acceptance rate;
- rollback recovery time;
- number of rejected or quarantined updates.

## Kill and Fallback Rules

- **No second platform by August 2:** substitute a documented x86-64 Linux host or move the submission date. Do not make a cross-platform claim from software reruns on one machine.
- **Insufficient independent repetitions by August 9:** reduce workloads or scenario breadth before reducing replication.
- **No sequential benefit by August 15:** retain original DICE alerting and make platform transfer plus long-horizon reliability the core paper.
- **Online update unsafe by August 20:** remove it from the contribution list and report the negative result or limitation.
- **L40S data late:** omit it from the paper; provide a post-submission artifact branch later.
- **Conflict with CITADEL:** PRISM keeps host-side reliability evidence; CITADEL keeps hardware-aware EDA and implementation claims.

## Daily Coordination

Send Krish a five-line update each working day:

1. completed artifact;
2. current result with denominator;
3. blocker;
4. decision needed;
5. next 24-hour deliverable.

Every gate review should use artifacts, not verbal status: CSV, figure, manifest, paper section, or reproducible command.
