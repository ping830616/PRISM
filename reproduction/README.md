# Reproduction records

**Reviewers:** use [the standalone artifact reproduction guide](../docs/reviewer-reproduction.md)
and `python reproduction/reproduce.py --output reviewer-output`. Install the
fixed `requirements-reviewer.txt` environment first. This path regenerates
Tables VI–IX and Figures 4–7, preserves the authored/reference assets separately,
and needs neither raw recordings nor model fitting.

Historical records below describe earlier saved-report notebook executions;
they do not certify the current reviewer workflow. In particular, do not treat
`requirements-source.txt` as the new reviewer's environment lock or as proof
that every historical verification used those exact versions.

The current instructions live in [docs/reproducibility.md](../docs/reproducibility.md).
Use the [paper artifact map](../docs/paper-artifacts.md) to find the relevant
notebook cell and Overleaf output.

- [Source environment snapshot](requirements-source.txt): macOS Python 3.13.5
  package versions captured on 2026-08-28, not a universal Linux lock file.
- [Earlier verification record](verification-2026-08-28.md): safe notebook run
  and figure synchronization at commit 9d69654.
- [Draft alignment verification](verification-draft-alignment.md): checks for
  the current manuscript alignment.

Raw data, private caches, and the Overleaf project are not included in this
directory. Environment snapshots do not replace data provenance.
