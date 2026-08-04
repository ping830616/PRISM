# PRISM

**PRISM: Platform-Robust In-Field Sequential Monitoring for Silicon Lifecycle Management**

PRISM is the proposed journal extension of the DICE host-side monitoring study. It asks a focused question:

> Can a behavioral micro-twin provide reliable, statistically calibrated in-field monitoring across heterogeneous host platforms without requiring identical telemetry channels?

The repository is intentionally private-ready while the work is unpublished.
It contains the research plan, experiment contract, paper outline, and one
canonical, executable notebook for the complete experiment. Raw telemetry may
be imported locally but is not tracked in Git.

## Journal Thesis

PRISM maps platform-specific host telemetry into a common functional representation, fits a benign-only behavioral micro-twin per platform, and converts temporally dependent residual blocks into sequential evidence. Its evaluation emphasizes:

1. cross-platform calibration and transfer between Apple M2 Pro/macOS and AMD EPYC/Linux;
2. false alerts per monitored hour and time-to-detect under repeated, temporally dependent testing;
3. calibration effort on a newly observed platform;
4. robustness to benign drift, controlled crashes, and telemetry interruption;
5. optional host-side telemetry escalation when richer evidence is needed.

The proposed primary venue is **IEEE Transactions on Reliability**. The paper should be written as a reliability-monitoring contribution, not as a new conformal-inference theory paper.

## Relationship to Existing Projects

- **DICE (ITC):** conference baseline—host-side behavioral micro-twin, residual block scoring, split-conformal thresholds, and fixed persistence on Apple M2 Pro.
- **PRISM:** journal extension—cross-platform host telemetry semantics, repeated long-horizon evaluation, and sequential reliability evidence.
- **CITADEL:** separate TCAD direction—hardware-counter analytics, causal/stable feature selection, hardware-aware design-space exploration, fixed-point/RTL/FPGA validation, and lifecycle monitor synthesis.

PRISM must not absorb CITADEL's hardware novelty. In particular, PRISM does not claim RTL synthesis, on-chip feature ranking, fixed-point cost, or FPGA validation.

## Critical-Path Scope

The August 30 submission path has three required contributions:

1. **Platform-semantic telemetry contract**
   - Functional groups: compute, memory, I/O, thermal/power, accelerator, and availability.
   - Platform adapters preserve missingness and provenance; unavailable counters are never filled with arbitrary zeros.
2. **Dependence-aware sequential monitoring**
   - Compare original DICE fixed persistence with CUSUM/EWMA and an established conformal test-martingale or e-process.
   - Report operational reliability metrics, especially false alerts per monitored hour.
3. **Repeated dual-platform study**
   - Independent runs, long benign traces, workload holdout, platform transfer, controlled crashes, and telemetry interruptions.

Safe online micro-twin updates and adaptive telemetry escalation are secondary contributions. They enter the paper only if their result gates pass by August 20.

## Repository Map

- `docs/research-plan.md`: schedule, owners, gates, and fallback rules.
- `docs/data-collection.md`: DICE reuse policy and the new PRISM collection protocol.
- `docs/data-collection-roadmap.md`: ordered Apple/Linux operator handbook from
  environment freeze through locked-test completion.
- `docs/extension-collection-contract.md`: executable acceptance mapping from the extension memo to required evidence.
- `docs/apple-collection.md`: notebook-only Apple M2 setup, smoke test, and production workflow.
- `docs/linux-asu-collection.md`: detailed ASU EPYC preparation, collection, validation, and transfer.
- `docs/novelty-boundary.md`: claim matrix and separation from DICE/CITADEL.
- `configs/experiment-matrix.toml`: machine-readable experiment design.
- `data/README.md`: immutable data layout and provenance rules.
- `paper/outline.md`: journal narrative and required tables/figures.
- `notebooks/PRISM_Complete_Experiment.ipynb`: canonical source for collection,
  validation, tests, DICE import, status reporting, and guarded production
  execution.

## Quick Start

```bash
python3 -m venv .venv
source .venv/bin/activate
python3 -m pip install -e ".[notebook]"
jupyter lab notebooks/PRISM_Complete_Experiment.ipynb
```

Run the notebook from top to bottom once. It reconstructs its embedded modules,
scripts, and tests under the Git-ignored `.prism_runtime/` directory, then runs
the preflight and unit-test gates. The operational sections are guarded by
boolean switches, so **Run All does not start hardware probes, smoke runs, DICE
imports, or production collection by default**.

Start with the Apple smoke workflow in `docs/apple-collection.md`. Every PRISM
run writes synchronized telemetry, events, sanitized platform metadata, channel
metadata, validation, and checksums into the Git-ignored `data/raw/` tree. Use
the notebook's operator-facing controls only: section 7 probes the current
platform, section 8 detects the platform and runs the complete smoke pair plus
readiness gate, section 9 automatically compares matched Apple/Linux smoke
evidence from one collection commit, sections 10–11 preview and execute
production rows, and section 12 reports collection quality. Do not run
files under `.prism_runtime/` manually. Locked-test rows remain unavailable
until explicitly unlocked after the method freeze.

The notebook is the only tracked Python source. Its runtime materialization is
disposable and can be regenerated by rerunning the setup/source cells. Never
edit `.prism_runtime/` as the changes will be overwritten; edit the
corresponding notebook cell instead.

The DICE import keeps the 124 MB raw Apple M2 baseline in an ignored local
payload directory. It tracks the source revision, SHA-256 inventory, and compact
result summaries without duplicating gigabytes of tuning artifacts in Git.

## Data Collection at a Glance

### Dataset comparison

| | Legacy DICE Apple data | New PRISM Apple data | New PRISM AMD data |
| --- | --- | --- | --- |
| Machine | Apple M2 Pro, ARM64/macOS | Apple M2 Pro, ARM64/macOS | AMD EPYC 9354, x86-64/Ubuntu |
| Role | Historical conference baseline | New same-protocol Apple evidence | New cross-platform Linux evidence |
| Scale | 24 cases; one execution per workload/condition | 126 planned runs; 32.4 machine-hours | 126 planned runs; 32.4 machine-hours |
| Workloads and conditions | Four workloads; nominal plus five pressure conditions | Four workloads; eight required and three targeted scenarios | Same PRISM workload/scenario plan as Apple |
| Repetition | No independent replication within each case | Three independent runs per required/targeted cell | Three independent runs per required/targeted cell |
| Benign monitoring | Limited | 12 planned hours | 12 planned hours |
| Telemetry | Apple-specific mixed/full tiers | Portable and Apple-native host channels | Portable and Linux-native host channels; unavailable sensors stay missing |

### Procedure, method, and settings

| Step | Procedure | Main method or setting |
| ---: | --- | --- |
| 1 | Prepare each physical machine and run notebook preflight | Use one approved, clean Git revision |
| 2 | Run nominal and anomalous smoke traces, then compare platforms | 30 seconds at 5 Hz; readiness must pass |
| 3 | Collect calibration and development runs while the host is idle | 12-minute runs at 5 Hz; 120-second anomaly warm-up; locked tests remain closed |
| 4 | Collect benign monitoring across different times/restarts | Three 48-minute sessions per workload; 12 benign hours per platform overall |
| 5 | Validate every run and back up raw evidence | Check cadence, coverage, events, manifests, and SHA-256 checksums |
| 6 | Freeze models, features, thresholds, and analysis choices | Never tune with locked-test runs |
| 7 | Collect and evaluate the locked test once | Unlock only after method freeze; report all outcomes |

See the [end-to-end collection roadmap](docs/data-collection-roadmap.md) for
the complete operator procedure.

## Reproducibility Rules

- Split by independent run, never by windows from the same run.
- Tune only on development runs; keep the final platform/workload test partition locked.
- Treat repeated seeds on one trace as computational sensitivity, not independent experimental replication.
- Record raw data immutably and derive processed tables with hashes and manifests.
- Report confidence intervals and denominator counts with every headline rate.
- Cite the ITC DICE paper and include a submission-time table that identifies every new journal contribution.

## Publication Status

Working research repository. Do not make public, archive a release, or add a code/data license until the authors and advisor approve the publication plan.
