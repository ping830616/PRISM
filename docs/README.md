# PRISM documentation

The current paper reports the v3 study on two hosts: 192 runs for declared
development revisions and 16 for independent benign confirmation. The reserved
partition remains sealed. Start with the [repository summary](../README.md).

## Current paper and reproduction

| Guide | Purpose |
| --- | --- |
| [Reviewer artifact reproduction](reviewer-reproduction.md) | One command, no raw data or fitting; all current manuscript assets and regenerated numerical results |
| [Historical collection methodology](collection-methodology.md) | How M2 Pro and EPYC data were collected, validated and assigned evidence roles |
| [Results and evidence roles](paper-results.md) | Counts, denominators, confirmation, uncertainty, and transfer |
| [Methods and terminology](methods.md) | What v3 means and how its monitoring decisions work |
| [Paper artifact map](paper-artifacts.md) | Draft figures/tables mapped to notebook cells and Overleaf files |
| [Evidence aligned abstract](../paper/abstract-prelock.md) | Current abstract wording and manuscript claim boundary |
| [Reproducibility](reproducibility.md) | Terminal setup, saved evidence, raw reanalysis, and figure editing |
| [Analysis sequence](drift-aware-analysis.md) | Sections needed for each recorded analysis stage |
| [Supporting analyses](supporting-analyses.md) | Preserved follow-ups and optional diagnostic metrics |
| [Claim boundaries](novelty-boundary.md) | Contributions and limits relative to earlier work |
| [Paper outline](../paper/outline.md) | Structure of the current manuscript |

## Acquisition and provenance

These guides retain the original acquisition procedures. Their full 252-run
plan is not the completed inventory. Use the reported evidence roles above;
do not start new collection to format figures or reproduce saved tables.

- [Data contract](../data/README.md)
- [Collection design](data-collection.md)
- [End-to-end acquisition roadmap](data-collection-roadmap.md)
- [Apple setup](apple-collection.md) and [ASU Linux setup](linux-asu-collection.md)
- [Original extension contract](extension-collection-contract.md)
- [Frozen experiment matrix](../configs/experiment-matrix.toml)
- [v2 confirmation protocol](../configs/v2-independent-confirmation.toml)
  and [v3 confirmation protocol](../configs/v3-independent-confirmation.toml)

Protocol files and machine-readable result fields retain their original names
and contents for provenance. For example, `locked_test` means the paper's
reserved partition; `frozen_method` records a candidate fixed for confirmation,
not approval for final evaluation.

## Historical planning

- [Research schedule and amendments](research-plan.md)
- [Previous repository guide](archive/readme-before-draft-alignment.md)
- [Previous guarded analysis procedure](archive/guarded-analysis-before-draft-alignment.md)

Historical schedules, proposed next steps, and superseded result summaries are
records, not current instructions. Detailed negative and positive evidence is
retained; narrowing the manuscript narrative does not remove analyses.
