# PRISM

**Practical Reliability Investigation of Sequential Monitoring for Silicon Lifecycle Management**

PRISM is a hybrid host monitoring and reliability evaluation framework for
heterogeneous computing platforms. The reported study uses Apple M2 Pro/macOS
and AMD EPYC 9354/Ubuntu hosts. PRISM preserves telemetry meaning and
availability, predicts expected benign behavior with compact behavioral
micro-twins, combines contextual and residual evidence through supervised
classifiers, and converts that evidence into persistent sequential alerts.

The repository contains the collection protocol, one canonical experiment
notebook, development artifacts, paper figures and tables, and the documentation
needed to reproduce the reported workflow. Raw telemetry is stored separately
and is not tracked in Git.

## Reviewers start here: six simple steps

These steps reproduce the paper's tables and figures from the numerical
evidence included in this repository. **No M2 Pro or EPYC machine, raw recordings,
Jupyter notebook, data collection, or detector retraining is needed.**
You need Python **3.12** and Internet access for the initial installation.
Follow only the commands for your operating system.

### 1. Download PRISM and open its folder

On this GitHub page, click **Code → Download ZIP**, extract the ZIP, and open
a terminal in the extracted `PRISM-main` folder. On Windows, use **PowerShell**.
You should be in the folder containing `README.md` and `reproduction/`.

Alternatively, if Git is installed, run:

```bash
git clone https://github.com/ping830616/PRISM.git
cd PRISM
```

**Run every remaining command from this same folder.**

### 2. Check that Python 3.12 is installed

macOS / Linux:

```bash
python3.12 --version
```

Windows PowerShell:

```powershell
py -3.12 --version
```

The output should begin with `Python 3.12`. If the command is not found,
install Python 3.12, reopen your terminal in the PRISM folder, and try again.

### 3. Create a separate Python environment

macOS / Linux:

```bash
python3.12 -m venv .venv-reviewer
```

Windows PowerShell:

```powershell
py -3.12 -m venv .venv-reviewer
```

No environment activation is needed; the commands below use it directly.

### 4. Install the required packages

macOS / Linux:

```bash
.venv-reviewer/bin/python -m pip install -r reproduction/requirements-reviewer.txt
```

Windows PowerShell:

```powershell
.\.venv-reviewer\Scripts\python.exe -m pip install -r reproduction/requirements-reviewer.txt
```

Wait for installation to finish successfully before continuing.

### 5. Reproduce the tables and figures

The script creates `reviewer-output` for you; do not create that folder first.

macOS / Linux:

```bash
.venv-reviewer/bin/python reproduction/reproduce.py --output reviewer-output
```

Windows PowerShell:

```powershell
.\.venv-reviewer\Scripts\python.exe reproduction/reproduce.py --output reviewer-output
```

The command checks the bundled input files, regenerates the results, and ends
with:

```text
PASS: 46 verified inputs; result tables and four numerical figures regenerated.
```

If you see `ERROR` instead, stop and consult the
[troubleshooting guide](docs/reviewer-reproduction.md#troubleshooting-and-validation).
For a second run, replace `--output reviewer-output` with
`--output reviewer-output-2`; existing output folders are never overwritten.

### 6. Open the results

In Finder or File Explorer, open the new **`reviewer-output`** folder and
double-click **`index.html`** to view the tables and figures in your browser.
The folder also contains:

- `tables/`: numerical Tables VI–IX as CSV and LaTeX, including all Table VIII subgroup rows.
- `figures/`: regenerated Figures 4–7 as PNG and PDF.
- `manuscript/`: original figure images and editable LaTeX for all nine tables.
- `reproduction-report.json`: verification results, versions, and file hashes.

Figures 1–3 and Tables I–V are authored diagrams/descriptive tables; they are
preserved rather than computationally regenerated. This workflow reproduces
saved paper artifacts, **not independent detector reanalysis from raw recordings**.

For further details, see the [reviewer guide](docs/reviewer-reproduction.md).
For how the original measurements were acquired, see the
[M2 Pro and EPYC collection methodology](docs/collection-methodology.md).
**Reviewers can stop here; the historical notebook instructions below are optional.**

## Reported evidence

| Evidence | Result |
| --- | --- |
| Validated runs outside the reserved partition | 208 total: 192 for declared v3 development and 16 for independent benign confirmation |
| Development evidence | 120 controlled event runs and 36.53 h of eligible benign monitoring |
| Selected development monitor | 71/120 event runs detected (59.2%), 0.164 false alert episodes per benign hour, and 337.5 s median delay among detected events |
| Telemetry interruption handling | 16/16 controlled interruptions identified as telemetry faults |
| Independent benign confirmation | 6 false alert episodes over 16.8 h, or 0.357 per hour, above the predeclared 0.25 per hour feasibility limit |
| Adaptive telemetry replay | Rich telemetry retained for 185/60,480 eligible seconds, or 0.31% of confirmation time |
| Reserved evaluation | 92 planned runs remained sealed and were not collected, inspected, or scored |

The independent confirmation set contains benign operations only. It evaluates
false alert reliability, not controlled event detection or delay. The adaptive
telemetry result is an offline retention replay from traces that originally
contained all channels; it does not measure acquisition, energy, storage, or
runtime savings.

## Scientific scope

PRISM evaluates host visible operating disturbances, controlled software
crashes, telemetry interface interruptions, and thermal, power, and degradation
proxies. It supports behavioral screening, telemetry integrity checks, and
reliability evaluation. It does not reproduce or diagnose physical aging
mechanisms, manufacturing defects, security attacks, remaining lifetime, or
physical root cause.

The development feasibility gate requires no more than 0.25 false alert
episodes per benign monitoring hour and at least 50% controlled event
detection. This gate is a research screen, not an industrial deployment
standard. Passing it during development permits independent confirmation of one
unchanged candidate; it does not authorize access to the reserved partition.

## Method summary

1. Collect native telemetry together with units, source, cadence, provenance,
   and availability.
2. Validate and map compatible channels into shared semantic groups.
3. Predict expected benign behavior with a compact behavioral micro-twin.
4. Fuse contextual and residual classifier evidence and accumulate it with a
   sequential alert rule.
5. Report one explicit state: normal, behavioral alert, telemetry fault, or
   abstention.

The notebook also contains guarded update audits, platform transfer analysis,
bounded development redesigns, and post hoc diagnostic ranking. These analyses
remain clearly separated from the independent confirmation result.

## Repository map

- `notebooks/PRISM_Complete_Experiment.ipynb`: canonical collection,
  validation, analysis, and paper artifact notebook.
- `configs/`: frozen collection and confirmation contracts.
- `docs/data-collection-roadmap.md`: end to end collection and transfer guide.
- `docs/README.md`: documentation index and current versus historical files.
- `docs/apple-collection.md`: Apple M2 setup and collection procedure.
- `docs/linux-asu-collection.md`: AMD EPYC server setup and collection procedure.
- `docs/methods.md`: current v3 hybrid method, evidence roles, and terminology.
- `docs/paper-artifacts.md`: manuscript figure and table provenance.
- `docs/paper-results.md`: result denominators, uncertainty, and interpretation.
- `docs/reproducibility.md`: bundled reproduction and raw reanalysis procedures.
- `docs/supporting-analyses.md`: development analyses outside the main paper.
- `docs/drift-aware-analysis.md`: analysis sequence, feasibility gate, and
  confirmation boundary.
- `docs/novelty-boundary.md`: relationship to DICE and separation from CITADEL.
- `docs/research-plan.md`: historical decisions, amendments, and stopping rules.
- `paper/figures/development/`: generated development and confirmation figures.
- `paper/results/development/`: generated paper tables and supporting results.
- `paper/abstract-prelock.md`: evidence aligned manuscript abstract and claim
  boundary.

Historical documents and configuration fields may use `locked_test` or
“locked test.” The manuscript calls the same protected evidence the
**reserved partition**.

## Optional historical notebook setup (not the reviewer workflow)

The commands below are for inspecting the original research notebook or
performing separately provisioned raw-data reanalysis. **They are not needed
to reproduce the saved paper tables and figures.** Reviewers should use the
standalone command at the top of this page instead.

Clone the repository into any writable directory on macOS or Linux:

```bash
git clone https://github.com/ping830616/PRISM.git
cd PRISM

python3 -m venv .venv
source .venv/bin/activate
python3 -m pip install --upgrade pip
python3 -m pip install -e ".[notebook]"

export PRISM_REPO_ROOT="$PWD"
export PRISM_DATA_ROOT="${PRISM_DATA_ROOT:-$PWD/data}"
export PYTHONHASHSEED=0
export PRISM_NUM_THREADS=1
export PRISM_STRESS_MB=128
export OMP_NUM_THREADS=1
export OPENBLAS_NUM_THREADS=1
export MKL_NUM_THREADS=1
export VECLIB_MAXIMUM_THREADS=1
export NUMEXPR_NUM_THREADS=1
export BLIS_NUM_THREADS=1
export MPLCONFIGDIR="$PWD/.prism_runtime/matplotlib"

mkdir -p "$PRISM_DATA_ROOT" "$MPLCONFIGDIR"

python -m jupyter lab \
  notebooks/PRISM_Complete_Experiment.ipynb
```

Python 3.10 or newer is required. `PRISM_DATA_ROOT` may point to a separate
local or server volume. Set it before starting Jupyter. The notebook uses the
active kernel, discovers the repository root, rejects embedded machine specific
paths, records the dataset fingerprint, and fixes random seeds and numerical
thread counts where supported.

## Historical notebook and raw-data reanalysis

1. Start from a clean clone and activate the virtual environment.
2. Set `PRISM_DATA_ROOT` to the validated telemetry directory.
3. Open the notebook and restart the kernel.
4. Leave every collection, redesign, confirmation, and reserved access switch
   set to `False` for a read only reproduction.
5. Run the setup, validation, analysis loading, and paper result cells in
   order. Section 17D displays paper evidence, and Section 17E checks the
   reported numbers and exports manuscript tables. The notebook checks
   fingerprints before combining artifacts.
6. Use collection switches only on the intended host and only under the frozen
   protocol described in `docs/`.

The standalone reviewer workflow regenerates the paper artifacts from bundled
numerical evidence without raw telemetry. Independently recomputing detector
outputs from the original measurements is a different task: it requires the
separately stored raw telemetry, checksum manifests, and matching analysis
revision. The notebook instructions in this section apply to that historical
research environment, not to the short reviewer workflow.

For an optional historical notebook execution check in that provisioned
environment (not a substitute for the reviewer command):

```bash
mkdir -p .prism_runtime/reproduction
python -m jupyter nbconvert --to notebook --execute \
  notebooks/PRISM_Complete_Experiment.ipynb \
  --ExecutePreprocessor.timeout=300 \
  --output PRISM.executed.ipynb \
  --output-dir .prism_runtime/reproduction
```

Keep all collection, search, confirmation, and reserved access switches set to
`False` for this check.

## Claim boundary

- Do not describe PRISM as deployment ready.
- Do not claim that independent confirmation validated event detection; the
  confirmation set was benign only.
- Do not report the offline telemetry replay as measured resource savings.
- Do not use confirmation evidence to retune the same analysis revision.
- Do not open the reserved partition without a separately approved and frozen
  future method.

The failed confirmation is a reported scientific result: it demonstrates why
promising development performance must remain distinct from independently
confirmed operational reliability.
