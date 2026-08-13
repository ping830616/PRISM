# PRISM development evidence

These tables and figures are derived from the calibration and development
partitions associated with dataset fingerprint
`2d83c66675a3c4e31c7b85b67b39db5a44ad7862af9f56bc4a4c80c74e0eaf2f`.
They are bundled so the paper-result cells in the canonical notebook remain
portable when private raw telemetry is unavailable.

They are not locked-test claims. The pooled development-only robust residual
fusion passes Gate G3 at 0.134 false-alert episodes/hour and 51.7% controlled-
event detection. Development-only transfer analysis reveals strong directional
asymmetry; advisor review and method freeze have not occurred, so the 46
locked rows per platform remain unopened.

## Five primary tables

1. `table-1-dataset-inventory.csv`
2. `table-2-scenario-coverage.csv`
3. `table-3-data-quality.csv`
4. `table-4-headline-method-comparison.csv`
5. `table-5-guarded-update-audit.csv`

The static and guarded selection pairs retain their complete candidate
evidence. The canonical notebook writes the larger robust-normalization
candidate and selection artifacts under the Git-ignored processed-data root
when Section 17B.2 is explicitly enabled.

## Five primary figures

The notebook regenerates five 300-dpi PNGs under
`paper/figures/development/`: scenario coverage, operating-point tradeoff,
headline method performance, guarded-update safety audit, and research
progression.
