# Paper figure reproduction

The canonical notebook is `notebooks/PRISM_Complete_Experiment.ipynb`.
The summaries under `paper/results/development/` and the figures under
`paper/figures/development/` are publication artifacts, not raw telemetry.

## Open the notebook

Follow the portable quick start in the repository README. Activate the
environment before launching Jupyter and select a kernel from that environment.
Leave collection, fitting, search, confirmation, and reserved-test switches
disabled. In particular, keep `RUN_DIAGNOSTIC_RANKER = False` when formatting
figures; changing its appearance does not require repeating model selection.

For a fresh kernel, select the first code cell in Section 17D and choose
**Run All Cells Above Selected Cell**. Then run the two setup cells in Section
17D and the table/figure cells in order. Save the notebook after editing.

The bundled static, guarded, and robust-fusion reports share a dataset
fingerprint. The setup loads each refinement's JSON and CSV as a pair and
checks its fingerprint before displaying it. A fresh clone can therefore
recreate Figure 2's three method panels without access to local raw data.
The separately revised shared-quantile result is not silently combined with
these earlier results.

Figure 2 has one typography control block, `OPERATING_POINT_FONTS`, near the
top of its cell. `axis_label` changes the x/y axis text, `tick_number` changes
the axis numbers, and the other keys change the panel and figure titles.
Legend and annotation sizes are separate. Its explicit GridSpec layout
reserves space for the larger titles; do not add `tight_layout()` to that cell.

Some cells display bundled images when the corresponding local analysis cache
is absent, including the micro-twin illustration. Formatting such an image
requires its generating cell and cache; displaying the bundled image is not
a new experiment. Raw analysis and confirmation must follow their documented
protocols and cannot be replaced by this figure-only workflow.

## Environment snapshot

`requirements-source.txt` records package versions captured from the local
macOS Python 3.13.5 environment on 2026-08-28. It is a reference
environment snapshot, not proof of the original collection environment and
not a universal cross-platform lock file. It includes platform-specific
packages such as `appnope`; Linux users should use `pyproject.toml` and the
portable quick start instead of installing this snapshot unchanged.

Keep the source commit, Python version, dependency versions, input
fingerprints, and thread settings with a reproduction. Font rendering and
inference timing can vary by platform. A regenerated PNG or timing number
need not be byte-identical even when the numerical monitoring results match.
The diagnostic timing files synchronized in this update preserve an existing
local rerun; the classifier accuracy metrics were unchanged.

This update does not alter the reported development or independent
confirmation outcomes, retrain a detector, or authorize reserved-test access.
