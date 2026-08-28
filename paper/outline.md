# Current manuscript structure

**PRISM: Platform-Robust In-Field Sequential Monitoring for Silicon Lifecycle
Management**

This outline follows the supplied 2026-08-28 draft. It replaces the earlier
proposed full-extension outline. The paper reports the v3 study; later
searches and diagnostic analyses remain in the repository as
[supporting evidence](../docs/supporting-analyses.md).

## I. Introduction

Motivate continuous SLM monitoring across heterogeneous hosts. Introduce
semantic telemetry, the behavioral micro-twin, operational metrics, and the
independent confirmation boundary. Keep development and confirmation results
separate.

## II. Background and Related Work

- Telemetry and silicon observability after deployment.
- Behavioral modeling of multivariate telemetry.
- Sequential monitoring and repeated decisions.
- Platform transfer, drift, and telemetry failure.

Table I compares capability coverage, not successful attainment of reliability
requirements. Prior work titles retain their published spelling.

## III. Proposed Method: PRISM

- Reliability contract and evidence roles.
- Architecture and semantic adapter.
- Behavioral micro-twin and residual evidence.
- Sequential decision process.
- Guarded adaptation and adaptive telemetry.
- Failure handling and platform calibration.

Distinguish the benign predictor from the supervised v3 classifiers. Distinguish
the earlier guarded VAR shadow model from v3 residual offsets. The micro-twin
trace is a mechanism illustration, not the v3 alert statistic.

## IV. Experimental Setup

Table II separates the original 252-run plan from the 208 admitted runs.
Describe the two hosts, four workload proxies, scenarios, complete run
grouping, exclusions, and recorded protocols. State pooled G3, the additional
v3 platform/fold requirements, and the independent confirmation requirement.

## V. Results and Analysis

### A. Admitted Evidence and Data Quality

Tables III and IV distinguish the original 160 runs from the 48 additions.
Explain v1–v3 as analysis revisions, not partitions, and account for every
denominator.

### B. Development Operating Points and Gate G3

Fig. 5 and Table V show the initial candidate search and progression to v3.
The selected monitor passed G3 during development. The first three checkpoints
and v3 use different eligible exposures, so the table is not a paired ablation.

### C. Guarded Adaptation to Drift and Update Safety

Fig. 6 audits the earlier guarded VAR checkpoint. Counts demonstrate exercised
control paths, not that every update learned benign drift.

### D. Transfer Across Platforms and Calibration Effort

Table VI preserves the earlier development transfer curve. No reported
calibration point meets both requirements; do not label it confirmed v3 transfer.

### E. Adaptive Telemetry, Fault Handling, and Cost

Describe fault handling, abstention, and offline telemetry replay. The data
were collected continuously; hardware energy and storage reductions were not
measured.

### F. Operational Reliability and Independent Confirmation

Fig. 7 covers scenario detection, confirmation FAH, delay among detected
events, and integrity/replay. Include count denominators, conditional Poisson
and Wilson intervals, and limitations. The reserved partition remained sealed.

## VI. Conclusion

Summarize the workflow and reported results without equating development
feasibility with deployment readiness.

See [the artifact map](../docs/paper-artifacts.md) for notebook cells, generated
tables, figure paths, and focused Overleaf edits. Notebook figure numbers are
stable artifact identifiers and do not equal the manuscript's figure numbers.
