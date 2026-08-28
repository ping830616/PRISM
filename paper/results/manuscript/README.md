# Current manuscript exports

Section 17E of the canonical notebook verifies pinned source hashes and
regenerates Tables III–VI as CSV and LaTeX, the conditional uncertainty table,
and `paper-consistency-check.json`. Run it after Section 17D.

The [artifact map](../../../docs/paper-artifacts.md) gives exact Overleaf
locations and interpretation. The original experiment results and plans have
not changed. This is reproduction from saved summaries, not another raw
validation pass, model search, or independent confirmation.

## Pinned sources

`sources/input-manifest.json` records input hashes and the reviewed PDF's
fingerprint. The PDF itself is not uploaded. Sources preserve the original
v2/v3 reports, initial inventory and checkpoints, and the earlier transfer
curve. Historical `next_step` fields are retained as recorded; the current
confirmation outcome supersedes the old instruction to collect confirmation.

The transfer CSV is an earlier robust fusion/persistence analysis, not the v3
sequential controller. Do not overwrite this curve with a new exploratory
Section 18 run while keeping the old paper claim.

The generated tables contain formatted values from these pinned inputs.
Their captions and column layout may be adjusted in Overleaf without changing
counts, denominators, evidence roles, or outcome labels. Missing confirmation
entries for v1 are dashes, not zero events.
