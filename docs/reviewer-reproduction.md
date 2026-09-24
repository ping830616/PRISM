# Reproduce the manuscript tables and figures

This is the short reviewer workflow. It runs on an ordinary computer without
an Apple M2 Pro, an EPYC server, Jupyter, privileged telemetry tools, or the
original raw recordings. It never starts data collection or retrains a detector.

The scope is **reproduction of paper artifacts from saved numerical evidence**,
not independent raw-data reanalysis. A successful run must preserve the reported
negative confirmation result as well as the development results.

## Install and run

Use Python **3.12** for the tested environment. The pinned packages also support
Python 3.10–3.13; the CI workflow tests selected versions on macOS, Ubuntu and
Windows when this revision is pushed. Do not infer a CI pass before that job
has actually completed. Installation needs Internet access; execution does not.

From the repository root on macOS or Linux:

```bash
python3.12 -m venv .venv-reviewer
.venv-reviewer/bin/python -m pip install -r reproduction/requirements-reviewer.txt
.venv-reviewer/bin/python reproduction/reproduce.py --output reviewer-output
```

On Windows, from PowerShell (activation is not required):

```powershell
py -3.12 -m venv .venv-reviewer
.\.venv-reviewer\Scripts\python.exe -m pip install -r reproduction/requirements-reviewer.txt
.\.venv-reviewer\Scripts\python.exe reproduction/reproduce.py --output reviewer-output
```

Open **`reviewer-output/index.html`** in a browser. The command prints `PASS`
only after input checksums, reported counts/rates, and all twelve rows of the
current Table VIII agree. `reproduction-report.json` records the environment,
source and output hashes, numerical tolerances, and each figure's evidence role.
If the destination exists, choose a new name such as `reviewer-output-2`; the
runner will not overwrite earlier results.

An input-only check needs no third-party Python packages and writes nothing:

```bash
python reproduction/reproduce.py --verify-only
```

Do **not** run the collection notebook as a prerequisite. Do not set
`PRISM_DATA_ROOT`, enable a collection switch, or supply raw telemetry for this
reviewer workflow. Paths are resolved relative to the script, so an absolute
script path also works from another current directory, including one with spaces.

## What is reproduced

This package follows the 15-page `TR_PRISM` draft represented by the Overleaf
ZIP fingerprint in `reproduction/manuscript/manifest.json`. It contains seven
figures and nine tables. The older notebook map used different table numbers.

| Current paper item | Output and source | Meaning of reproduction |
| --- | --- | --- |
| Figures 1–3 | `manuscript/figures/figure-1-*` through `figure-3-*` | Exact authored diagrams copied and checksum-verified; not computational plots |
| Figure 4 | `figures/figure-4-micro-twin.{png,pdf}` | Curves redrawn from the exported numerical illustration trace and metadata |
| Figure 5 | `figures/figure-5-development-operating-points.{png,pdf}` | Initial candidate CSVs; static, guarded and robust reports must share a fingerprint |
| Figure 6 | `figures/figure-6-guarded-update-audit.{png,pdf}` | Saved earlier guarded VAR action counts, cross-checked against its JSON report |
| Figure 7 | `figures/figure-7-operational-reliability.{png,pdf}` | Saved scenario, delay, confirmation and retention evidence |
| Tables I–V | `manuscript/tables/table-i-*` through `table-v-*` | Exact editable authored tables: scope, literature, extension, parameters and experimental setup |
| Table VI | `tables/table-vi-data-quality.{csv,tex}` | Original inventory and data-quality reports |
| Table VII | `tables/table-vii-revision-history.{csv,tex}` | Saved revision inventory and v2/v3 confirmation reports |
| Table VIII | `tables/table-viii-development-progression.{csv,tex}` | Four pooled checkpoints plus eight platform/fold audit rows |
| Table IX | `tables/table-ix-transfer-calibration.{csv,tex}` | Preserved earlier bidirectional transfer calibration curve |

The exact manuscript images for Figures 4–7 and original LaTeX for Tables VI–IX
are also retained under `manuscript/`. They are clearly labeled reference assets,
not passed off as regenerated output. Regenerated plots preserve numerical
content, but fonts, image dimensions, and layout can differ from the Overleaf
images. CSV numerical values are checked; pixel equality across platforms is
not promised. The generated Table VIII uses a wider layout to make every
subgroup row explicit; the original one-column source remains available.

Tables I–V are not statistical calculations. Reproducing them means preserving
their authored source, not manufacturing a computational derivation of the
literature review or study descriptions. To compile the original tables within
Overleaf, use the files under `manuscript/tables/`, the provided
`table-preamble.tex`, and `references.bib` in an IEEEtran project.

## Numerical checks

The runner validates the following, among other source consistency checks:

- 208 admitted runs: 192 development and 16 fresh benign confirmation runs;
  92 reserved rows are not used.
- Development detection: 71/120, or 59.1667%; false-alert rate:
  6/36.5333333 hours, or 0.1642336 per hour.
- Median delay: 337.48666996 seconds among detected development events.
- Confirmation: 6 false-alert episodes in 16.8 hours, or 0.3571429 per hour.
- Retention: 37/12,096 blocks = 185/60,480 seconds = 0.305886%, displayed as 0.31%.
- Table VIII's subgroup successes and failures, including robust fusion's
  failure to satisfy all subgroup limits.

These checks do not make the failed confirmation pass the 0.25/hour research
limit. They do not establish adaptation benefit, physical aging detection,
formal conformal validity, or live acquisition/resource savings.

## Figure 4 provenance

`reproduction/inputs/figure-4-micro-twin.csv` holds the actual plotted arrays,
not values digitized or guessed from the image. Its JSON records the fixed
development run, source-cache and code hashes, five nominal fitting identities,
lag/penalty settings, and the one-time export environment. The original
illustration is a compact VAR diagnostic illustration, not the selected v3
monitor or its decision threshold. Its reference was recovered with the original
fixed illustration code; the reviewer command only reads the exported arrays.

The author-only `export_micro_twin_inputs.py` records how this export can be
recovered from the corresponding historical cache. It is not invoked by the
reviewer command, is not new experimental evidence, and must not be used to
change the paper's selected detector. `import_manuscript_assets.py` similarly
documents extraction of exact reference assets from an explicit Overleaf ZIP.

## Data collection and full reanalysis

For how the original data were acquired, read
[the historical collection methodology](collection-methodology.md). It links
the M2 Pro/macOS and EPYC/Ubuntu guides, workload code, event timing, telemetry
sources, validity checks, manifests, exclusions and evidence roles. Reviewers
do not need to repeat those steps to run this package.

Full raw reanalysis remains a separate task requiring the original recordings,
checksums, run trackers, and the matching analysis revision. This package does
not make those recordings public or substitute report hashes for raw provenance.
The original [reproduction guide](reproducibility.md) retains that distinction.

## Troubleshooting and validation

The [local verification record](../reproduction/verification-reviewer-package.md)
documents a fresh macOS ARM64/Python 3.12 run and 19 passing tests in a clean
source copy. It distinguishes those completed checks from configured but
not-yet-run Linux/Windows CI jobs.

- Missing/checksum-mismatched input: stop and obtain an intact checkout. Do not
  edit a hash or expected result to make the test pass.
- Missing package: install the exact `requirements-reviewer.txt` environment.
  The historical `requirements-source.txt` is not the lock for this workflow.
- No display server: expected; plotting uses Matplotlib's noninteractive Agg backend.
- Different font/PNG/PDF bytes: compare numerical data and the supplied
  verification report, not cross-platform image hashes.
- Run tests with `python -m unittest discover -s reproduction -p 'test_reviewer.py'`.
  Numerical outputs and source files are written separately; all original
  reports and the collection notebook remain unchanged.
