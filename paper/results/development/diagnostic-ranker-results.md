# Post hoc complete run diagnostic ranking

This optional analysis asks a different question from the online PRISM alert
gate: after a complete run is available, can robust temporal summaries rank a
controlled event above benign operation? It uses 152 complete development runs
(32 benign and 120 controlled event runs) and excludes telemetry interruption
runs because those represent the explicit telemetry fault state.

Each run uses a fixed 120 second local baseline followed by a fixed 600 second
observation window. The features summarize level, persistence, change, and
availability without using filenames, run kind, variable run duration, future
confirmation data, or locked data. Two cross validation folds hold out complete
repetitions, so blocks from one run cannot appear in both fitting and scoring.

The event labelled ExtraTrees ranker achieved 0.997 AUC PR, 0.986 ROC AUC,
0.959 precision, 0.983 recall, and 0.971 F1. The 2,000 run bootstrap intervals
were 0.992 to 0.999 for AUC PR, 0.969 to 0.997 for ROC AUC, and 0.947 to 0.989
for F1. Apple and EPYC F1 values were 0.967 and 0.976, respectively. A benign
only one class SVM ablation reached 0.934 AUC PR, 0.881 ROC AUC, and 0.906 F1.
An event labelled logistic comparator reached 0.996 AUC PR and 0.982 ROC AUC,
but its fixed 0.5 threshold produced 0.857 F1, supporting the selected nonlinear
ranker without tuning the reported decision threshold on the held out folds.

Excluded domain stress tests remained favorable but exposed the transfer
boundary. Leaving one workload out at a time produced 0.989 AUC PR, 0.961 ROC
AUC, and 0.954 F1. Leaving one platform out produced 0.945 AUC PR, 0.879 ROC
AUC, and 0.928 F1. The weakest excluded scenario test produced 0.975 AUC PR,
0.973 ROC AUC, and 0.909 F1.

These are post hoc, event labelled development results. They do not repair the
failed independent benign confirmation, replace false alerts per monitored
hour, authorize locked access, or demonstrate deployment readiness. A newly
predeclared independent event confirmation set is required before a final
diagnostic performance claim.

Artifacts:

- `table-11-development-diagnostic-ranker.csv`
- `table-11-development-diagnostic-ranker.tex`
- `supporting-diagnostic-ranker-stress-validation.csv`
- `supporting-diagnostic-ranker-run-scores.csv`
- `supporting-diagnostic-ranker-result.json`
- `../../figures/development/figure-9-development-diagnostic-ranker.png`
