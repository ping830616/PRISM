# Evidence Aligned Abstract

Host telemetry can support silicon lifecycle management (SLM), but
heterogeneous interfaces and repeated decisions complicate reliable monitoring.
This paper presents the Practical Reliability Investigation of Sequential
Monitoring (PRISM) framework for hybrid host monitoring and reliability
evaluation across Apple M2 Pro/macOS and AMD EPYC 9354/Ubuntu hosts. PRISM
preserves telemetry semantics and availability and predicts benign behavior
using compact behavioral digital micro-twins. Workload-specific supervised
classifiers produce contextual and residual evidence. Residual corroboration
and an empirical sequential rule convert this evidence into persistent alert
episodes. The study contained 208 validated runs outside the reserved
partition: 192 formed the declared v3 development inventory, and 16 provided
independent benign confirmation. Development analysis covered 120 runs with
controlled events and 36.53 h of eligible benign monitoring. The selected
monitor detected 71 of 120 event runs (59.2%) and produced 0.164 false alert
episodes per benign monitoring hour (FAH). The median detection delay was
337.5 s across detected events. It identified all 16 controlled telemetry
interruptions as faults. On the independent 16.8 h benign set, the unchanged
monitor produced six false alert episodes (0.357 per hour), exceeding the
predeclared feasibility limit of 0.25 per hour. The reserved partition,
therefore, remained sealed. This benign set did not independently confirm the
detection of events. Offline replay retained rich telemetry for 0.31% of
eligible confirmation time; it did not measure acquisition or energy savings.
These results establish an auditable workflow for evaluating host monitoring
across platforms and expose the gap between development feasibility and
independently confirmed reliability.

## Claim boundary

- PRISM is a hybrid monitor: the behavioral micro-twin is combined with
  supervised contextual and residual classifiers and a sequential alert rule.
- The 0.25 FAH and 50% detection limits are research feasibility criteria, not
  an industrial deployment standard.
- Independent confirmation evaluates benign false alert reliability; it does
  not independently confirm controlled event detection or delay.
- The rich telemetry result is an offline retention replay, not a measured
  acquisition, energy, storage, or runtime saving.
- The reserved partition remained sealed. Do not claim final held out
  performance or deployment readiness.
