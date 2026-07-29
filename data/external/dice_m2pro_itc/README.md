# Local DICE M2 Pro Baseline

`payload/` is a local, Git-ignored copy of the original DICE Apple M2 Pro
telemetry. Recreate it with section 6 of
`notebooks/PRISM_Complete_Experiment.ipynb`:

```python
DICE_ROOT = REPO_ROOT.parent / "DICE"
RUN_DICE_IMPORT = True
```

Tracked provenance:

- `source.json`: source repository, exact commit, import scope, and byte count;
- `local-files.sha256`: integrity hashes for every copied telemetry file.

The payload is a frozen conference baseline. Do not modify it in place, use it
as new PRISM replication, or combine windows from one case across data splits.
