# Draft alignment verification — 2026-08-28

This update was prepared from `9d69654bc2f48e3ee84896a671ebaa8680e67fb8`
against the supplied 14-page manuscript. The source PDF is not distributed in
the repository; its SHA-256 appears in the manuscript input manifest.

## Scope

- Condensed the README and moved procedures, interpretation, and history into
  `docs/` without removing the original research records.
- Aligned the abstract, outline, notebook narrative, and result labels with
  the reported v3 study. Supporting searches remain separately identified.
- Added Section 17E for checked manuscript summaries and CSV/Overleaf exports.
- Relabeled the micro-twin illustration's aggregate residual evidence and
  enabled vector PDF export alongside PNG for regenerated paper figures.

Collector, detector, and embedded test source are unchanged. Collection plans,
confirmation protocols, recorded model settings, and numerical outcomes are
unchanged. No reserved run was collected, inspected, or scored.

## Checks completed

- Notebook schema and Python syntax checks passed: 80 code cells, including
  one empty cell. All 79 nonempty cells completed without notebook errors.
- All 20 embedded tests and the synthetic analysis checks passed under
  Python 3.13.5 on macOS with single-thread settings.
- A fresh execution without raw data or analysis caches reproduced the
  bundled paper summaries. Cache-dependent illustrations used saved images.
- A separate execution regenerated the micro-twin illustration from the
  existing semantic cache. It did not recollect data, repeat detector search,
  or reevaluate independent confirmation.
- Section 17E checked pinned source hashes, protocol/plan hashes, evidence
  roles, inventory totals, development selection, confirmation outcomes,
  operational scorecard values, and scenario counts.
- Poisson and Wilson intervals were recomputed from the recorded counts.
  Their dependence and selection limitations remain explicit.
- Four generated Overleaf tables compiled with LaTeX and were visually
  checked. The corrected micro-twin figure was also inspected.
- The saved notebook retains the portable `python3` kernel metadata.

Collection, fitting/search, confirmation evaluation, and reserved-access
controls remained disabled. Synthetic checks and paper rendering run with
their documented defaults. This verifies execution and reproduction from
saved evidence, not a new raw-data audit or deployment validation.

The repository's CI workflow independently executes the notebook on Linux
with Python 3.10 and 3.11. Consult the workflow status for the published commit;
the local checks above do not substitute for that status.

## Paper follow-up

See [the paper artifact map](../docs/paper-artifacts.md) for exact Overleaf
placement and two focused clarifications: the earlier transfer checkpoint in
Table VI and the aggregate residual label in Fig. 4(c).
