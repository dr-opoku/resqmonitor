# Input and configuration

## Prediction records

UTF-8 CSV, nonempty unique headers, exactly one field per header for each record. Headers/cells are trimmed and empty lines skipped. Header-only CSV means no observations. Limit: **5 MiB and 50,000 records per CSV**; standard-library CSV field-size limits also apply. Up to 100 distinct labels and 100 distinct nonempty groups per extract are supported.

```csv
record_id,predicted_label,actual_label,confidence,cost,latency_ms,group
T001,billing,billing,0.92,0.02,180,consumer
T002,refund,,0.90,0.02,200,business
```

T002 is pending. Required headers are the configured ID, prediction, and outcome columns. Missing ID/prediction makes a row invalid. Duplicate IDs exclude **all** their occurrences from accuracy, preventing an arbitrary first record from becoming the truth. ID values are not included in reports. Record numbers start at 1 after the header and refer to parsed records, not physical CSV lines.

Prediction and outcome labels use exact, case-sensitive string matching after trimming. Distinct IDs should identify attempts, not only business entities. Include incorrect and pending classification outputs rather than selecting correct cases. A no-output failure is not a valid classification record; use separate workflow accounting for those failures. Both current and baseline must follow the same definition. The monitor cannot detect omitted attempts.

Optional confidence is the supplied probability of the chosen prediction being correct, between 0 and 1. Cost and latency must be finite and nonnegative; latency is in milliseconds. Missing or invalid cells in present measurement columns produce findings. Set an optional column role to null to disable it. All costs must use one declared unit/currency; no conversion is performed. Allocate retries and other attributable costs to the defined output cohort upstream. This is not full workflow-attempt accounting.

Optional groups support descriptive breakdowns and case-mix comparison. Category and group names are included in reports and may need anonymization.

## Configuration

A JSON object with known, unique keys and finite numeric values. Partial configurations are accepted. Roles must use distinct column names; names must exactly match trimmed CSV headers.

| Key | Default | Meaning |
| --- | --- | --- |
| `dataset_name` | Local classification results | Report label |
| `id_column` | record_id | Required unique attempt ID |
| `prediction_column` | predicted_label | Required predicted category |
| `outcome_column` | actual_label | Required outcome header; blank values are pending |
| `confidence_column` | confidence | Optional column name, or null |
| `cost_column` | cost | Optional column name, or null |
| `latency_column` | latency_ms | Optional column name, or null |
| `group_column` | group | Optional column name, or null |
| `cost_unit` | EUR | User-declared cost unit; no currency inference |
| `min_evaluated_rows` | 30 | Positive minimum for accuracy, confidence, cost, and baseline verdicts |
| `min_accuracy_pct` | 85 | Minimum accuracy on the selected threshold basis |
| `accuracy_threshold_basis` | point_estimate | point_estimate or wilson_lower_bound (95% interval) |
| `evidence_context` | {} | Optional purpose, population, sampling_method and reference_basis declarations; each string up to 2000 characters or null |
| `min_outcome_coverage_pct` | 90 | Minimum valid completed outcomes / all rows |
| `max_confidence_gap_pp` | 10 | Maximum absolute mean-confidence / paired-accuracy gap |
| `allowed_accuracy_drop_pp` | 10 | Maximum descriptive accuracy drop from baseline |
| `max_case_mix_shift_pct` | 20 | Maximum total variation of supplied group shares |
| `max_cost_per_correct` | null | Optional positive cost target |
| `max_mean_latency_ms` | null | Optional positive mean-latency target |

Percent and percentage-point thresholds are between 0 and 100 inclusive. [Bundled example](../resqmonitor/fixtures/config.json).

## Report contract

`schema_version: 2.0`; `status: ok|attention|unknown`; named `checks` with value, unit, status, message, and evidence. A value may be measured while its verdict is unknown due to insufficient evidence. `summary` gives raw/evaluated/correct/pending/invalid counts and a 95% Wilson interval. `baseline_summary` and `groups` expose comparison evidence. Consumers should tolerate additional fields and use names rather than positional order.

The JSON CLI returns invalid-input/execution errors as `status: error` and `error: {code, message}` on stdout, including when an output path was requested. The optional MCP SDK reports raised invalid-input exceptions through its standard tool-error mechanism.

### Evidence contract 2.0

Each check exposes `value`, `threshold_status`, `evidence_status`, `status`, `threshold` and `reason_codes`. See [field semantics](EVIDENCE_POLICY.md#reading-the-report) and the [normal-report JSON Schema](report.schema.json). The same typed shape is exposed as the optional MCP output schema. Error objects are a separate CLI contract; MCP tool errors are separate from normal reports.

The report adds `decision`, `policy` and `provenance`. Read `decision.required_checks` for overall scope. Context is caller-declared and is not validated against the world. Reports expose supplied policy/context, column and category names; omit identifying details if they are unnecessary.

Migration from 1.0: check names and observed values remain accessible, but verdict rules are stricter. A diagnostic without a configured target no longer silently receives `ok`. Missing evidence stays unknown; insufficient observations can still have a passing numeric threshold comparison. Check schema version explicitly before relying on these meanings.
