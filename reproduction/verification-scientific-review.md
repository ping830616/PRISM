# Scientific review cleanup — 2026-08-28

Prepared from `6be1cd290ddba3e7c89326c2c1e9c62b5448ff16` against the supplied
14-page manuscript. Its SHA-256 is recorded in the manuscript input manifest.
The PDF and Overleaf project were not modified. Current manuscript wording and
claim boundaries appear in the [evidence aligned abstract](../paper/abstract-prelock.md)
and [paper results guide](../docs/paper-results.md).

## Changes

- Described v3 as a hybrid of a benign predictor, supervised scoring, and
  empirical sequential monitoring. Documented the nine compact states,
  availability loss, classifier features, labels, and training settings.
- Distinguished reported checkpoints from a matched final baseline benchmark.
  Documented cumulative destination calibration prefixes per workload.
- Clarified research feasibility limits, preassigned confirmation groups,
  candidate lock, and final method freeze without changing the protocol.
- Preserved the original confirmation run summary as a hashed manuscript
  input. Exported exact replay accounting and replaced Figure 8(d)'s shared
  gap axis with direct counts and rates.
- Supplied a proposed abstract, an optional DICE extension table, and exact
  Overleaf locations. The external architecture diagram still needs editing
  in its original source.

## Verification

- All 79 nonempty notebook cells completed in a fresh kernel; the remaining
  code cell is empty. No notebook error outputs were produced.
- All 20 embedded tests passed. Synthetic checks retained their defaults.
- Section 17E verified the pinned report and protocol hashes, evidence roles,
  original numerical results, and confirmation session groups.
- Replay totals matched both the per-run and aggregate reports: 37/12,096
  blocks, or 185/60,480 seconds (0.305886%).
- The updated figure was rendered and visually inspected. The optional DICE
  table compiled using IEEEtran without warnings and was visually inspected.
- Only the figure and manuscript export code cells changed. Collector,
  detector, embedded tests, collection plans, confirmation protocols, and
  selected model parameters were unchanged.

This is reproduction from saved reports, plus regeneration of a fixed
illustration from the existing semantic cache. It is not a new raw data audit,
model search, or independent confirmation. No reserved data were accessed.
No reported experimental outcome changed. Regenerated images unrelated to
this cleanup were not included in the update.

## Execution environment

macOS, Python 3.13.5; one numerical thread and `PYTHONHASHSEED=0`.

| Package | Version |
| --- | --- |
| NumPy | 2.3.2 |
| pandas | 2.3.1 |
| SciPy | 1.15.3 |
| scikit-learn | 1.7.1 |
| Matplotlib | 3.10.5 |
| nbconvert | 7.16.6 |
| nbformat | 5.10.4 |
| ipykernel | 6.29.5 |

This is the environment used for this verification, not the original data
collection environment or a replacement for its manifests. Linux notebook
execution is checked separately by the repository CI for Python 3.10 and 3.11.
