# Measurement definitions

## Accuracy and coverage

A valid evaluated row has a unique nonempty ID, a nonempty prediction, and a nonempty outcome. All duplicate-ID occurrences are invalid. A valid row with a blank outcome is pending.

- Accuracy = 100 × exact matches / evaluated rows.
- Coverage = 100 × evaluated rows / all supplied rows, including invalid and pending.
- No evaluated rows means accuracy unknown; no supplied rows means coverage unknown.
- Accuracy's verdict is unknown below `min_evaluated_rows`, below minimum outcome coverage, or with invalid result records; the observed percentage remains visible.

The report includes a two-sided 95% Wilson interval using z = 1.959963984540054. It is conditional on an independent binomial sample. Correlated, selected, or unrepresentative observations can invalidate its practical interpretation. By default, status compares the **point estimate**. `accuracy_threshold_basis: wilson_lower_bound` compares the unrounded lower bound instead; the displayed `value` remains point accuracy and `threshold.assessment_value` records the compared value. Count, coverage and validity guardrails apply in both modes. Passing a threshold is not statistical proof of performance.

## Confidence alignment

On evaluated rows with valid confidence, compute mean confidence as a percentage and accuracy on exactly the same paired rows. The score is the absolute gap in percentage points. Both high and low mean confidence can create a gap. Status is unknown below the minimum paired count, if any evaluated row lacks valid confidence, or if accuracy's count, outcome-coverage or record-validity guardrails fail.

This aggregate warning is **not a calibration assessment**: opposing errors can cancel. It does not replace reliability diagrams, proper scoring rules, or a representative evaluation. If the confidence column is absent, this optional diagnostic is unknown and does not enter overall status.

## Cost per correct result

Total cost of **all supplied classification-output rows**, including incorrect predictions, divided by correct evaluated results. It requires valid cost for every row, all outcomes completed and valid, the minimum evaluated count, and at least one correct result. Otherwise its value/verdict is unknown; known cost and coverage remain visible as evidence. No successes cannot yield a zero cost per success.

Costs of omitted retries, infrastructure, review work, and failures are not inferred. Use an upstream accounting definition that captures costs attributable to the output cohort. No-output failures cannot be valid records here; assess full workflow economics separately. With no configured cost target, a computable value remains visible but its verdict is unknown. All cost values use the declared unit. Very large inputs that make the result unrepresentable produce an input error; an unrepresentable known total is null.

## Latency

Mean of valid, nonnegative durations. P95 uses the nearest-rank element at ceil(0.95 × instrumented count). If only part of the sample is instrumented, the measured mean is shown with an unknown verdict. With no configured latency target, the mean remains visible but its verdict is unknown. These are supplied durations, not end-to-end latency measured by the tool.

## Baseline accuracy

Current accuracy minus baseline accuracy, in percentage points. A negative value indicates an observed decline. The verdict requires the minimum evaluated count in both samples, minimum outcome coverage in both, and no invalid result rows. A measured delta may still have an unknown verdict. Decline beyond the tolerance creates attention.

The tool does not test statistical significance, infer a causal model regression, enforce equal sampling periods, or validate equivalent labeling policies. The caller owns comparability.

## Case mix and groups

For each supplied group, show row count, evaluated count, correct count, observed accuracy, and whether its evaluated count meets the same sample guardrail. Overall aggregate adequacy does not establish subgroup adequacy.

Case-mix shift is total variation: 50 × sum of absolute differences between current and baseline group proportions. It ranges from 0% for identical proportions to 100% for disjoint groups. It uses all supplied rows, requires complete nonempty group assignment in both extracts, and uses baseline comparability guardrails for its verdict. A shift above the configured tolerance warns that aggregate accuracy comparisons may reflect different case composition. Groups cannot detect unmeasured differences within each group.

## Overall status

Always includes accuracy and outcome coverage. Also includes:

- Confidence alignment when the configured confidence column exists in current input.
- Cost and latency when their explicit targets are configured.
- Baseline accuracy when a baseline is supplied.
- Case mix when group columns exist in both compared inputs.

Any finding or included attention verdict yields overall attention. Otherwise any included unknown yields unknown; all included ok yields ok. The report's scope note lists these included checks. Missing optional diagnostics remain visible without silently asserting their adequacy. Invalid measurements in present optional columns create findings even without a target.

See [evidence policy](EVIDENCE_POLICY.md) for separate threshold/evidence/verdict semantics and cross-domain examples. Numeric comparisons use unrounded values; report check values are rounded to six decimal places.
