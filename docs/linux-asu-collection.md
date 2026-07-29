# ASU AMD EPYC Linux Collection

Use this workflow after the Apple smoke pair passes. Do not send passwords,
private keys, tokens, or Duo codes through chat or commit them to the
repository.

## 1. Connect and record the server identity

From your Mac:

```bash
ssh <ASURITE-or-user>@<ASU-hostname>
```

On the server:

```bash
uname -a
uname -m
cat /etc/os-release
lscpu
python3 --version
```

Confirm that the intended system is x86-64 Linux and record the exact EPYC
model. PRISM expects AMD EPYC 9354, but the collector records the observed
model instead of silently assuming it.

## 2. Obtain the private PRISM repository

Use an existing GitHub SSH key or authenticate GitHub CLI on the server:

```bash
git clone git@github.com:ping830616/PRISM.git
cd PRISM
```

If SSH access to GitHub is unavailable, transfer the repository from the Mac
with `rsync` rather than embedding a token in a URL.

## 3. Create the environment

```bash
python3 -m venv .venv
source .venv/bin/activate
python3 -m pip install --upgrade pip
python3 -m pip install -e .
```

If `venv` is missing and you have administrator permission:

```bash
sudo apt-get update
sudo apt-get install python3-venv linux-tools-common linux-tools-$(uname -r) lm-sensors
```

If you do not have `sudo`, ask the server administrator to provide the packages.
Tier-0-like host collection still works without `perf` or `lm-sensors`.

## 4. Inspect Linux telemetry permissions

```bash
command -v perf || true
perf --version || true
cat /proc/sys/kernel/perf_event_paranoid
find /sys/class/hwmon -maxdepth 2 -type f -name '*_input' -readable | head -50
find /sys/class/powercap -maxdepth 4 -type f -readable | head -50
command -v sensors && sensors
```

Do not change `perf_event_paranoid`, kernel modules, or sensor permissions
without ASU authorization. Save the observed limitation as part of the
platform-availability result.

## 5. Run the PRISM capability probe

```bash
source .venv/bin/activate
python3 scripts/probe_collection.py
```

Review:

- CPU model and Ubuntu version;
- readable hwmon temperature/power/energy channels;
- CPU-frequency channel count;
- `perf` availability and `perf_event_paranoid`;
- missing sensors.

The current enriched Linux collector reads available hwmon channels and CPU
frequency directly from sysfs. It does not require `sudo`. `perf` is probed but
is not enabled in the smoke pair until the server's allowed events and
permissions are confirmed.

## 6. Protect a long SSH collection

Use `tmux` or the ASU scheduler rather than relying on one SSH connection:

```bash
tmux new -s prism
cd ~/PRISM
source .venv/bin/activate
```

If this is a shared or scheduled machine, request an exclusive allocation and
record the scheduler job ID. Do not run pressure scenarios on a shared login
node.

## 7. Required EPYC smoke pair

Nominal:

```bash
python3 scripts/collect_run.py \
  --platform-id EPYC_LINUX \
  --workload PY_STATS \
  --scenario NOMINAL \
  --repetition 0 \
  --split smoke \
  --purpose smoke \
  --profile enriched \
  --duration-seconds 30 \
  --sampling-hz 5
```

Atomic pressure:

```bash
python3 scripts/collect_run.py \
  --platform-id EPYC_LINUX \
  --workload PY_STATS \
  --scenario ATOMIC \
  --repetition 0 \
  --split smoke \
  --purpose smoke \
  --profile enriched \
  --duration-seconds 30 \
  --warmup-seconds 10 \
  --sampling-hz 5
```

Run `scripts/validate_run.py` on both outputs. A Linux run may be valid with no
enriched channels, but that absence must remain explicit and becomes part of
the telemetry-availability analysis.

## 8. Transfer raw EPYC runs to the Mac

Raw data are ignored by Git, so `git push` will not transfer them. From the Mac:

```bash
rsync -av --partial --checksum \
  '<ASURITE-or-user>@<ASU-hostname>:~/PRISM/data/raw/EPYC_LINUX/' \
  '/local/path/to/PRISM/data/raw/EPYC_LINUX/'
```

Then validate the transferred directory locally. The checksum manifest detects
partial or modified transfers.

## 9. Production rules

- Production mode requires a clean, committed Git checkout so every trace
  records an immutable software revision.
- Use the same duration, sampling rate, workload code, scenario onset, and
  thread/memory environment on Apple and EPYC.
- Keep `PRISM_NUM_THREADS=1` and `PRISM_STRESS_MB=128` unless a protocol revision
  is declared before production collection.
- Collect at least three independent executions per required cell.
- Preserve failed runs and create replacement IDs.
- Never use locked-test runs to choose thresholds, channels, or methods.
- Record maintenance, other-user interference, scheduler preemption, and
  telemetry permission changes.

After the probe, add `perf` events only if the same event definitions remain
available throughout the study. Platform-specific events belong in the enriched
profile and must not be presented as identical to Apple `xctrace` channels.
