# PRISM operational results

The selected v3 monitor detected 71 of 120 runs with controlled events
(59.2%) during development. It recorded six false alert episodes over
36.53 h of eligible benign monitoring, or 0.164 FAH. Median detection delay
was 337.5 s among detected events. Detection was 61.7% on Apple M2 Pro and
56.7% on AMD EPYC 9354.

PRISM classified all 16 controlled telemetry interruptions as faults. The
unchanged monitor then recorded six false alert episodes over 16.80 h of
independent benign monitoring, or 0.357 FAH. This exceeded the 0.25 FAH limit,
so final approval and reserved evaluation remained closed.

Eligible confirmation monitoring was 100% valid after startup exclusions.
During offline confirmation replay, the rich tier would be retained for
0.31% of eligible time and omitted for 99.7%. The original traces contained
continuously collected telemetry. These fractions do not measure reductions
in acquisition, energy, processor overhead, storage, or network traffic.

The [paper results guide](../../../docs/paper-results.md) gives scenario
outcomes, evidence roles, and conditional confidence intervals. The
[artifact map](../../../docs/paper-artifacts.md) distinguishes paper Fig. 7
from notebook Figure 8. Conventional diagnostic metrics remain supporting
analyses, not headline validation of the online monitor.
