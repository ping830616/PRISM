# Supporting analyses outside the main narrative

The current draft reports the v3 workflow and confirmation. The following
analyses remain available with their original outcomes. They are not extra
independent confirmations or replacements for the reserved partition.

| Analysis | Notebook section | Recorded outcome |
| --- | --- | --- |
| Bounded v4 persistence search | 17B.9 | 0.244 FAH at 49.2% detection; 0.281 FAH at 50.8%; neither met both G3 limits |
| Post hoc nested temporal validation | 17B.10 | 39/60 events, 65.0%; 11 episodes / 33.6 h, 0.327 FAH |
| Final bounded semantic corroboration | 17B.11 | Best detection 16/120, 13.3%, at 0.056 FAH; no confirmation authorized |
| Conventional complete run metrics | 17B.13 | Supplementary Tables S1–S2 and Fig. S1; not online reliability |
| Post hoc diagnostic design space | 17B.14 | ExtraTrees PR AUC 0.997, ROC AUC 0.986, F1 0.971 on development runs |

The post hoc ranker compares One Class SVM, logistic regression, Random
Forest, ExtraTrees, and gradient boosting. It uses complete run summaries
and evaluated folds excluded from fitting. It addresses offline diagnosis,
not live alert reliability. Its inference times depend on the execution host.

The v4 and later analyses explicitly admit previously evaluated evidence into
a separately labeled development analysis. This does not retrospectively
change the v3 confirmation outcome. No reused set can independently confirm
a newly selected method.

Full records remain in [paper/results/development](../paper/results/development/):

- `table-6-prelock-reliability-checkpoint.csv`
- `nested-run-grouped-inner-candidates.csv`, `nested-run-grouped-outer-runs.csv`,
  and `nested-run-grouped-temporal-result.json`
- `v5-final-semantic-corroboration-candidates.csv` and its selection JSON
- `supplement-s1-dice-comparable-performance.csv` and workload/run score files
- `supporting-diagnostic-ranker-result.json`, run scores, and stress validation

The [historical repository guide](archive/readme-before-draft-alignment.md)
retains the detailed earlier workflow and artifact list. Do not tune further
or recollect confirmation as part of paper figure formatting.
