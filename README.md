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

## PRISM Research Flow

![PRISM research pipeline: historical and new cross-platform data are harmonized, modeled, monitored, and evaluated before locked testing](docs/assets/prism-research-flow.svg)

The historical DICE data provides a baseline; the new Apple and AMD runs test whether the same monitoring method remains reliable across different platforms and sensor capabilities.

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
- `docs/drift-aware-analysis.md`: portable, guarded robust-normalization and
  adaptive-VAR execution sequence, G3 rule, and current development checkpoint.
- `docs/extension-collection-contract.md`: executable acceptance mapping from the extension memo to required evidence.
- `docs/apple-collection.md`: notebook-only Apple M2 setup, smoke test, and production workflow.
- `docs/linux-asu-collection.md`: detailed ASU EPYC preparation, collection, validation, and transfer.
- `docs/novelty-boundary.md`: claim matrix and separation from DICE/CITADEL.
- `configs/experiment-matrix.toml`: machine-readable experiment design.
- `data/README.md`: immutable data layout and provenance rules.
- `paper/outline.md`: journal narrative and required tables/figures.
- `paper/abstract-prelock.md`: evidence-aligned abstract and publication claim
  boundary for the current pre-lock manuscript.
- `notebooks/PRISM_Complete_Experiment.ipynb`: canonical source for collection,
  validation, tests, DICE import, dual-platform semantic preprocessing,
  ridge/VAR micro-twins, sequential method selection, transfer calibration,
  and the guarded method freeze.

## Portable Quick Start

Clone PRISM into any writable directory on the Mac or Linux server. If the
repository is already present, start at `cd PRISM`.

```bash
git clone https://github.com/ping830616/PRISM.git
cd PRISM
python3 -m venv .venv
source .venv/bin/activate
python3 -m pip install -e ".[notebook]"

# Portable paths
export PRISM_REPO_ROOT="$PWD"
export PRISM_DATA_ROOT="${PRISM_DATA_ROOT:-$PWD/data}"

# Reproducible PRISM protocol
export PYTHONHASHSEED=0
export PRISM_NUM_THREADS=1
export PRISM_STRESS_MB=128
export MPLCONFIGDIR="$PWD/.mplconfig"
export OMP_NUM_THREADS="$PRISM_NUM_THREADS"
export OPENBLAS_NUM_THREADS="$PRISM_NUM_THREADS"
export MKL_NUM_THREADS="$PRISM_NUM_THREADS"
export VECLIB_MAXIMUM_THREADS="$PRISM_NUM_THREADS"
export NUMEXPR_NUM_THREADS="$PRISM_NUM_THREADS"
export BLIS_NUM_THREADS="$PRISM_NUM_THREADS"
mkdir -p "$MPLCONFIGDIR" "$PRISM_DATA_ROOT"

# Open the one canonical experiment notebook
python -m jupyter lab notebooks/PRISM_Complete_Experiment.ipynb
```

The notebook is portable across macOS and Linux and always uses the active
Jupyter kernel's Python executable. It discovers the checkout automatically,
so the repository does not need a particular folder name or home directory.
To keep large telemetry on a separate local or server volume, add
`PRISM_DATA_ROOT` **before** starting Jupyter:

```bash
export PRISM_DATA_ROOT="/absolute/path/to/prism-data"  # optional
mkdir -p "$PRISM_DATA_ROOT"
python -m jupyter lab \
  "$PRISM_REPO_ROOT/notebooks/PRISM_Complete_Experiment.ipynb"
```

`PRISM_DATA_ROOT` defaults to `<repository>/data`. The setup cells link the
disposable runtime to that selected data location, while collection and
analysis continue to use the same notebook controls. Python 3.10 or newer is
required. `PRISM_NUM_THREADS=1` and `PRISM_STRESS_MB=128` are recorded workload
settings and must stay fixed across Apple and Linux collection. The remaining
exports make hashing, numerical-library threading, and figure configuration
reproducible. The automatic integrity section rejects embedded Mac/ASU paths
and checks that the runtime, repository, and selected data root are writable
and connected correctly.

## Run PRISM: eleven simple steps

Use the switches in the named notebook sections; do not run files from
`.prism_runtime/` directly.

| Step | What the researcher does | What PRISM produces |
| ---: | --- | --- |
| 1 | Open the notebook and choose **Run All Cells** with every collection/analysis switch left `False` | A safe environment, portability, preflight, and embedded-test check; no experiment starts |
| 2 | On each machine, run Section 7, then set `RUN_SMOKE_PAIR=True` in Section 8 | A 30-second normal/anomalous smoke pair and a readiness decision for Apple or Linux |
| 3 | With the machine authorized and idle, use Sections 10–12 to collect all calibration/development rows | Validated raw telemetry, events, platform/channel metadata, checksums, progress, and quality reports |
| 4 | Put both platforms under one `PRISM_DATA_ROOT`; set `RUN_PREFREEZE_AUDIT=True` in Section 14 and `RUN_PREPARE_ANALYSIS=True` once in Section 15 | A 160-run pre-freeze inventory, immutable dataset fingerprint, and five-second semantic-block cache |
| 5 | Run Section 17 and Section 17A for the static and guarded baselines; then set `RUN_ROBUST_NORMALIZATION_G3=True` in Section 17B.2 | Baseline ablations plus the authoritative robust residual-fusion development selection |
| 6 | Preserve the v2 and v3 confirmation records, then run the bounded v4 development gate in Section 17B.9 | Complete candidate evidence plus the two nearest operating points when no candidate meets both G3 limits |
| 7 | Optionally run Section 17B.10 with `RUN_NESTED_TEMPORAL_VALIDATION=True` | Post-hoc nested complete-run temporal validation, including environment and artifact fingerprints; locked rows remain inaccessible |
| 8 | Run the final bounded redesign once in Section 17B.11 with `RUN_V5_DEVELOPMENT_REDESIGN=True` | A 36-candidate semantic-corroboration audit that either earns fresh confirmation review or terminates detector iteration; it cannot access locked rows |
| 9 | Set `RUN_DICE_COMPARABLE_METRICS=True` once in Section 17B.13, return it to `False`, then run the paper cells in Section 17D | Operational Tables 9--10 and Figure 8; conventional AUC and F1 results are retained as Supplementary Tables S1--S2 and Figure S1; no retuning or locked access |
| 10 | Optionally set `RUN_DIAGNOSTIC_RANKER=True` once in Section 17B.14, return it to `False`, and rerun the Table 11 and Figure 9 cells | A bounded five model design space with repetition held out validation, imbalance and calibration metrics, inference timing, and excluded workload, platform, and scenario stress tests; it cannot access locked rows or replace G3 |
| 11 | Freeze the publication scope | The recorded v5 result did not earn confirmation, so submit the transparent pre-lock study, retain all negative results, and keep the sealed test for a separately confirmed future method |

### Results supplied to the paper

| Paper evidence | Notebook artifact or metric | Current status |
| --- | --- | --- |
| Dataset and quality table | Run counts, benign hours, cadence, channel coverage, failures, and checksum-backed provenance | Pre-freeze Apple/EPYC evidence available |
| Cross-platform telemetry table | Shared semantic groups plus Apple- and Linux-specific sensor availability | Available from smoke and quality reports |
| Monitoring comparison | Static VAR versus robust guarded adaptive VAR, persistence, EWMA, CUSUM, and conformal/e-process candidates | Development CSV/JSON generated |
| Reliability results | False alerts per benign hour, anomaly-run detection, median time-to-detect, and telemetry-interruption identification | Frozen v3 failed independent benign confirmation at 0.357 FAH; v4 found no point meeting both G3 limits |
| Adaptation ablation | Accepted/rejected updates, fault freezes, promotions, and rollbacks | Guarded update audit generated |
| Adaptive telemetry and transfer | Warning-triggered rich-tier duty cycle plus destination-platform calibration effort | Adaptive telemetry remains an offline trace replay; it is not a measured energy-saving claim |
| Temporal robustness | Nested complete-run inner selection and later-run outer evaluation | Available as an explicitly post-hoc sensitivity analysis in Section 17B.10 |
| Final redesign | Semantic-group corroboration of sequential warnings | No candidate passed: the best-detecting point reached 13.3% detection at 0.056 FAH, so further confirmation was not authorized |
| Operational scorecard | Monitored hours, alert episodes per hour, controlled event coverage, detection delay, fault identification, valid monitoring, and adaptive telemetry replay | 59.2% development event coverage, 100% telemetry fault identification, 337.5-s median detection time, 36.53 development benign hours, and 99.7% rich telemetry time avoided in independent offline replay |
| Scenario and platform robustness | Complete-run scenario counts, Apple/AMD subgroup rates, and independent benign confirmation | Seven of nine event scenarios reached at least 50% development coverage; Apple and AMD differed by five detection percentage points; confirmation remains the controlling reliability result |
| Conventional classifier supplement | Complete-run AUC PR, ROC AUC, precision, recall, and F1 | Retained transparently in Supplementary Tables S1--S2 and Figure S1 rather than used as the headline PRISM claim |
| Optional diagnostic design space | One Class SVM, logistic regression, Random Forest, ExtraTrees, and gradient boosting | ExtraTrees leads with development AUC PR 0.997, ROC AUC 0.986, MCC 0.858, balanced accuracy 0.914, and F1 0.971; post hoc and awaiting new independent event confirmation |
| Final headline table and figures | Operational scorecard, scenario coverage, independent-confirmation evidence, v4 boundary points, complete candidate tables, and limitations | Supported for a pre-lock paper; no locked-test or deployment-readiness claim |

The original and guarded ablations remain under
`$PRISM_DATA_ROOT/processed/prism-analysis-v1/`. The independent v2
confirmation failed at 17 false alerts over 16.8 benign hours (1.012/hour).
The later frozen v3 method detected 71/120 controlled event runs (59.2%) during
development, but its new 16-run benign confirmation produced 6 false alerts
over 16.8 hours (0.357/hour), exceeding the 0.25/hour requirement. Both
failures remain preserved and cannot be reused as independent confirmation.

The final bounded v4 development search also found no configuration meeting
both predeclared G3 limits. Its two nearest points were 0.244 false alerts/hour
with 59/120 detections (49.2%), and 0.281/hour with 61/120 detections (50.8%).
Section 17B.10's nested complete-run temporal sensitivity analysis detected
39/60 later-run events (65.0%) but produced 11 false alerts over 33.6 benign
hours (0.327/hour). It is post hoc and cannot erase either confirmation failure
or authorize locked-test access. The final 36-candidate semantic-corroboration
redesign reduced false alerts but over-suppressed real events: its
best-detecting point reached only 16/120 detections (13.3%) at 0.056/hour.
Consequently, no new confirmation collection is justified for this manuscript.

Section 17B.14 adds an explicitly separate offline diagnostic question: given a
complete development run, can robust temporal summaries distinguish controlled
events from benign operation? Its bounded five model comparison reports AUC PR,
ROC AUC, MCC, balanced accuracy, F1, Brier score, worst platform F1, and warm
cache inference time. ExtraTrees reaches 0.997 AUC PR, 0.986 ROC AUC, and 0.971
F1 under repetition held out cross validation. Excluding
an entire workload gives 0.989 AUC PR, while excluding an entire platform gives
0.945 AUC PR. These post hoc results are useful diagnosis evidence, but they do
not change the failed online confirmation, authorize locked access, or establish
deployment readiness. A new independent event confirmation set is required for
a final diagnostic performance claim.

The same warning window defines an adaptive-telemetry replay. A portable base
tier is treated as continuously available, while the richer diagnostic tier is
retained only during warning verification. The notebook reports that tier's
active-time fraction and the fraction avoided relative to always-on retention.
This replay uses previously collected full traces, so it is evidence about data
retention and diagnostic duty cycle—not a measured energy-saving claim. For the
selected development candidate, the richer tier is active for 1.23% of eligible
monitoring time.

### Immediate next action

1. Stop detector tuning and collect no additional confirmation or locked-test
   rows for this manuscript. The final bounded redesign did not earn them.
2. Use Table 6 for the independent-confirmation and v4 boundary results; use
   Table 7/Figure 7 only with the label **post-hoc temporal sensitivity
   analysis**, and Table 8 as the final redesign stopping record.
3. Write the current submission as a transparent pre-lock study. State that
   the 92 locked rows remain sealed for a future confirmatory study and do not
   claim G3 passage, final held-out performance, or deployment readiness.
4. Preserve the full candidate tables and negative results. Reporting only the
   most favorable point would be selection bias and would weaken both the
   scientific paper and the public research artifact.

### Main files to expect

- `$PRISM_DATA_ROOT/raw/<platform>/<date>/<run_id>/`: immutable telemetry,
  events, platform/channel descriptions, validation, and checksums.
- `$PRISM_DATA_ROOT/processed/smoke-gate/<commit>/comparison.json`: matched
  Apple/Linux smoke comparison.
- `$PRISM_DATA_ROOT/processed/prism-analysis-v1/development-method-selection.csv`:
  static development candidates.
- `$PRISM_DATA_ROOT/processed/prism-analysis-v1/development-guarded-method-selection.csv`:
  robust guarded adaptive-VAR candidates and G3 evidence.
- `$PRISM_DATA_ROOT/processed/prism-analysis-v1/development-robust-normalization-selection.json`:
  authoritative pooled development selection and G3 status.
- `$PRISM_DATA_ROOT/processed/prism-analysis-v1/development-shared-quantile-selection.json`:
  cross-platform alignment, platform/fold metrics, and strict-G3 status.
- `$PRISM_DATA_ROOT/processed/prism-analysis-v2/development-residual-corroborated-selection.json`:
  analysis-v2 development selection, subgroup metrics, guard configuration, and
  the mandatory independent-confirmation flag.
- `$PRISM_DATA_ROOT/processed/prism-analysis-v2/development-residual-corroborated-false-alerts.csv`:
  traceable false-alert episodes for the selected v2 setting.
- `$PRISM_DATA_ROOT/processed/prism-analysis-v2/independent-confirmation-result.json`:
  frozen-method confirmation decision, dataset/method fingerprints, and pooled,
  platform, and fold false-alert rates.
- `$PRISM_DATA_ROOT/processed/prism-analysis-v2/independent-confirmation-runs.csv`:
  one auditable result row for each of the 16 independent benign sessions.
- `$PRISM_DATA_ROOT/processed/prism-analysis-v3/development-warning-confirmation-selection.json`:
  bounded-search provenance, the strict v3 development selection, subgroup
  metrics, and the explicit requirement for fresh confirmation.
- `$PRISM_DATA_ROOT/processed/prism-analysis-v3/development-adaptive-telemetry-replay.json`:
  warning-triggered rich-tier active time and avoided-time fractions from an
  offline replay; it does not claim measured hardware-energy savings.
- `$PRISM_DATA_ROOT/processed/prism-analysis-v3/independent-confirmation-result.json`:
  one-shot v3 confirmation decision with pooled, platform, and fold FAH.
- `$PRISM_DATA_ROOT/processed/prism-analysis-v4/development-persistent-corroboration-selection.json`:
  bounded v4 development result, both nearest G3 boundary points, and the
  preserved no-pass decision.
- `$PRISM_DATA_ROOT/processed/prism-analysis-v4-posthoc-nested-temporal/`:
  optional nested complete-run temporal candidates, outer-run results,
  environment manifest, split and candidate fingerprints, and artifact hashes.
- `$PRISM_DATA_ROOT/processed/prism-analysis-v5/`:
  final bounded semantic-corroboration candidate table and stopping decision;
  the recorded result authorizes neither new confirmation nor locked testing.
- `paper/results/development/v5-final-semantic-corroboration-*`:
  portable tracked copies of the complete final candidate table and stopping
  decision for review without private raw telemetry.
- `$PRISM_DATA_ROOT/processed/prism-analysis-v6-diagnostic-ranker/`:
  optional post hoc complete run diagnostic scores, model fingerprint,
  bootstrap intervals, and excluded domain stress tests. It uses controlled
  event labels and is not an online reliability or locked test result.
- `paper/results/development/table-11-development-diagnostic-ranker.csv` and
  `paper/figures/development/figure-9-development-diagnostic-ranker.png`:
  portable paper facing copies of the diagnostic ranking result.
- `$PRISM_DATA_ROOT/processed/prism-analysis-v1/development-operational-robustness.json`:
  combined platform/fold, fault-state, and bidirectional-transfer freeze gate.
- `$PRISM_DATA_ROOT/processed/prism-analysis-v1/development-transfer-calibration.csv`:
  cross-platform calibration results after Section 18.
- `paper/method-freeze.json`: frozen method and notebook fingerprint, created
  only after every development gate passes.

This follows the same portable, notebook-first pattern as
[DICE](https://github.com/ping830616/DICE), but PRISM adds dual-platform data
collection, drift-aware monitoring, and a mandatory locked-test boundary.

The notebook is the only tracked Python source. **Run All Cells is safe by
default**: it rebuilds `.prism_runtime/` and runs checks without collecting data
or opening locked tests. The DICE baseline import is optional and never counts
as new PRISM replication. Detailed Apple, Linux, and analysis instructions are
linked in the repository map above.

## Data Collection at a Glance

### Dataset comparison

A **case** is one workload/condition combination; a **run** is one independent
execution of that combination.

| | Legacy DICE Apple data | New PRISM Apple data | New PRISM AMD data |
| --- | --- | --- | --- |
| Machine | Apple M2 Pro, ARM64/macOS | Apple M2 Pro, ARM64/macOS | AMD EPYC 9354, x86-64/Ubuntu |
| Role | Historical conference baseline | New same-protocol Apple evidence | New cross-platform Linux evidence |
| Count | `4 workloads × 6 conditions × 1 execution = 24` | `4×8×3 = 96` required; `2×3×3 = 18` targeted; `4×3 = 12` long-benign; total 126 runs (32.4 h) | Same PRISM design: 126 runs (32.4 h) |
| Workloads | Four original DICE workloads | `PY_STATS`, `PY_AI`, `BROWSER`, `VIDEO_SW` | Same four PRISM workload families |
| Required scenarios | `NOMINAL`, `ATOMIC`, `BRANCH`, `CACHE`, `MEMBW`, `TLB` | DICE scenarios plus `CONTROLLED_CRASH` and `TELEMETRY_INTERRUPTION` | Same eight required scenarios as PRISM Apple |
| Targeted scenarios | None | `THERMAL_SHIFT`, `POWER_SHIFT`, `DEGRADATION_PROXY` on two representative workloads | Same three targeted scenarios as PRISM Apple |
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
| 7 | Reserve or evaluate the locked test according to the declared paper scope | For the current pre-lock paper, keep it sealed; for a future confirmatory study, unlock only after method freeze and report all outcomes |

See the [end-to-end collection roadmap](docs/data-collection-roadmap.md) for
the complete operator procedure.

## Reproducibility Rules

- Split by independent run, never by windows from the same run.
- Tune only on development runs; keep the final platform/workload test partition
  locked unless a passing method is frozen for a separately declared future
  confirmatory evaluation.
- Treat repeated seeds on one trace as computational sensitivity, not independent experimental replication.
- Record raw data immutably and derive processed tables with hashes and manifests.
- Report confidence intervals and denominator counts with every headline rate.
- Cite the ITC DICE paper and include a submission-time table that identifies every new journal contribution.

## Publication Status

Working research repository. The current defensible manuscript scope is a
transparent pre-lock study: independent confirmation failures and all bounded
development analyses are retained, while the 92 locked rows remain sealed for
future confirmation. Do not claim final held-out performance or deployment
readiness, and do not make the repository public, archive a release, or add a
code/data license until the authors and advisor approve the publication plan.
