# Data Contract

Raw telemetry is not stored in this scaffold.

## Required Layout

```text
data/
  raw/
    <platform_id>/
      <collection_date>/
        <run_id>/
          telemetry.*
          events.*
          platform.json
          collection.json
          checksums.sha256
  processed/
    <dataset_snapshot_id>/
      observations.parquet
      runs.parquet
      channels.parquet
      splits.json
      manifest.json
```

## Run Identity

Every independent execution receives a unique `run_id`. Windows from the same run inherit that ID and must never appear in multiple train/calibration/development/test partitions.

## Required Run Metadata

- platform ID, architecture, operating system, kernel/version;
- CPU/GPU model and relevant firmware/driver versions;
- workload, scenario, repetition, and start/end timestamps;
- collector names, versions, command lines, and sampling cadences;
- anomaly or crash onset when controlled and known;
- telemetry interruption interval when injected;
- raw file hashes;
- collection failure and exclusion reason, if any.

## Channel Metadata

Each channel records:

- native platform name and units;
- semantic group;
- sampling cadence;
- source API/tool;
- whether it is cumulative, instantaneous, or derived;
- missingness semantics;
- transformation applied during processing.

Unavailable channels remain unavailable. Do not represent unavailable telemetry with arbitrary zeros.

## Data Freeze

Create a new immutable `dataset_snapshot_id` when:

- raw data changes;
- an exclusion decision changes;
- a processing transform changes;
- run labels or onset annotations change.

Generated results must record the snapshot ID and input hashes.
