# PRISM

**Platform-Robust In-Field Sequential Monitoring for Silicon Lifecycle Management**

PRISM extends DICE to host monitoring on Apple M2 Pro/macOS and AMD EPYC
9354/Ubuntu. Its hybrid monitor combines a benign behavioral micro-twin with
supervised classifiers and sequential evidence. The study asks whether
promising development performance survives independent benign confirmation.
The project name expresses a design goal, not demonstrated detector robustness
or reliable transfer to a new platform.

## Key results

The reported v3 study contains **208 validated runs**: 192 supported declared
development revisions, including calibration, and 16 provided independent
benign confirmation. The 92 planned runs in the **reserved partition remained
sealed**. FAH means false alert episodes per benign monitoring hour.

| Evidence | Reported result |
| --- | --- |
| Development detection | 71/120 runs with controlled events: **59.2%** |
| Development false alerts | 6 episodes / 36.53 h: **0.164 FAH** |
| Detection delay | **337.5 s** median among detected events |
| Telemetry fault identification | **16/16** controlled interruptions |
| Independent benign confirmation | 6 episodes / 16.80 h: **0.357 FAH** |
| Rich telemetry during confirmation replay | **0.31%** of eligible time |

The replay fraction is **37/12,096 valid blocks**, or **185/60,480 s**.

The selected monitor satisfied Gate G3 **during development**, including its
platform and fold checks. Independent confirmation exceeded the **0.25 FAH**
limit, so the method did not advance to final approval or reserved evaluation.
Replay estimates selective telemetry retention, not measured energy or storage
savings. See the [results and evidence roles](docs/paper-results.md) for counts,
uncertainty, transfer results, and interpretation.

## Method in brief

1. **Record and align:** preserve units, sources, cadence, provenance, and
   availability; map compatible measurements into shared functional groups.
2. **Predict and score:** fit a benign behavioral reference. The selected v3
   method also uses two supervised logistic classifiers per workload, shared
   across platforms, to combine contextual and residual evidence.
3. **Monitor:** accumulate empirical sequential evidence, require residual
   corroboration, and distinguish behavioral alerts from telemetry faults and
   abstention. Guarded offsets follow a fixed policy during evaluation.
4. **Evaluate:** keep complete runs together, select using development
   evidence, then confirm one unchanged candidate on fresh benign runs.

## Reproduce from a terminal

Use Python **3.10 or newer** on macOS or Linux. GitHub access is required while
the repository is private. Raw telemetry is not included; a fresh clone can
check the notebook and reproduce the bundled paper summaries and most figures.

```bash
git clone https://github.com/ping830616/PRISM.git
cd PRISM
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -e ".[notebook]"
python -m ipykernel install --sys-prefix --name prism --display-name "PRISM"

export PRISM_REPO_ROOT="$PWD"
export PRISM_DATA_ROOT="$PWD/data"  # or your existing external PRISM data directory
export PYTHONHASHSEED=0 PRISM_NUM_THREADS=1 PRISM_STRESS_MB=128
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1
export VECLIB_MAXIMUM_THREADS=1 NUMEXPR_NUM_THREADS=1 BLIS_NUM_THREADS=1
export MPLCONFIGDIR="$PWD/.mplconfig"
mkdir -p "$MPLCONFIGDIR"

python -m jupyter lab notebooks/PRISM_Complete_Experiment.ipynb
```

Select the **PRISM** kernel. Leave collection, fitting, search, confirmation,
and reserved access switches `False`, then choose **Run All Cells**. Setup and
synthetic checks run automatically. **Section 17D** displays paper evidence;
**Section 17E** checks the reported numbers and exports manuscript tables.
This does not collect experiments or repeat independent confirmation.

For a terminal check without opening JupyterLab:

```bash
mkdir -p .prism_runtime/reproduction
python -m jupyter nbconvert --to notebook --execute \
  notebooks/PRISM_Complete_Experiment.ipynb \
  --ExecutePreprocessor.kernel_name=prism \
  --ExecutePreprocessor.timeout=300 \
  --output PRISM.executed.ipynb --output-dir .prism_runtime/reproduction
```

## Documentation

- [Documentation index](docs/README.md): detailed procedures and historical records.
- [Paper figure and table map](docs/paper-artifacts.md): where each draft result
  comes from, what to run, and how to use its Overleaf export.
- [Reproduction guide](docs/reproducibility.md): saved results versus raw
  reanalysis, environments, figure editing, and troubleshooting.
- [Methods and terminology](docs/methods.md): v1–v3, evidence roles, and gates.
- [Supporting analyses](docs/supporting-analyses.md): preserved searches,
  temporal validation, and diagnostic metrics outside the main paper narrative.
- [Scientific review edits](docs/scientific-review-edits.md): exact Overleaf
  replacements and the remaining decisions for advisor review.

The [notebook](notebooks/PRISM_Complete_Experiment.ipynb) is the canonical
Python source. `.prism_runtime/` is disposable; edit notebook cells, not that
generated directory. Collection plans and recorded outcomes remain unchanged.
