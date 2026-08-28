# Experiment artifacts: development and confirmation

This directory retains stable notebook artifact names. **Its name does not
mean every row is development evidence**: Table 9 and Figure 8 include
independent v3 benign confirmation. Dataset fingerprints and evidence roles
remain attached to the underlying reports.

Start with the [current paper artifact map](../../../docs/paper-artifacts.md).
The manuscript has different figure and table numbers. Its primary numerical
exports are generated under [../manuscript](../manuscript/).

## Current paper inputs

| Notebook artifact | Purpose in the paper |
| --- | --- |
| Tables 1–3 | Original 160-run inventory, scenario coverage, and integrity |
| Table 4 / Figure 2 | Initial static, guarded, and robust fusion checkpoints |
| Table 5 / Figure 4 | Earlier guarded VAR audit, not v3 offset updates |
| Figure 6 | Representative behavioral micro-twin illustration |
| Table 9 / Figure 8 | v3 development, independent confirmation, delay, and replay |
| Table 10 | Controlled event detection counts by scenario |

The original candidate snapshot has fingerprint
`2d83c66675a3c4e31c7b85b67b39db5a44ad7862af9f56bc4a4c80c74e0eaf2f`.
Static, guarded, and robust fusion JSON/CSV pairs are bundled. Their method
exposures differ. Later v3 used expanded development evidence; these
checkpoints are not a paired comparison on an identical exposure.

The selected v3 candidate passed G3 and its platform/fold requirements during
development. It recorded 0.357 FAH on the independent benign set, above 0.25.
The 92 reserved runs remained sealed. A fixed candidate is not a final
method freeze or a deployment approval.

## Supporting records

Table 6 retains the v3 confirmation and later v4 boundary points. Tables 7–8
and Figure 7 preserve post hoc temporal validation and the final redesign
stopping record. Full candidate and run tables remain available under
`nested-run-grouped-*` and `v5-final-semantic-corroboration-*`.

Table 11 / Figure 9 and `supporting-diagnostic-ranker-*` describe a separate
post hoc offline classifier comparison. Supplementary Tables S1–S2, Figure S1,
and `supporting-dice-comparable-complete-run-scores.csv` retain conventional
metrics. They do not replace independent benign confirmation or demonstrate
online deployment reliability. See [supporting analyses](../../../docs/supporting-analyses.md).

Generated plots are saved as PNG and vector PDF when their source arrays are
available. A cache-dependent cell may instead display a bundled PNG; no new
calculation or vector reconstruction is implied.
