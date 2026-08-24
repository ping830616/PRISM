# PRISM development evidence

Tables 1--5 and Figures 1--5 are derived from the original calibration and
development snapshot with fingerprint
`2d83c66675a3c4e31c7b85b67b39db5a44ad7862af9f56bc4a4c80c74e0eaf2f`.
Tables 6--10 and Figures 6--8 preserve later pre-lock checkpoint, mechanism,
temporal-sensitivity, stopping-rule, and DICE-comparable complete-run evidence;
their source artifacts and fingerprints are identified in the canonical
notebook. The tracked copies keep paper rendering portable when private raw
telemetry is unavailable.

They are not locked-test claims. Later evidence supersedes the early pooled
development pass: the frozen v3 method failed independent benign confirmation
at 0.357 false-alert episodes/hour, and the bounded v4 search found no setting
meeting both G3 requirements. Post-hoc nested temporal validation reached
65.0% detection but 0.327 FAH. The final semantic-corroboration redesign found
no development-margin pass and therefore triggered the stopping rule.
Development-only transfer analysis reveals strong directional asymmetry; the
46 locked rows per platform remain sealed.

## Primary tables

1. `table-1-dataset-inventory.csv`
2. `table-2-scenario-coverage.csv`
3. `table-3-data-quality.csv`
4. `table-4-headline-method-comparison.csv`
5. `table-5-guarded-update-audit.csv`
6. `table-6-prelock-reliability-checkpoint.csv`
7. `table-7-nested-temporal-validation.csv`
8. `table-8-final-redesign-stopping-record.csv`
9. `table-9-dice-comparable-performance.csv`
10. `table-10-dice-comparable-workload-performance.csv`

Table 7 must be reported as a post-hoc temporal sensitivity result and may not
replace independent confirmation. Table 8 documents why no additional
confirmation or locked-test collection was authorized.

Tables 9 and 10 report secondary, DICE-comparable complete-run metrics. The
pooled frozen v3 decision reached 0.922 precision, 0.592 recall, 0.721 event F1,
and 0.663 macro F1. Its AUC PR was 0.755 against an event prevalence of 0.714,
while ROC AUC was 0.527. These development metrics characterize the selected
rule but do not supersede the failed independent benign confirmation.

The complete nested audit is retained in
`nested-run-grouped-inner-candidates.csv`,
`nested-run-grouped-outer-runs.csv`, and
`nested-run-grouped-temporal-result.json`.

The complete final-redesign audit is retained in
`v5-final-semantic-corroboration-candidates.csv` and
`v5-final-semantic-corroboration-selection.json`. The summary table does not
replace these full candidate and stopping-decision artifacts.

The DICE-comparable audit is retained in
`supporting-dice-comparable-complete-run-scores.csv`. It contains one row per
complete run, fold identity, peak/median/p95 score summaries, frozen alert
outcomes, FAH accounting, delay, fault identification, and an explicit false
locked-access flag. Bootstrap intervals and complete platform/workload scopes
are stored under the processed-data root in
`prism-analysis-v3-dice-comparable/complete-run-performance.json`.

The static and guarded selection pairs retain their complete candidate
evidence. The canonical notebook writes the larger robust-normalization
candidate and selection artifacts under the Git-ignored processed-data root
when Section 17B.2 is explicitly enabled.

## Primary figures

The notebook regenerates eight 300-dpi PNGs under
`paper/figures/development/`: scenario coverage, operating-point tradeoff,
headline method performance, guarded-update safety audit, and research
progression, plus a data-grounded behavioral digital-micro-twin illustration.
Figure 7 is the post-hoc nested temporal analysis and must retain that label.
Figure 8 shows pooled and per-platform complete-run ROC and precision-recall
curves; its precision-recall panel includes the 0.714 event-prevalence baseline.
