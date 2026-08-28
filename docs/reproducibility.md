# Reproduce the paper evidence

## Choose the right task

| Task | Inputs | What it establishes |
| --- | --- | --- |
| Open figures and tables | Git checkout and notebook environment | Displays saved evidence |
| Rebuild manuscript summaries | Bundled reports, plans, and tables | Recomputes counts, rates, and intervals; verifies fingerprints |
| Recompute illustrative micro-twin trace | Existing semantic cache | Recreates the fixed illustration, not a new v3 evaluation |
| Reanalyze experiments | Original raw files, manifests, trackers, and recorded configuration | Verifies data admission and recomputes the specified analysis |

A successful saved-result run is not raw data revalidation. The default notebook
does not collect new experiments, search for a better monitor, or open the
reserved partition.

## Terminal and kernel

Follow the [README quick start](../README.md). It installs the notebook extras,
registers a kernel inside the virtual environment, and sets deterministic hash
and numerical thread settings. Python 3.10 or newer is required.

For an existing checkout, activate its virtual environment and repeat the
environment exports before starting Jupyter. Select that environment's
**PRISM** kernel. If another Jupyter instance already owns a port, use its URL
or choose an unused port, for example `--port=8893 --port-retries=0`.
Do not terminate another user's server.

To use an existing data volume, change only this export before launch:

```bash
export PRISM_DATA_ROOT="/absolute/path/to/existing/prism-data"
```

This does not copy data. The notebook discovers its checkout and links its
disposable runtime to the chosen data root. It uses the active kernel's Python
for subprocesses. Never edit files under `.prism_runtime/` as source.

## Saved paper workflow

1. Restart the kernel. Leave every collection, fitting, search, confirmation,
   and reserved access switch `False`. The automatic synthetic self-check
   remains enabled.
2. Choose **Run All Cells**. The notebook builds its runtime, runs preflight
   and embedded tests, and displays saved evidence.
3. Use **Section 17D** for the figure and operational table cells.
4. Use **Section 17E** for manuscript Tables III–VI, confidence intervals,
   and the manuscript evidence check. It exports CSV and LaTeX under
   `paper/results/manuscript/` without raw data or model fitting.
5. Locate the draft's result using the [artifact map](paper-artifacts.md).
   Notebook numbering is not the paper's numbering.

For a fresh kernel when editing one plot, select the first code cell in
Section 17D, run all cells above it, then run its setup and the prerequisite
table cells in order. Keep `RUN_DIAGNOSTIC_RANKER=False`; typography does not
require repeating the classifier comparison.

The static, guarded, and robust fusion candidate reports are matched by
dataset fingerprint. The later shared quantile result uses a different
snapshot and is not silently mixed into these panels. Section 17E uses pinned
bundled v2/v3 and transfer reports; it does not replace them with whichever
local rerun is newest.

Some cells display a bundled image if its local cache is absent. In particular,
the micro-twin illustration needs the semantic cache to regenerate its curves;
the diagnostic figure is displayed from its saved image by default. Displaying
these images does not constitute reanalysis. The main paper's first three
diagrams and literature capability table were authored outside this notebook.

## Edit figure text

The plotting code controls appearance independently of recorded results.

- Notebook Figure 2 / paper Fig. 5: edit `OPERATING_POINT_FONTS` for the
  overall title, panel titles, axis labels, and tick numbers. Keep its explicit
  GridSpec spacing; adding `tight_layout()` may undo the reserved title space.
- Notebook Figure 4 / paper Fig. 6: edit its title, label, and tick font sizes
  in the guarded audit cell. This is the earlier VAR audit, not v3 updating.
- Notebook Figure 6 / paper Fig. 4: edit `generate_digital_micro_twin_figure`.
  Panel (c) is aggregate residual evidence, not the selected v3 statistic.
- Notebook Figure 8 / paper Fig. 7: edit the operational profile cell. Keep
  delay conditional on detected events and replay tied to confirmation time.

The shared save function exports 300 dpi PNG and vector PDF for generated
plots. Existing bundled images without a cache are not converted into genuine
vector curves. Check the exported figure at its final column width before
uploading it to Overleaf.

## Full raw reanalysis

Use the [recorded analysis sequence](drift-aware-analysis.md). Raw telemetry,
progress trackers, and processed caches are not supplied by Git. Verify every
required manifest and the analysis revision's admitted run list before
enabling an analysis. Preserve the original outcomes and write any rerun to a
separate data root. Re-executing an unchanged confirmation is a computational
reproduction, not a new independent confirmation set.

Do not regenerate collection plans, change evidence roles within a revision,
exclude runs based on their alert outcome, or enable reserved access. The
current study did not earn final method freeze. Historical acquisition guides
are not an instruction to collect the 92 reserved runs.

## Environment and verification records

The [source environment snapshot](../reproduction/requirements-source.txt)
records macOS Python 3.13.5 packages captured on 2026-08-28. It is not a
universal lock file and includes macOS packages such as `appnope`. Use
`pyproject.toml` for Linux installation. The repository CI executes the safe
notebook on Python 3.10 and 3.11.

Keep the commit, Python/package versions, input hashes, and thread settings
with a reproduction. Numerical results should match within justified floating
point tolerance; font rendering, PNG bytes, and inference timing may differ.
Source manifests identify the recorded reports, not a guarantee that every
environment reproduces every raw experiment bit for bit.

See [draft alignment verification](../reproduction/verification-draft-alignment.md)
for the checks performed for this update.
