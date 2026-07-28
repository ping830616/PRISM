# PRISM-SLM

**PRISM: Platform-Robust In-Field Sequential Monitoring for Silicon Lifecycle Management**

PRISM is the proposed journal extension of the DICE host-side monitoring study. It asks a focused question:

> Can a behavioral micro-twin provide reliable, statistically calibrated in-field monitoring across heterogeneous host platforms without requiring identical telemetry channels?

The repository is intentionally private-ready while the work is unpublished. It contains the research plan, experiment contract, paper outline, and implementation scaffolding, but no raw telemetry.

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
- `docs/novelty-boundary.md`: claim matrix and separation from DICE/CITADEL.
- `configs/experiment-matrix.toml`: machine-readable experiment design.
- `data/README.md`: immutable data layout and provenance rules.
- `paper/outline.md`: journal narrative and required tables/figures.
- `src/prism_slm/contracts.py`: platform and channel schema primitives.
- `scripts/preflight.py`: validates experiment configuration.
- `tests/`: schema tests.

## Quick Start

```bash
python -m pip install -e .
python scripts/preflight.py configs/experiment-matrix.toml
python -m unittest discover -s tests -v
```

## Reproducibility Rules

- Split by independent run, never by windows from the same run.
- Tune only on development runs; keep the final platform/workload test partition locked.
- Treat repeated seeds on one trace as computational sensitivity, not independent experimental replication.
- Record raw data immutably and derive processed tables with hashes and manifests.
- Report confidence intervals and denominator counts with every headline rate.
- Cite the ITC DICE paper and include a submission-time table that identifies every new journal contribution.

## Publication Status

Working research repository. Do not make public, archive a release, or add a code/data license until the authors and advisor approve the publication plan.
