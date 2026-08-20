# Guarded Drift-Aware Analysis Procedure

This procedure runs PRISM's robust residual normalization and guarded adaptive
VAR analysis without opening the locked test. The canonical implementation is
Section 17A of `notebooks/PRISM_Complete_Experiment.ipynb`; no separate Python
source file is maintained.

## 1. Start the same notebook on any analysis machine

Use Python 3.10 or newer. From a normal checkout:

```bash
cd /absolute/path/to/PRISM
python3 -m venv .venv
source .venv/bin/activate
python3 -m pip install -e ".[notebook]"
python -m jupyter lab notebooks/PRISM_Complete_Experiment.ipynb
```

If the raw Apple and EPYC telemetry is on another local or server volume, set
the data location before starting Jupyter:

```bash
export PRISM_REPO_ROOT="/absolute/path/to/PRISM"
export PRISM_DATA_ROOT="/absolute/path/to/prism-data"
python -m jupyter lab \
  "$PRISM_REPO_ROOT/notebooks/PRISM_Complete_Experiment.ipynb"
```

The selected data root must contain `raw/M2_MACOS`, `raw/EPYC_LINUX`, the
Apple tracker, and the copied EPYC audit tracker in the documented layout.

## 2. Run the safe default pass

Restart the kernel, then use **Run All Cells** once with all collection and
analysis switches left at `False`. This materializes `.prism_runtime`, runs
preflight, executes the embedded source tests, checks for machine-specific
paths, and runs the synthetic analysis checks. It does not collect data.

Stop if the notebook does not print both of these messages:

```text
PASS: portable notebook contract
PASS: PRISM analysis functions passed synthetic self-checks.
```

## 3. Admit only the pre-freeze evidence

In Section 14 set:

```python
RUN_PREFREEZE_AUDIT = True
VERIFY_ALL_RAW_CHECKSUMS = False
```

Run that code cell. The expected inventory is 80 admitted runs per platform:
four calibration runs and 76 development runs. All 46 locked-test rows per
platform must still be `planned`. Record the printed dataset fingerprint.

Use `VERIFY_ALL_RAW_CHECKSUMS = True` for the final archival audit; it is slower
but verifies every raw manifest.

## 4. Build or load the semantic cache

In Section 15 set `RUN_PREPARE_ANALYSIS = True` and run the cell once when the
fingerprinted cache is absent or the raw manifest fingerprint changes. Return
the switch to `False` afterward. Five-second nonoverlapping blocks retain their
original run identity and split.

## 5. Reproduce the static control

Set `RUN_METHOD_SELECTION = True` in Section 17 and run that cell. This is the
unchanged static ridge/VAR control and must remain available for the journal
ablation table. It may not unlock the test unless G3 passes.

## 6. Run guarded adaptive VAR

Set `RUN_GUARDED_METHOD_SELECTION = True` in Section 17A and run that cell.
The implementation performs, in causal order:

1. 60 seconds of run-local startup calibration inside the predeclared
   120-second clean pre-onset interval;
2. log-transformed residual scoring with median/MAD normalization and bounded
   winsorized reference updates;
3. normalized-LMS updates to a shadow VAR only when residual and conformal
   guards agree that the block is safe;
4. bounded coefficient drift, validation-buffer promotion, checkpoints, and
   rollback after post-promotion residual bursts; and
5. complete update freezing during telemetry faults or declared interruption.

The cell writes ignored development artifacts under
`data/processed/prism-analysis-v1/` (or the corresponding
`PRISM_DATA_ROOT/processed/` path). Inspect the JSON report and retain the audit
counts for accepted/rejected updates, fault freezes, promotions, and rollbacks.

## 7. Run robust residual normalization

Set `RUN_ROBUST_NORMALIZATION_G3 = True` in Section 17B.2 and run that cell.
This is the authoritative development selection. It robustly normalizes
run-local semantic levels, changes, and compact micro-twin residuals; fits
platform/workload-local fusion models using complete-run cross-fitting; and
writes the selected configuration without reading locked-test rows. Reset the
switch to `False` after the run.

## 8. Apply Gate G3 without reinterpretation

G3 requires both:

- false alerts no greater than 0.25 per monitored benign hour; and
- anomaly-run detection of at least 50% on development runs.

If `gate_passed` is `false`, do not create a method freeze and do not collect,
copy, inspect, or score locked-test rows. Revise the method using calibration
and development evidence only, then rerun the affected development sections.

If it passes, run Section 18 with `RUN_TRANSFER_ANALYSIS = True`. Review both
transfer directions and all destination-calibration points before advisor
review. The zero-shot row is leakage-proof: its regularization, percentile,
workload thresholds, and persistence are selected on the source platform only,
then evaluated on the destination once. Positive-minute rows may use only a
chronological benign destination prefix; destination event labels never select
or calibrate a policy. A pooled G3 pass does not erase platform-specific or
transfer limitations and does not by itself authorize locked-test collection.

## Current development checkpoint (August 20, 2026)

The supplement confirmation failed at 0.253 FAH, and the later independent v2
confirmation failed at 1.012 FAH (17 alerts/16.8 h). Both outcomes are preserved
and their rows are now development evidence. They cannot confirm another
method. Locked-test access remains false.

Section 17B.7 performs one bounded v3 development search. It keeps a shared
workload classifier, calibrates the benign score reference by platform and
workload, thins sequential decisions to one per two blocks, and requires
residual-only confirmation within six blocks of a warning.

| v3 development subgroup | Benign h | FAH | Detection | G3 |
| --- | ---: | ---: | ---: | --- |
| Pooled | 36.533 | 0.164 | 59.2% (71/120) | **Pass** |
| Apple M2 | 18.267 | 0.109 | 61.7% (37/60) | **Pass** |
| AMD EPYC | 18.267 | 0.219 | 56.7% (34/60) | **Pass** |
| Fold 0 | 18.267 | 0.109 | 55.0% (33/60) | **Pass** |
| Fold 1 | 18.267 | 0.219 | 63.3% (38/60) | **Pass** |

Exactly one of 216 candidates passes every development subgroup. Its
warning-triggered rich-tier replay activates the diagnostic tier for 1.23% of
eligible monitoring time. This is a development selection and an offline
retention replay, not independent confirmation or measured energy savings.

The next permitted step is the disjoint 16-session plan in
`data/v3-independent-confirmation-plan.csv`. Apply the selected v3 method once,
unchanged. A pooled, per-platform, and per-fold confirmation pass permits
transfer review and formal method-freeze preparation; it does not automatically
open the locked test. If confirmation fails, preserve it, report the limitation,
and do not retune on those rows.
