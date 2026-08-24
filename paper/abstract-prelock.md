# Pre-lock Abstract Draft

Host telemetry offers a practical path to silicon lifecycle management, but
its meaning and availability vary across processor architectures, operating
systems, and sensor interfaces. A detector that appears accurate in a short
evaluation may still produce excessive false alerts during prolonged benign
operation. This paper presents Platform-Robust In-Field Sequential Monitoring
(PRISM), a framework for operational monitoring across heterogeneous computing
platforms. PRISM records each native channel with its unit, source, sampling
cadence, provenance, and availability; maps compatible measurements into
shared functional groups; learns expected behavior using a compact behavioral
digital micro-twin; and converts temporally dependent residuals into sequential
alert evidence. Complete-run experiments on an Apple M2 Pro/macOS host and an
AMD EPYC 9354/Ubuntu host include matched workloads, long benign sessions,
controlled resource pressure, crashes, telemetry interruptions, and
destination-platform calibration. Sequential mechanisms are compared under a
common requirement of no more than 0.25 false-alert episodes per benign hour
and at least 50% event detection. The frozen v3 method detected 71 of 120
controlled event runs (59.2%) during development, but produced six false alerts
over 16.8 hours (0.357 per hour) on an independently collected benign
confirmation set. A final bounded development-only search exposed a narrow
trade-off: 0.244 false alerts per hour with 49.2% detection, or 0.281 with 50.8%
detection. Because neither configuration satisfied both requirements, the 92
locked-test runs remain sealed. A post-hoc complete-run temporal analysis
detected 39 of 60 later-run events (65.0%) but yielded 0.327 false alerts per
hour, confirming that useful detection did not meet the operational alert
budget. A final bounded semantic-corroboration redesign reduced false alerts
but detected at most 16 of 120 events (13.3%), activating the predeclared
stopping rule. These findings demonstrate PRISM's portable cross-platform
monitoring workflow while showing why long-horizon independent confirmation
and explicit reliability gates are necessary before operational claims are
made.

## Claim boundary

- Label the nested temporal result post hoc and the final redesign as a bounded
  stopping experiment; neither is independent confirmation.
- Do not state that G3 passed, that locked testing was completed, or that PRISM
  is deployment-ready.
- Retain complete candidate tables and both failed independent confirmations
  in the supplemental evidence.
- Describe the adaptive rich-tier result as offline retention/duty-cycle replay,
  not measured power or energy savings.
