# PRISM operational results

## Recommended results text

PRISM evaluated 120 controlled event runs and 36.53 hours of benign development
monitoring across Apple M2 and AMD EPYC hosts. The frozen development rule
identified 71 controlled events (59.2%) with a median detection time of 337.5 s.
Coverage was 61.7% on Apple and 56.7% on AMD, a five percentage point platform
gap. Seven of nine controlled event scenarios reached at least 50% complete run
coverage, including both processor pressure scenarios and thermal and power
shift proxies.

All 16 telemetry interruption runs were routed to the explicit telemetry fault
state, and the independent confirmation retained 100% valid monitoring time.
The adaptive collection controller used the rich telemetry tier for only 0.31%
of independent replay time, avoiding rich collection for 99.7% of the trace.
This result is an offline duty cycle measurement and is not presented as direct
energy savings.

Development false alert rates were 0.109 episodes/h on Apple and 0.219
episodes/h on AMD. The separately collected 16.8-hour benign confirmation set
produced 0.357 episodes/h, above the predefined 0.25 episodes/h reliability
limit. The confirmation therefore remains the controlling result: PRISM
demonstrates a portable and auditable monitoring workflow, but the evaluated
detector is not claimed to be deployment ready and the locked test remains
sealed.

## Primary artifacts

- `table-9-operational-evidence-scorecard.csv`: operational metrics by platform.
- `table-10-scenario-detection-coverage.csv`: controlled event counts by scenario.
- `figure-8-operational-reliability-profile.png`: integrated operational profile.

Conventional AUC, ROC, precision, recall, and F1 results remain available as
Supplementary Tables S1--S2 and Figure S1.
