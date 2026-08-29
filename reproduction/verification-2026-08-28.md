# Verification: 2026-08-28

The paper synchronization was prepared from repository revision
`9ad28b9f4616dbd52513bcbf7705b3d66bbaca93` in an isolated checkout.

## Checks completed

- Python 3.13.5 on macOS; `pip check` reported no broken requirements.
- All 78 code cells completed with safe defaults and no notebook errors.
- All 20 embedded source tests passed.
- Synthetic analysis self-checks passed.
- Collection, detector search, fitting, confirmation evaluation, and reserved
  access controls stayed disabled. Only the synthetic self-check switch was on.
- The execution used the isolated checkout's data directory, not local raw
  telemetry or analysis caches. The micro-twin and diagnostic illustrations
  were displayed from bundled images where their generation inputs were absent.
- Figure 2 reproduced 57 static VAR, 88 guarded VAR, and 4,836 robust-fusion
  candidate rows using matching bundled summaries.
- Static and robust reports shared dataset fingerprint
  `2d83c66675a3c4e31c7b85b67b39db5a44ad7862af9f56bc4a4c80c74e0eaf2f`.
- The existing local diagnostic rerun differed from its committed report only
  in inference timing. Classification metrics were unchanged.
- The headline method, operational reliability, and scenario result tables
  were unchanged by the safe-default execution.
- The saved notebook retained the portable `python3` kernel metadata.

This verifies notebook execution and reproduction from saved evidence. It is
not a raw-data reanalysis, a new independent confirmation, or a deployment
validation. The original data and older local working copies were not modified.

Linux execution is checked separately by the repository CI workflow on Python
3.10 and 3.11; its status belongs to the pushed commit, not this local record.
