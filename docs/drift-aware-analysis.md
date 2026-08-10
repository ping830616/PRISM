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
preflight, executes the 18 embedded source tests, checks for machine-specific
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

## 7. Apply Gate G3 without reinterpretation

G3 requires both:

- false alerts no greater than 0.25 per monitored benign hour; and
- anomaly-run detection of at least 50% on development runs.

If `gate_passed` is `false`, do not create a method freeze and do not collect,
copy, inspect, or score locked-test rows. Revise the method using calibration
and development evidence only, then rerun Sections 14, 15, 17, and 17A.

## Current development checkpoint (August 10, 2026)

Dataset fingerprint:
`2d83c66675a3c4e31c7b85b67b39db5a44ad7862af9f56bc4a4c80c74e0eaf2f`

| Development control | Benign hours | False alerts/hour | Detection | G3 |
| --- | ---: | ---: | ---: | --- |
| Static VAR sequential conformal | 12.53 | 24.81 | 97.5% (117/120) | Fail |
| Guarded adaptive VAR, lowest-alert detecting candidate | 10.00 | 0.90 | 44.2% (53/120) | Fail |

The guarded method materially reduces false alerts, but it does not yet meet
the declared reliability/detection pair. The correct status is therefore:
**implementation complete, G3 closed, locked test untouched**.
