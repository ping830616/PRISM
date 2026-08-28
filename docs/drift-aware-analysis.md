# Analysis sequence for the reported study

For paper formatting, use [saved-result reproduction](reproducibility.md).
The v2 and v3 confirmations are complete. Do not recollect them or enable a
model search just to regenerate a figure.

## Recorded analysis dependencies

All implementation remains in
[`PRISM_Complete_Experiment.ipynb`](../notebooks/PRISM_Complete_Experiment.ipynb).
With raw data available, execute prerequisite definitions in order. Enable
only the specific analysis being reproduced, and return its switch to
`False` afterward. Store a rerun separately from preserved reports.

| Stage | Notebook section | Evidence and output |
| --- | --- | --- |
| Original admission audit | 14 | 160 calibration/development runs; checksum and validity checks |
| Semantic block cache | 15 | Fingerprinted blocks; complete run identities retained |
| Static and guarded comparisons | 17, 17A | Initial candidate surfaces and guarded VAR audit |
| Robust residual fusion | 17B.2 | Initial pooled operating point; not strict acceptance |
| Shared alignment and v2 | 17B.3, 17B.3A | Expanded development and supervised fusion |
| v2 confirmation | 17B.6 | Preserved 17 episodes / 16.80 h result |
| v3 development | 17B.7 | 216 candidates; one passed pooled, platform, and fold requirements |
| v3 confirmation | 17B.8 | Preserved 6 episodes / 16.80 h result |
| Paper displays | 17D | Saved original and v3 operational evidence |
| Manuscript exports and checks | 17E | Revision/progression/transfer tables and intervals |
| Transfer implementation | 18 | Exploratory development calibration, not confirmed v3 transfer |

The original audit uses each platform's progress tracker and raw manifests.
A full archival reanalysis requires `VERIFY_ALL_RAW_CHECKSUMS=True`. An
existing semantic cache or bundled figure cannot replace that check.

## Current gate outcome

The selected v3 monitor recorded 0.164 FAH and 59.2% detection during
development, with all required platform and fold checks satisfied. Its
separate benign confirmation recorded 0.357 FAH, above the 0.25 limit.
Further review, final method freeze, and reserved evaluation remain closed.

The protocols were fixed before collection and remain unchanged. Their
`frozen_method` field denotes the candidate fixed for confirmation; it is
not a final deployment approval. Old report `next_step` strings describe
the stage when the report was written, not today's task.

## Historical record

The [previous procedure](archive/guarded-analysis-before-draft-alignment.md)
retains the original instructions and development checkpoint. Later v4/v5
searches and post hoc validation are documented under
[supporting analyses](supporting-analyses.md), outside the reported v3
confirmation claim.
