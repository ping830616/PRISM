# Focused edits before scientific review

These locations refer to the supplied 14-page `WIP_PRISM.pdf`, SHA-256
`d3281421f2e342d0bbfec0e7d4eb0da82f370fe215ae020ff07de56365658764`.
The instructions below edit presentation, not recorded methods or outcomes.
Do not change a protocol, rerun a search, or remove inconvenient outcomes to
make the wording fit. The PDF and Overleaf project have not been edited here.
After adding a table, LaTeX will renumber later tables automatically.

## 1. Title and scope of the claim — page 1

Recommended title for discussion with Krish:

```latex
\title{PRISM: Reliability Evaluation of Host Telemetry Monitoring
for Silicon Lifecycle Management}
```

This preserves the project identifier without claiming demonstrated robustness
of the detector. If you retain the expanded project name instead, add the
following immediately after its first definition in the Introduction:

```latex
The name denotes the goal of monitoring across heterogeneous platforms,
not a claim that the selected detector transfers reliably between hosts.
We evaluate that goal through development checks and independent benign
confirmation.
```

Do not redefine “robust” as a demonstrated property of the evaluation workflow
without evidence. A transparent workflow is auditable; that is the supported claim.

## 2. Replace the complete abstract and add Index Terms — page 1

```latex
\begin{abstract}
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
120 runs with controlled events and 36.53~h of eligible benign monitoring.
The selected monitor detected 71 of 120 event runs (59.2\%) and produced 0.164 false
alert episodes per benign monitoring hour. Its median detection delay was
337.5~s among detected events. It identified all 16 controlled telemetry
interruptions as faults. On the independent 16.8~h benign set, the unchanged
monitor produced six false alert episodes (0.357 per hour), exceeding the
predeclared feasibility limit of 0.25 per hour. The reserved partition
therefore remained sealed. This benign set did not independently confirm
event detection. Offline replay retained rich telemetry for 0.31\% of eligible
confirmation time; it did not measure acquisition or energy savings. These
results establish an auditable workflow for evaluating host monitoring across
platforms and expose the gap between development feasibility and independently
confirmed reliability.
\end{abstract}

\begin{IEEEkeywords}
Silicon lifecycle management, host telemetry, anomaly detection,
behavioral digital twins, sequential monitoring, reliability evaluation.
\end{IEEEkeywords}
```

The repository abstract uses this wording. The result remains a legitimate
study; its design should not be described as wholly benign only.

## 3. Introduction and architecture — pages 2 and 5

Replace the contribution beginning “Reliability gates for micro-twin
monitoring” with:

```latex
\item \textbf{Hybrid monitoring with explicit feasibility gates:}
PRISM combines a benign micro-twin with supervised contextual and residual
classifiers. During development, the selected monitor detected 59.2\% of
controlled events at 0.164~FAH. Median delay among detected events was
337.5~s.
```

In Section III-B, replace the paragraph beginning “For a valid observation”:

```latex
For a valid observation, the micro-twin predicts expected telemetry using
parameters learned from benign data. The selected v3 monitor passes contextual
and residual features to two supervised classifiers for the known workload.
Their fused score supplies the sequential evidence, and a separate residual
tail rank corroborates warnings. Invalid collection conditions produce a
telemetry fault; insufficient valid evidence prevents a behavioral decision.
```

In Fig. 3's editable source, insert **FUSE: supervised context + residuals**
between COMPARE and DECIDE. Add **Workload selects classifier pair** as a
short label. Rename the lower loop **GUARDED STATE UPDATE** and distinguish
**Earlier VAR: shadow predictor** from **v3: residual offsets**. The latter
policy also operates unchanged during confirmation; it is not restricted to
development. Use this caption:

```latex
\caption{Hybrid PRISM monitoring, guarded state updates, and evidence
separation. The selected v3 monitor fixes its predictors and classifiers
while applying a predeclared residual offset policy.}
```

The diagram source is external to the notebook; these are editing instructions,
not a claim that the diagram has already been changed.

## 4. Classifier inputs and training — Section III-C, pages 6–7

Replace the paragraph starting “The selected v3 monitor adds a supervised
scoring layer” through “Confirmation observations do not enter model fitting
or parameter selection” with:

```latex
The selected v3 monitor combines the benign reference with supervised
scoring. Its nine compact states describe compute activity, scheduler pressure,
memory pressure, storage activity, network activity, compute variability,
memory variability, input and output variability, and availability loss.
Each state and its prediction residual contributes signed level, absolute
level, signed first difference, and absolute first difference features.
Scaling uses the first 120~s of each run; a benign empirical quantile map
then aligns the features. The joint classifier uses 72 features, and the
residual classifier uses 36.

Two logistic classifiers are fitted for each workload and shared across
platforms. The negative class uses at most 360 valid nominal blocks per run
after startup. The positive class uses at most 48 valid blocks within the
first 240~s after a controlled event. Telemetry interruption runs do not
supply positive labels. Sampling is deterministic from the run identifier.
Both classifiers use balanced class weights, the liblinear solver, a maximum
of 2000 iterations, and random seed 123. The selected regularization parameter
is $C=0.03$. Their probabilities are combined by the geometric mean.

Development evaluation excludes each complete evaluated run from fitting.
The benign feature maps and score references use only eligible fitting
observations. Before independent confirmation, the selected configuration
is fitted using eligible development evidence. All 16 confirmation runs use
this same configuration. Workload identity selects a classifier pair; this
study does not validate detection for an unseen workload.
```

Keep the following distinction explicit: the predictor learns from benign
observations, but the scoring layer uses event labels. The fixed empirical
score references are derived from benign fitting scores, not an independent
conformal calibration set.

### Additional implementation mismatch: availability — page 6

Replace “Availability is represented separately and gates score calculation
rather than contributing directly to the behavioral score” with:

```latex
Explicit validity checks gate behavioral decisions. The compact v3
representation also includes an aggregate availability loss state, so
availability can affect its model features as well as its validity checks.
```

The broad registry includes thermal, power, and optional accelerator channels;
do not present that registry as the selected v3 classifier's feature list.
The nine states above describe the implementation actually evaluated.

## 5. Remove unsupported comparison claims — pages 3, 5, 7–8

**Section II-C:** replace the paragraph starting “PRISM does not assume that
theoretical guarantees” with:

```latex
PRISM does not assume that theoretical guarantees automatically apply to
dependent host telemetry. Its implementation includes persistence, CUSUM,
EWMA, and empirical sequential evidence for development exploration. The
reported results focus on representative development checkpoints and one
selected v3 monitor, not a matched benchmark of every rule on the final
evidence. FAH measures the burden of repeated false alerts and complements
classification metrics such as the $F_1$ score.
```

**Section III-A, page 5:** replace “All decision rules are compared under
the false-alert requirement” with:

```latex
Candidate selection uses the predeclared development feasibility limits.
```

**Section III-D, page 7:** replace the paragraph starting “For each comparison
of sequential rules” with:

```latex
The implementation provides persistence, EWMA, and CUSUM for exploratory
development comparisons. The current paper does not report a complete
matched comparison of these rules on the final v3 evidence. The selected
v3 rule uses classifier fusion and empirical sequential accumulation.
```

For a shorter main paper, move the persistence discussion and Eqs. (18)–(20)
to supplementary implementation details. Keep the v3 statistic and its reset
and corroboration rules. Do not delete or cherry-pick the saved search results.

**Section III-F, page 8:** replace the paragraph starting “The semantic
representation is compared with” with:

```latex
The reported transfer analysis evaluates the shared semantic representation
with varying amounts of benign destination calibration. It does not establish
superiority over a native channel intersection, independent models for each
platform, or zero substitution. Those ablations are outside the reported
comparison. The calibration curve remains an exploratory development result.
```

Also narrow the claims to report **recovery** in Section III-A unless you add
a defined recovery metric and its results. The current manuscript reports
episode reset rules, not a separate recovery benchmark.

## 6. Make G3's meaning explicit — Section IV, page 9

After the paragraph defining the pooled G3 limits, add:

```latex
G3 is a research feasibility screen, not a deployment acceptance standard.
The FAH limit corresponds to one episode per four benign monitoring hours
in aggregate, and the detection limit requires sensitivity to at least half
the controlled event runs. These limits prevent a low alert rate alone from
qualifying a detector. They do not establish an acceptable operating point
for a particular industrial application.
```

This is an interpretation of the recorded limits, not an invented account of
why they were originally chosen. If an application cost model motivated them,
Krish should confirm that rationale and its evidence before it is added.

Replace the page-9 paragraph starting “Independent confirmation requires” with:

```latex
Independent confirmation requires FAH at or below 0.25 for the pooled set,
each platform, and each of two preassigned session groups, with at least
95\% valid monitoring in every run. The protocol calls these groups folds.
Each contains one run for every platform and workload combination, giving
eight runs per group. They are reporting strata, not cross validation folds;
neither group fits a model for the other. Passing confirmation permits
further review. Reserved evaluation additionally requires formal approval
and final method freeze. Because confirmation contains only benign runs,
it does not independently validate controlled event detection or delay.
```

**Keep the group requirement.** It appears in the original protocol and was
not an accidental carry-over from development cross validation.

Where the draft excludes all “abstention periods” from exposure, use the
precise v3 rule instead:

```latex
The v3 denominator includes blocks after startup with valid telemetry and
finite classifier scores and tail ranks. A warning without residual
corroboration does not by itself remove otherwise valid monitoring time.
```

## 7. Candidate lock versus final freeze — pages 5, 7, and 9

Use **candidate lock** for fixed features, parameters, and runtime policies
before independent confirmation. Use **final method freeze** only for formal
approval after confirmation and the required reviews. Replace ambiguous
phrases such as “frozen v3 method” in new prose with **locked v3 candidate**.
Do not rename historical configuration keys or the frozen protocol files.

## 8. Transfer procedure — Section V-D, page 11

Replace the opening paragraph with:

```latex
Table~\ref{tab:transfer_calibration} reports the earlier robust residual
fusion checkpoint with probability persistence, not the selected v3 monitor.
For each source workload, the source classifier and its threshold and
persistence settings remain fixed. With no destination calibration, the
source behavioral reference is reused. Positive calibration budgets refit
the behavioral reference using cumulative prefixes of the destination's
single nominal calibration run: its first 1, 2, 4, 8, or 12 minutes.
The budget is per workload, so 12 minutes corresponds to 48 minutes across
the four workloads. Destination event labels are not used for fitting.
The analysis uses one prefix at each budget and does not estimate variability
across alternative calibration segments.
```

In Section III-F, replace the broader claim that destination calibration
re-estimates all normalization, behavioral, residual, and decision parameters:

```latex
For the recorded transfer checkpoint, a positive destination budget refits
the behavioral reference from benign destination telemetry while retaining
the source classifier and its probability persistence settings.
```

Repeating calibration across alternative segments could strengthen a future
analysis, but it is a new experiment, not an editorial correction.

## 9. DICE extension — add after Table I's discussion

An optional compact table is supplied in
[`table-dice-extension.tex`](../paper/review/table-dice-extension.tex).
Upload it to `tables/` and insert:

```latex
\input{tables/table-dice-extension.tex}

Table~\ref{tab:dice_prism_extension} distinguishes the inherited behavioral
reference from the added evaluation and monitoring mechanisms. DICE reports
24 workload and condition cases on one host. PRISM evaluates 208 validated
runs across two hosts and separates development from fresh benign
confirmation. These are different benchmarks; their detection rates do not
establish a paired improvement over DICE.
```

Use this table to replace repetitive extension prose, not as an additional
performance leaderboard. The DICE counts and separation description were
checked against the supplied `ITC_DICE.pdf`, Sections III-F and IV–V.

## 10. Figures and replay accounting — pages 7 and 12

- **Fig. 4(c):** use “Aggregate residual evidence.” This correction is already
  in the notebook Figure 6. Upload its new PNG or generated vector PDF.
- **Fig. 7(d):** use the updated notebook Figure 8. It now gives three direct
  measurements with numerators, denominators, and rates. It no longer plots
  unlike quantities as gaps from 100%.
- **Fig. 3:** apply the editable-source instructions in item 3 above.

Replace the paragraph beginning “The integrity results in Fig. 7(d)” with:

```latex
The integrity summary in Fig.~\ref{fig:operational_reliability_profile}(d)
reports 16 correctly identified telemetry interruption runs out of 16.
All 12,096 eligible confirmation blocks remained valid. Rich telemetry was
retained during 37 of these blocks in replay. At 5~s per block, this is
185~s out of 60,480~s, or 0.306\% (rounded to 0.31\%). The corresponding
fractions were 13/6,048 blocks on Apple and 24/6,048 on AMD. These values
estimate selective retention from continuously collected traces, not measured
reductions in acquisition, energy, or storage costs.
```

## 11. Implementation and package provenance — end of Section IV

```latex
The implementation and reproduction instructions are maintained at
\url{https://github.com/ping830616/PRISM}. The v3 confirmation records
identify collector revision \texttt{b322457}; Table~\ref{tab:prism_experimental_setup}
reports Python versions for the two hosts. The repository archives the
analysis environment, source hashes, and a paper result verification cell.
The archived reproduction environment is distinct from the original
collection environment. Raw run manifests remain the authority for
collector and native utility versions.
```

Load `url` or `hyperref` if needed. Repository access must be arranged for
reviewers while it is private. Do not relabel the August 28 reproduction
package snapshot as the environment that originally collected or fitted the
experiments. An exact `macmon` version should be quoted only from its recorded
collection metadata, not the version currently installed on the laptop.

## 12. Conclusion — replace only its opening and replay sentences

Opening:

```latex
This paper presented PRISM, a hybrid host monitoring framework that combines
a benign behavioral micro-twin, supervised scoring, and sequential evidence
within an explicit reliability evaluation protocol.
```

Replay sentence:

```latex
Offline confirmation replay retained rich telemetry for 185 of 60,480
eligible seconds (0.31\%), without measuring acquisition or energy savings.
```

Keep the existing development numbers, failed confirmation result, and sealed
reserved partition. Avoid claiming deployment readiness or independently
confirmed event sensitivity.

## Remaining scientific decisions

The focused edits do not make acceptance predictable. Krish should review the
title and framing, justification of the feasibility limits, independence and
scope of the reported evidence, and whether extra ablations or calibration
draws are necessary for the target journal. Do not start v4 or change the
sealed partition as part of this wording pass.
