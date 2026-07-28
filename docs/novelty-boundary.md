# Novelty and Project Boundary

## Recommended Claim

PRISM is a **cross-platform host-side reliability monitoring framework** that translates heterogeneous telemetry into platform-semantic signals and evaluates established sequential evidence mechanisms under realistic temporal dependence, repeated trials, and long benign operation.

The defensible novelty is the SLM systems design and evidence, not the isolated use of VAR, conformal p-values, martingales, or e-processes.

## Claim Matrix

| Capability | DICE ITC baseline | PRISM journal extension | CITADEL TCAD direction |
|---|---|---|---|
| Primary deployment point | Host | Host/control plane | Edge/near-silicon |
| Platform evidence | Apple M2 Pro only | M2/macOS + EPYC/Linux | DDR4/DDR5 hardware-counter platforms; Apple limited-observability case |
| Telemetry representation | Platform-specific tiers | Shared functional semantics with platform adapters | Stable conditional graph and hardware-aware feature set |
| Behavioral model | Ridge micro-twin | Ridge/VAR comparison; optional guarded host update | CINTAS-oriented compact detector |
| Alerting | Split conformal + fixed persistence | Operational sequential evidence and long-horizon false-alert study | Benign thresholds and lifecycle drift checks |
| Cost study | Mixed versus full feature profiles | Host collection bandwidth and escalation duty cycle | Arithmetic, fixed-point, area, power, RTL/FPGA |
| Diagnosis | Category/subsystem-path evidence | Cross-platform/selective diagnosis stability | Causal/stable feature interpretation |
| Hardware implementation | Projected only | Not claimed | Core contribution |

## What Is Actually New Enough to Test

### N1. Platform-semantic telemetry contract

Rather than requiring channel identity across ARM64/macOS and x86-64/Linux, adapters expose functional groups and explicit availability. Test whether this reduces calibration data or transfer loss relative to:

- raw common-channel intersection;
- platform-local models with no shared representation;
- naive zero filling, included only as a failure baseline.

### N2. Operational sequential reliability

The ITC study reports zero benign-run alerts on a small set of benign runs. PRISM must measure long-horizon false-alert behavior under repeated decisions and temporal dependence. The novelty claim is the SLM evaluation and operational metric contract, not invention of conformal martingales.

### N3. Cross-platform calibration effort

Measure the accuracy/false-alert tradeoff as a function of benign calibration minutes on a newly observed platform. This is more useful than a binary “portable/not portable” claim and aligns with deployment practice.

### N4. Failure-aware monitoring

Evaluate controlled crashes, telemetry gaps, sensor dropout, and degradation proxies. Distinguish:

- an actual workload/system anomaly;
- missing or stale telemetry;
- collector failure;
- benign distribution drift.

### N5. Guarded host adaptation, only if it passes

An update must be quarantined, screened for contamination, compared against a held-out benign reference, versioned, and reversible. Report both successful and rejected updates. Keep hardware update-policy synthesis in CITADEL.

## Claims to Avoid

- “First cross-platform SLM framework” without a completed systematic literature search.
- “Anytime-valid” unless the exact assumptions of the chosen sequential method are met or the statement is qualified.
- “Zero false alarms” without monitored hours, repetitions, and a confidence interval.
- “Fault localization” when only subsystem-path or mechanism evidence is available.
- “Aging detection” when using a synthetic degradation proxy.
- “GPU lifecycle monitoring” from one optional L40S workload.
- “Energy savings” inferred only from channel count.
- “Fleet robustness” from two hosts.

## Reviewer Questions the Paper Must Answer

1. What is substantially new beyond the ITC DICE paper?
2. Why is the telemetry mapping meaningful rather than hand-picked?
3. How are temporal dependence and repeated testing handled?
4. Were test windows leaked into fitting or conformal calibration?
5. How many independent runs and benign monitoring hours support each rate?
6. Does adaptation learn anomalies, and how is rollback validated?
7. What happens when telemetry is missing rather than anomalous?
8. Why does PRISM belong in a reliability journal?
9. Which contributions remain distinct from CITADEL and other related manuscripts?

## Conference-to-Journal Difference Table Template

| Area | ITC paper | Journal manuscript | New evidence |
|---|---|---|---|
| Platforms | One M2 Pro/macOS host | M2/macOS and EPYC/Linux | Repeated dual-platform traces and adapters |
| Micro-twin | Ridge, fixed reference | Ridge/VAR comparison; optional guarded update | Drift and contamination experiments |
| Decision rule | Fixed persistence after split conformal | Sequential evidence comparison | False alerts/hour and detection delay |
| Telemetry policy | Fixed mixed/full profiles | Optional host-side escalation | Duty cycle, bytes/s, latency tradeoff |
| Robustness | Controlled stressors and limited crash pilots | Long benign, crash, interruption, degradation proxy | Independent repetitions and uncertainty |
| Reproducibility | Released notebook and Apple dataset | Platform manifests, locked splits, clean-clone scripts | Journal artifact bundle |
