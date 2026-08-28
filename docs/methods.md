# Methods and terminology

PRISM is a host monitoring framework for silicon lifecycle management (SLM).
Its contribution is the telemetry contract, monitoring workflow, and auditable
evaluation across two hosts, not a new forecasting algorithm or an
unconditional statistical guarantee.

## Telemetry and behavioral reference

The collector records native measurements with units, source, cadence,
provenance, and availability. The adapter maps compatible measurements into
shared functional groups. Missing measurements remain unavailable; they do
not become numerical zeros or behavioral anomalies.

A **behavioral micro-twin** is a compact digital representation of expected
benign behavior. PRISM compares ridge and vector autoregressive (VAR)
references. Their prediction residuals provide evidence about host behavior,
not localization of a physical silicon defect. Five-second decision blocks
retain the identity of their complete run.

## Selected v3 monitor

**v3 is the third declared analysis revision, not a data partition.** Its
predictor learns from benign observations. Its scoring layer is supervised:
two logistic classifiers per workload learn from eligible benign and
controlled event observations and are shared across platforms. One combines
contextual and residual features; the other uses residual features alone.
Their probabilities are combined by the geometric mean.

Development evaluation excludes complete runs in the evaluated fold from
fitting. Before independent confirmation, the selected configuration is fitted
on eligible development evidence. Confirmation never selects its parameters.

The fixed v3 settings are recorded in
[`v3-independent-confirmation.toml`](../configs/v3-independent-confirmation.toml):

| Setting | Value |
| --- | ---: |
| Logistic regularization parameter C | 0.03 |
| Decision block | 5 s |
| Sequential stride | 2 blocks |
| Evidence exponent eta | 0.9 |
| Warning threshold | log(600) = 6.396929655216146 |
| Residual tail rank for corroboration | at most 0.05 |
| Diagnostic window | 6 blocks / 30 s |
| Reset | 6 valid blocks at or below half the warning threshold |
| Startup exclusion | 120 s |

Benign score references are fixed for each platform and workload. The
sequential statistic accumulates empirical rank evidence and restarts at
zero. A warning becomes a behavioral alert only after residual corroboration
within its window. Repeated crossings within an episode do not create extra
alerts. Telemetry faults reset the episode and sequential state.

The earlier guarded VAR comparison updates a shadow predictor. **v3 instead
updates residual feature offsets** using a fixed guard, promotion, and rollback
policy. Fitted predictors, classifier parameters, and benign score references
remain unchanged during evaluation. A changing monitoring state is not
retuning from confirmation outcomes.

## Gates and evidence separation

Gate G3 requires development FAH at most 0.25 and controlled event detection
at least 50%. v3 selection also requires these limits for every platform and
fold of complete runs. The selected v3 candidate satisfied these requirements
**during development**.

Independent confirmation requires FAH at most 0.25 for the pooled set, each
platform, and each fold, plus at least 95% valid monitoring in every run.
It evaluates one unchanged candidate on fresh benign runs. Passing it would
permit further review, not automatic reserved access. The recorded v3
confirmation did not pass, so final approval and reserved evaluation remain
closed.

Each run has one evidence role within an analysis revision. Once a confirmation
result is finalized and preserved, its runs may enter a separately declared
later development revision. That revision needs a new confirmation set.
For the reported v3 analysis, v2 confirmation runs support development; the
fresh v3 set serves confirmation only. Later exploratory analyses do not
change the independence or interpretation of the preserved v3 evaluation.

## Vocabulary used in the paper and repo

| Term | Meaning |
| --- | --- |
| FAH | False alert episodes per eligible benign monitoring hour |
| Detection rate | Fraction of eligible runs with controlled events detected on or after onset |
| Detection delay | Time from onset to first qualifying alert, among detected events only |
| Telemetry fault | Invalid measurement availability, collection, or cadence |
| Abstention | Insufficient valid evidence for a behavioral decision |
| Portability | Common workload functions, semantics, and evaluation rules across hosts |
| Transfer | A separately measured destination calibration experiment, not implied by portability |
| Reserved partition | 92 planned runs not collected, inspected, or scored |
| Fixed candidate | Parameters and policies held unchanged for confirmation, not a final method freeze |

Use active wording, methods in present tense, and completed results in past
tense. Prefer “false alert,” “telemetry interruption,” “complete runs,” and
“for each platform” in prose. Retain the official title and “behavioral
micro-twin,” and preserve exact identifiers in code and historical records.
Define abbreviations once and report every rate with its evidence stage and
denominator.
