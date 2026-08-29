# Abstract for scientific review

Host telemetry can support silicon lifecycle management, but heterogeneous
interfaces and repeated decisions complicate reliable monitoring. This paper
presents PRISM, a hybrid monitoring and reliability evaluation framework for
Apple M2 Pro/macOS and AMD EPYC 9354/Ubuntu hosts. PRISM preserves telemetry
meaning and availability, predicts benign behavior with a compact behavioral
micro-twin, and combines contextual and residual evidence through supervised
classifiers fitted for each workload. Empirical sequential evidence and
residual corroboration govern alerts. The study contains 208 validated runs
outside the reserved partition: 192 supported declared development revisions,
and 16 provided independent benign confirmation. Development analysis covered
120 runs with controlled events and 36.53 h of eligible benign monitoring.
The selected monitor detected 71 of 120 event runs (59.2%) and produced 0.164 false
alert episodes per benign monitoring hour. Its median detection delay was
337.5 s among detected events. It identified all 16 controlled telemetry
interruptions as faults. On the independent 16.8 h benign set, the unchanged
monitor produced six false alert episodes (0.357 per hour), exceeding the
predeclared feasibility limit of 0.25 per hour. The reserved partition
therefore remained sealed. This benign set did not independently confirm
event detection. Offline replay retained rich telemetry for 0.31% of eligible
confirmation time; it did not measure acquisition or energy savings. These
results establish an auditable workflow for evaluating host monitoring across
platforms and expose the gap between development feasibility and independently
confirmed reliability.

Index Terms: Silicon lifecycle management, host telemetry, anomaly detection,
behavioral digital twins, sequential monitoring, reliability evaluation.

The filename is retained for existing links. This proposed revision makes
the supervised layer explicit and separates development sensitivity from
independent benign confirmation. See the [exact Overleaf replacements](../docs/scientific-review-edits.md)
for locations in the supplied draft. The PDF and Overleaf project are not
modified by this repository update.
