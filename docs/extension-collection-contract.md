# Journal-Extension Data Collection Contract

This file turns the data promises in the DICE journal-extension memo into
executable PRISM acceptance criteria. The repository is collection-ready only
when `scripts/preflight.py` passes. The journal extension is empirically
fulfilled only after the tracker shows that all required and targeted rows are
valid and both platforms meet the benign-hour target.

## Extension-to-Run Mapping

| Extension promise | PRISM evidence |
| --- | --- |
| Retain the legacy M2 evidence | Frozen DICE import with source revision and SHA-256 inventory |
| New M2 and EPYC data under one protocol | Required matrix on `M2_MACOS` and `EPYC_LINUX` |
| Workload pressure | `ATOMIC`, `BRANCH`, `CACHE`, `MEMBW`, and `TLB` |
| Controlled crashes | Collector terminates only its workload child and records the exact event |
| Telemetry interruptions | Collector masks enriched telemetry for a declared interval while retaining the research clock and portable host channel |
| Thermal and power changes | Targeted `THERMAL_SHIFT` and `POWER_SHIFT` workload-induced condition changes |
| Degradation proxy | Targeted progressive-duty-cycle `DEGRADATION_PROXY`; this is not physical aging |
| Longer benign evidence | Matrix nominal runs plus long-benign supplements total 12 planned hours per platform |
| Repeated evidence | Three independently restarted runs per required/targeted cell |

`THERMAL_SHIFT`, `POWER_SHIFT`, and `DEGRADATION_PROXY` are required targeted
extension experiments on two representative workloads, rather than an
unnecessary full cross-product. They must be described as controlled
condition/proxy experiments. They are not operating-system power-policy
changes, silicon aging, or remaining-useful-life evidence.

## Frozen Collection Inventory

The machine-readable configuration generates:

- 192 required-matrix runs;
- 36 targeted extension runs;
- 24 long-benign supplement sessions;
- 252 total runs and 64.8 total machine-hours across both platforms;
- 12 planned benign hours per platform after combining matrix nominal runs and
  long-benign supplements.

The tracked `data/collection-plan.csv` is immutable after collection starts.
Machine-local progress is written to the Git-ignored
`data/collection-progress.csv`, allowing production collection to retain a
clean Git revision.

## Terminal Gate

Run from a clean checkout:

```bash
python3 -m pip install -e .
python3 scripts/preflight.py configs/experiment-matrix.toml
python3 scripts/probe_collection.py
python3 scripts/check_collection_readiness.py --platform-id M2_MACOS
python3 scripts/collect_next.py --platform-id M2_MACOS
```

The last command previews the next eligible run. It does not collect anything
until `--execute` is supplied:

```bash
python3 scripts/collect_next.py --platform-id M2_MACOS --execute
```

Locked-test rows are hidden until the method is frozen. After the documented
freeze, they require the explicit `--unlock-locked-test` flag.

Check progress at any time:

```bash
python3 scripts/collection_status.py
python3 scripts/data_quality_report.py --platform-id M2_MACOS
```

## Per-Run Acceptance

A valid run must have:

1. the exact predeclared run ID, split, duration, cadence, and scenario;
2. a clean committed software revision for production;
3. monotonic timestamps, expected row count, bounded cadence gaps, and complete
   checksums;
4. the required workload and scenario events;
5. raw platform-native telemetry preserved separately from sanitized values;
6. impossible temperature, power, or utilization values nulled rather than
   silently retained or replaced with zero;
7. critical-channel non-null coverage at or above the declared production
   threshold, excluding the deliberately masked interruption interval
   (95% for primary utilization/power channels and 70% for the known-flaky
   Apple temperature channel);
8. an explicit valid, replacement-required, or excluded tracker state.

Passing this contract makes the repository ready to collect extension evidence.
It does not by itself mean that the journal extension has been completed.
