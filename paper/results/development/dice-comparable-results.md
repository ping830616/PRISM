# Supplementary DICE comparable complete run results

## Recommended results text

To support comparison with DICE, we evaluated one cross fitted score per
complete development run. The analysis included 48 benign and 120 controlled
event runs; 16 telemetry interruption runs were routed to the explicit fault
state and excluded from behavioral classification. The frozen v3 sequential
decision detected 71 of 120 events and produced six false alert episodes over
36.53 benign monitoring hours. Its pooled precision was 0.922, recall was
0.592, event F1 was 0.721, and macro F1 was 0.663. The corresponding AUC PR was
0.755, compared with an event prevalence of 0.714, and ROC AUC was 0.527.
Complete run bootstrap intervals were 0.696 to 0.816 for AUC PR, 0.428 to 0.616
for ROC AUC, and 0.649 to 0.788 for event F1.

Apple and AMD results were not identical. Apple reached 0.797 AUC PR, 0.579
ROC AUC, and 0.747 event F1; AMD reached 0.717, 0.469, and 0.694,
respectively. The frozen development FAH values were 0.109 on Apple and 0.219
on AMD, and all 16 telemetry interruption runs were identified as telemetry
faults. PY AI produced the strongest workload ranking (0.838 AUC PR and 0.639
ROC AUC), whereas PY STATS was weakest (0.677 and 0.319). This workload spread
supports reporting both pooled and subgroup results.

## Interpretation boundary

The high precision and event F1 describe the frozen sequential decision on
development evidence. The near chance pooled ROC AUC and the small AUC PR gain
above event prevalence show that the peak run score alone provides weak global
ranking. These metrics therefore complement the operational FAH, delay, and
fault results; they do not replace the separately collected benign
confirmation, which remains the controlling reliability result.

## Paper artifacts

- `supplement-s1-dice-comparable-performance.csv`: pooled and platform summary.
- `supplement-s2-dice-comparable-workload-performance.csv`: workload summary.
- `supporting-dice-comparable-complete-run-scores.csv`: one auditable row per
  complete development run.
- `figure-s1-dice-comparable-discrimination.png`: pooled and platform ROC and
  precision recall curves.
- `$PRISM_DATA_ROOT/processed/prism-analysis-v3-dice-comparable/`: full JSON,
  confidence intervals, scope table, and run scores.
