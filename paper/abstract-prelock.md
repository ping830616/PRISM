# Abstract aligned with the current draft

Silicon lifecycle management (SLM) requires dependable monitoring after
deployment because workloads, software, environmental conditions, and device
aging can alter system behavior. Heterogeneous platforms expose different
operating system telemetry and hardware signals, while short evaluations can
conceal excessive false alerts during continuous operation. This paper
presents Platform-Robust In-Field Sequential Monitoring (PRISM), a framework
for host monitoring across heterogeneous platforms. PRISM preserves signal
meaning and availability, maps compatible measurements into shared functional
groups, learns benign behavior with a compact behavioral micro-twin, and
converts prediction residuals into sequential alert evidence. We evaluated
PRISM on Apple M2 Pro/macOS and AMD EPYC 9354/Ubuntu hosts using 208 validated
runs outside the reserved partition. Of these, 192 supported declared
development revisions, including 120 runs with controlled events and 36.53 h
of eligible benign monitoring; 16 independently collected benign runs
evaluated the unchanged monitor. During development, the monitor detected
71 of 120 runs with controlled events (59.2%), produced 0.164 false alert
episodes per benign monitoring hour, and achieved a median detection delay
of 337.5 s among detected events. It classified all 16 controlled telemetry
interruptions as telemetry faults. On the independent 16.8 h benign set, the
monitor produced six false alert episodes (0.357 per hour), exceeding the
predeclared limit of 0.25 per hour; the reserved partition therefore remained
sealed. During offline replay, the adaptive controller requested rich
diagnostic telemetry for only 0.31% of eligible monitoring time. These results
establish a portable and auditable behavioral micro-twin workflow for SLM
across platforms and demonstrate why independent benign confirmation must
precede final evaluation and deployment.

The filename is retained for existing links. This text follows the supplied
2026-08-28 draft, with unnecessary prose hyphens removed. Detailed method and
claim definitions are in [the methods guide](../docs/methods.md). The 0.31%
value describes confirmation replay, not measured acquisition or energy savings.
