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

For HTTPS access to the private repository, enter a fine-grained GitHub personal
access token—not a GitHub or ASU password—at the password prompt. Limit the
token to read-only access to PRISM, give it an expiration, and never put it in a
command, notebook, chat, or remote URL. If server authentication is undesirable,
transfer the repository from the Mac without copying credentials.

## 3. Create the environment

```bash
python3 -m venv .venv
source .venv/bin/activate
python3 -m pip install --upgrade pip
python3 -m pip install -e ".[notebook]"
```

Open a secure local tunnel from a Mac terminal:

```bash
ssh -L 8892:127.0.0.1:8892 <ASURITE-or-user>@<ASU-hostname>
```

In that SSH session, launch Jupyter on the loopback interface:

```bash
cd ~/PRISM
source .venv/bin/activate
python -m jupyter lab \
  --no-browser \
  --ip=127.0.0.1 \
  --port=8892 \
  --ServerApp.port_retries=0 \
  notebooks/PRISM_Complete_Experiment.ipynb
```

Keep the terminal open and paste the complete printed
`http://127.0.0.1:8892/lab?token=...` URL into the Mac browser.

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

Restart the kernel and run the notebook once from the top with every guarded
switch left `False`. Confirm that preflight and all unit tests pass. Then change
and run the section 7 capability-probe cell:

```python
RUN_CAPABILITY_PROBE = True
```

Review:

- CPU model and Ubuntu version;
- readable hwmon temperature/power/energy channels;
- CPU-frequency channel count;
- `perf` availability and `perf_event_paranoid`;
- missing sensors.

The current enriched Linux collector reads available hwmon channels and a
bounded, evenly distributed subset of at most four per-CPU frequency paths
directly from sysfs. It records both the discovered and sampled path counts;
this avoids serially reading every core on high-core-count hosts and preserves
the declared 5 Hz cadence. It does not require `sudo`. `perf` is probed but is
not enabled in the smoke pair until the server's allowed events and permissions
are confirmed.

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

Notebook section 8 automatically detects Linux and runs both the nominal and
matched atomic-pressure smoke executions, followed by the readiness gate:

```python
RUN_SMOKE_PAIR = True
```

After transferring the EPYC directory to the Mac, set
`COMPARE_SMOKE_PAIR=True` in notebook section 9. It automatically selects the
newest valid Apple/Linux pairs from one clean collection commit and reports
cadence, availability, semantic coverage, and portable CPU response. A Linux
run may be valid with no enriched channels, but that absence must remain
explicit and becomes part of the telemetry-availability analysis.

Section 9 reports CPU temperature, CPU power, and peripheral temperature
availability separately. Do not treat an NVMe or network-controller hwmon
temperature as CPU-package temperature, and do not interpret a larger flattened
channel count as richer system observability.

The cell is successful only when it prints both valid run paths and ends with:

```text
EPYC_LINUX is ready for predeclared production collection
```

After both final platform pairs have been copied to the Mac, section 9 must also
confirm that the smoke collection commit matches the current notebook revision
before calibration/development collection begins.

Return `RUN_SMOKE_PAIR` to `False` and save the notebook after collection to
prevent an accidental repeat. Do not run `.prism_runtime` files manually.

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

Preview the next eligible server run:

```python
PLATFORM_ID = "EPYC_LINUX"
PREVIEW_NEXT_RUN = True
```

Execute it only after reviewing the selection:

```python
EXECUTE_PRODUCTION = True
```

Use notebook section 10 for preview, section 11 for one guarded production row,
and section 12 for the daily progress and quality report.

The machine-local `data/collection-progress.csv` is ignored by Git. Back it up
with the raw EPYC directory when transferring data to the Mac.

After the probe, add `perf` events only if the same event definitions remain
available throughout the study. Platform-specific events belong in the enriched
profile and must not be presented as identical to Apple `xctrace` channels.
