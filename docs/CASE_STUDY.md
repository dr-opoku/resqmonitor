# Case study: investigate confident but deteriorating ticket routing

**All tickets, labels, confidence, timings and costs are authored synthetic fixtures.** There was no real classifier, customer incident, independent adjudication or observed financial benefit.

## The decision and the reference

A fictional service operation routes tickets into `billing`, `refund` and `account`. The current 40-ticket batch is compared with a separately constructed 40-ticket reference batch. These are hypothetical cohorts, not measured calendar periods or a controlled before/after experiment. The fixed report time is 13 October 2026, 12:00 UTC.

`actual_label` is the author's expected class. In a real use case a business owner must define that reference, arrange independent review/adjudication and record disagreements and pending labels. The engine measures **exact categorical label agreement**; it does not establish reference truth or evaluate arbitrary prose.

## What the supplied records show

| Observation | Baseline | Healthy example | Degraded example |
| --- | --- | --- | --- |
| Correct / evaluated | 36/40 = 90% | 38/40 = 95% | 26/40 = 65% |
| Outcome coverage | 40/40 | 40/40 | 40/40 |
| Current confidence | — | 92% | 94% |
| Absolute paired confidence/accuracy gap | — | 3 percentage points | 29 percentage points |
| Supplied attempt cost / correct | — | EUR 0.80 / 38 ≈ 0.021053 | EUR 2.00 / 26 ≈ 0.076923 |
| Mean / p95 latency | — | 190 / 210 ms | 440 / 460 ms |
| Difference from baseline accuracy | — | +5 percentage points | −25 percentage points |
| Default aggregate | — | `ok` | `attention` |

The example targets point accuracy ≥85%, outcome coverage ≥90%, confidence gap ≤10 percentage points, cost/correct ≤EUR 0.05, mean latency ≤300 ms and a baseline drop ≤10 percentage points. Thresholds are illustrative business choices.

Saved evidence: [healthy text](../examples/healthy.txt), [degraded text](../examples/degraded.txt), [healthy JSON](../examples/healthy.json), [degraded JSON](../examples/degraded.json). Download/open [healthy HTML](../examples/healthy.html) or [degraded HTML](../examples/degraded.html) locally.

## External case analysis: which mistakes matter?

The following confusion counts are calculated directly from the fixtures and regression tested. **They are case-study analysis, not additional metrics implemented by the core report.** Rows are authored actual classes and columns are predicted classes.

| Actual → predicted | Healthy | Degraded |
| --- | --- | --- |
| billing → billing | 13 | 9 |
| billing → refund | 1 | 5 |
| refund → refund | 13 | 9 |
| refund → account | 0 | 4 |
| account → account | 12 | 8 |
| account → billing | 1 | 5 |

The three omitted pairings (`billing → account`, `refund → billing`, `account → refund`) each have zero observations in both cohorts. The complete nine cells sum to 40 per cohort.

A refund routed to account support may delay reimbursement; a billing ticket routed to refunds may create different rework. A service owner should assign priorities and review consequential errors separately. No loss matrix or financial impact is supplied, so no asymmetric-loss calculation or savings claim follows.

The degraded `business` group has 6/20 correct, while `consumer` has 20/20. Each group is below the 30-row evidence minimum and is descriptive only. Unchanged group proportions do not establish comparable difficulty or a causal model regression.

## A percentage is not an acceptance rule

For 38/40 correct, the Wilson 95% interval is approximately 83.50–98.62%. The point estimate passes 85%; the lower bound does not. Selecting `accuracy_threshold_basis="wilson_lower_bound"` therefore changes acceptance. Neither rule validates the labels or sample selection. One correct result stays unknown below the declared sample minimum.

Costs include supplied correct and incorrect attempts. Missing costs/labels cannot become free success. Records with no prediction output and omitted attempts are outside this input contract: an upstream collector must account for failures, retries and allocations. The figures exclude unreported labor, remediation, probes and infrastructure costs; they are not total workflow economics.

## Responsible next step

In this fictional process, the service owner investigates changed routing and label quality, the technical operator checks collection/cost instrumentation, and the program lead agrees acceptance criteria and accountable remediation. The report supports that conversation. It does not change routing, approve automation or grant an agent tool rights.

For another domain, define a finite label contract, reference ownership, pending-outcome handling, representative cohorts, error consequences and complete cost allocation first. Free-form assessments need another contract and judgment reliability evidence.

```bash
python3 -m resqmonitor demo
python3 scripts/reproduce_examples.py --check
python3 -m unittest discover -s tests -v
```
