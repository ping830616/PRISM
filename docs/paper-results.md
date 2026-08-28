# Reported results and evidence roles

This guide follows the supplied 14-page draft dated 2026-08-28. The
[notebook artifact map](paper-artifacts.md) identifies the underlying files.
The main paper reports v1–v3; [later analyses](supporting-analyses.md) remain
available separately and are not independent validation of v3.

## Inventory

| Evidence | Added runs | Cumulative runs | Role in the reported v3 evaluation |
| --- | ---: | ---: | --- |
| Original matched inventory | 160 | 160 | 8 calibration and 152 development runs |
| Balanced benign supplement | 16 | 176 | Expanded development |
| v2 benign confirmation | 16 | 192 | Later declared development, after preserving the v2 result |
| Fresh v3 benign confirmation | 16 | 208 | Independent confirmation only |

Thus, 192 runs supported declared development revisions and 16 evaluated the
unchanged v3 monitor. The original inventory contains 80 admitted runs per
host across 11 scenarios. The 92 planned reserved runs are outside these 208.
They were not collected, inspected, or scored.

The original nominal and long benign inventory contains 4.799 h per host,
9.599 h combined. The selected monitor uses **36.53 h** of eligible benign
development monitoring, including eligible clean intervals before event onset.
The independent set supplies **16.80 h**, or 8.40 h per host. These denominators
apply each method's validity, startup, and calibration exclusions; they are not
raw recorded durations. Totals are computed before rounding.

## Selected v3 results

| Metric | Apple M2 Pro | AMD EPYC 9354 | Pooled |
| --- | ---: | ---: | ---: |
| Development detected / eligible events | 37/60 | 34/60 | 71/120 |
| Development detection | 61.7% | 56.7% | 59.2% |
| Development false alert episodes | 2 | 4 | 6 |
| Eligible benign development time | 18.27 h | 18.27 h | 36.53 h |
| Development FAH | 0.109 | 0.219 | 0.164 |
| Median delay among detected events | 302.5 s | 347.5 s | 337.5 s |
| Telemetry interruptions identified | 8/8 | 8/8 | 16/16 |
| Independent confirmation runs | 8 | 8 | 16 |
| Independent benign monitoring | 8.40 h | 8.40 h | 16.80 h |
| Independent false alert episodes | 3 | 3 | 6 |
| Independent confirmation FAH | 0.357 | 0.357 | 0.357 |
| Valid eligible confirmation time | 100% | 100% | 100% |
| Rich tier active in confirmation replay | 0.21% | 0.40% | 0.31% |

Development satisfied G3 and the required platform/fold checks. Independent
confirmation exceeded the 0.25 FAH limit. These are different stages, not
contradictory gate decisions. Confirmation contained no controlled events, so
it did not re-estimate detection or delay.

Scenario detection was 75.0% for address translation pressure and thermal
shift, 68.8% for atomic contention, and 62.5% for branch, cache, memory
bandwidth, and power conditions. Degradation proxies reached 37.5%; controlled
crashes reached 25.0%. Telemetry interruption was assessed separately through
the fault state.

## Revision and comparison boundaries

v2 confirmation recorded 17 episodes / 16.80 h, or 1.012 FAH. v3 confirmation
recorded 6 / 16.80 h, or 0.357 FAH. The sets were collected separately: this
is not a paired estimate of improvement.

The initial checkpoints were static VAR (24.81 FAH, 97.5% detection), guarded
adaptive VAR (0.90, 44.2%), and robust residual fusion (0.13, 51.7%). The
last satisfied the pooled criterion but did not advance through the robustness
audit. v3 used expanded development evidence. The paper's progression table
does not compare all methods on an identical monitoring exposure.

The earlier guarded VAR audit counted 17,767 accepted and 6,929 rejected
update decisions, 1,402 promotions, 192 fault freezes, and 9 rollbacks. These
are controller actions, not independent runs. They demonstrate exercised
control paths, not proof that every accepted update represented benign drift.

## Transfer and replay

The preserved transfer curve uses the earlier robust residual fusion and
persistence checkpoint, not the selected v3 sequential controller. At 0, 1,
2, 4, 8, and 12 destination minutes, no point met both G3 limits in either
direction. Without destination calibration, M2 to EPYC reached 0.268 FAH and
58.3% detection; EPYC to M2 reached 1.071 FAH and 6.7% detection. Shared
semantics therefore do not establish reliable detector transfer.

The **0.31%** replay result uses eligible v3 confirmation time. The separate
**1.23%** development replay result uses 58.93 h of eligible monitoring across
benign and event periods, not the 36.53 h benign FAH denominator. All telemetry
was collected continuously. Replay estimates time when richer data would be
retained, not measured energy, acquisition, storage, network, or runtime savings.

## Statistical uncertainty

| Quantity | Reported 95% interval |
| --- | --- |
| Development FAH | [0.060, 0.357] |
| Independent confirmation FAH | [0.131, 0.777] |
| Each host's confirmation FAH | [0.074, 1.044] |
| Development detection, 71/120 | [50.2%, 67.5%] |

FAH uses exact Poisson intervals; detection uses a Wilson interval. These
intervals assume Poisson episode counts and independent binary run outcomes,
respectively. They do not adjust for dependence between runs or development
selection. Section 17E recomputes them from recorded counts. Two hosts and
controlled operational proxies do not establish fleet reliability, physical
aging detection, or deployment readiness.
