# Reviewer package verification — 2026-09-24

## Scope and source

This verifies **regeneration of paper artifacts from bundled numerical
evidence**, not a rerun of the detector on raw recordings. No collection,
detector training, candidate search, threshold changes, or reserved-data access
was performed by the reviewer workflow.

- Repository base: `6289c4dba7bc97ef685f9d6c5e5f8d959db321ca`.
- Manuscript: the 15-page `TR_PRISM` draft, with seven figures and nine tables.
- Overleaf ZIP SHA-256:
  `2a61fe74ba3c79441dda68b0e2592bcb70d26b3ae34f796b1d41737645b25c94`.
- Frozen scientific/reference inputs: 46 SHA-256-verified files.
- Reviewer runtime: a newly created Python 3.12.14 environment on macOS ARM64,
  using only `requirements-reviewer.txt`; `pip check` found no broken requirements.

## Checks actually executed

1. The complete CLI regenerated numerical Tables VI–IX, all twelve Table VIII
   rows, and Figures 4–7 as PNG and PDF. It also copied the explicitly labeled
   authored/reference assets and created an HTML gallery and JSON report.
2. A clean source copy made from the intended Git file inventory was tested
   outside the checkout, with spaces in its path. It contained no `.git`,
   environment, `.prism_runtime`, raw/processed/local data directory, or
   previously generated reviewer output. `PRISM_DATA_ROOT` was deliberately
   set to a nonexistent location.
3. All **19 tests passed**, including full rendering, in that clean copy
   (16.720 s for the recorded final test run). There were no skipped tests.
4. A stdlib-only, foreign-working-directory `--verify-only` subprocess passed
   without scientific packages. Missing or altered inputs, unsafe manifest
   paths, absent plotting data, and incorrect expected values were rejected.
5. Existing outputs were preserved, and failed runs discarded their staged
   results. Tests blocked imports of collection/model-fitting machinery.
6. All four regenerated figure PNGs were visually inspected for readability.

The full test command was:

```bash
PRISM_REVIEWER_FULL_TEST=1 python -m unittest discover \
  -s reproduction -p test_reviewer.py -v
```

The reviewer execution command was:

```bash
python reproduction/reproduce.py --output reviewer-output
```

Each execution records its own Python/package versions, code hashes, input
manifest hash, output hashes and numerical checks in `reproduction-report.json`.
The input-only check does not stand in for numerical execution.

## Scientific results preserved

- 208 admitted runs: 192 development and 16 fresh benign confirmation runs.
- Development: 71/120 controlled-event runs detected; 0.1642336 false alerts
  per benign monitoring hour; 337.48667 s median delay among detected events.
- Confirmation: 6 false alerts in 16.8 h, or 0.3571429 per hour. The
  predeclared 0.25/hour confirmation target remains **failed**.
- Retention replay: 37/12,096 blocks, equivalent to 185/60,480 s (0.305886%).
- Subgroup failures and the 92 unused reserved rows remain explicitly reported.

## Subsequent GitHub Actions verification — 2026-09-24

The published code at commit
`8597a7985990e00703710002532d90674c189328` passed
[reviewer reproduction run 36057529702](https://github.com/ping830616/PRISM/actions/runs/36057529702)
on all five configured environments:

- macOS with Python 3.12;
- Windows with Python 3.12;
- Ubuntu with Python 3.10, 3.12 and 3.13.

Every job installed the pinned requirements, verified the packaged inputs,
ran the unit tests, executed the complete numerical table/figure reproduction
command, and uploaded its output artifact successfully. The optional full-render
unit test is skipped in the default CI unit-test command; the following CLI
step performs the complete rendering on every platform instead.

## Limits of this verification

The local test and remote CI runs above are distinct observations. They establish
successful execution on those tested environments, not every possible machine
or future dependency/platform version. Cross-platform pixel/PDF byte identity
is not promised; numerical content and source integrity are checked.

Figures 1–3 and Tables I–V are authored diagrams/descriptive tables, preserved
as original assets rather than described as computationally regenerated.
Figure 4 uses actual numerical arrays recovered once from the historical fixed
illustration code/cache. That author-side recovery is documented separately;
reviewers do not need the cache or perform the recovery.

The package does not independently authenticate the original raw observations,
demonstrate adaptation benefit, turn failed confirmation into success, or
establish new reliability evidence. See
[the reviewer guide](../docs/reviewer-reproduction.md) and
[collection methodology](../docs/collection-methodology.md) for those boundaries.
