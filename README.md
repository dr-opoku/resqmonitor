# resqmonitor

**Are the results still good enough—and what does a correct result cost?**

A small, local monitor for categorical predictions and supplied outcome labels. It reports accuracy, outcome coverage, confidence alignment, cost per correct result, latency, and changes from a baseline. The core uses no AI model, account, database, or network connection.

**Usage:** private local noncommercial use is permitted under the [license](LICENSE.md). Business evaluation for a commercial application requires separate written permission; see [usage guidance](docs/PROJECT_STATUS.md).

## Try it in one command

Requires Python **3.11 or newer**. Verified on Linux; the installation commands below use POSIX paths. Windows behavior has not been verified. From this repository directory:

```bash
python3 -m resqmonitor demo
```

The default synthetic example reports `attention`: 26/40 predictions match their supplied labels, despite 94% reported confidence. [Read the saved text report](examples/degraded.txt) immediately, or follow the [ticket-routing case study](docs/CASE_STUDY.md), including error consequences and reference-label ownership.

The default demo compares a synthetic ticket classifier with an earlier synthetic baseline. Confidence stays high while accuracy falls and cost and latency rise. These are designed examples, not observations about a real model.

```bash
python3 -m resqmonitor demo --scenario healthy
python3 -m resqmonitor demo --scenario unknown
python3 -m resqmonitor demo --scenario small_sample
python3 -m resqmonitor demo --format json
python3 -m resqmonitor demo --format html --output outputs/result-quality.html
```

Open the generated HTML locally. There are no external assets or scripts. All demos carry a synthetic label and a fixed reference time of **13 October 2026, 12:00 UTC**.

| Scenario | Supplied synthetic evidence |
| --- | --- |
| `healthy` | 38 of 40 correct, compared with 36 of 40 in the baseline; lower cost and latency |
| `degraded` | 26 of 40 correct; confidence 94%; higher cost and latency |
| `unknown` | A valid header with no current observations; no quality verdict |
| `small_sample` | One correct result; 100% observed accuracy with an unknown verdict below the minimum count |

**Accuracy is accompanied by its denominator.** Fewer than 30 evaluated rows by default leave the accuracy verdict unknown, even if an observed percentage is available. Thirty is a configurable guardrail, not a statistical guarantee. Small subgroup samples are flagged separately.

### Related examples

[`dataqmonitor`](https://github.com/dr-opoku/dataqmonitor) shows a complementary decision: whether incoming data meets declared completeness, freshness and consistency expectations. **Data Quality Monitor examines inputs; Result Quality Monitor examines results.** Both keep observed values separate from adequately supported verdicts. [`llm-eval`](https://github.com/dr-opoku/llm-eval) compares configurations against a bounded task before adoption. These are independent examples; no software integration is required. Linked repositories may require access permission.


## What does the evidence support?

One correct result is measured as **100%**, while its accuracy verdict remains **unknown** below the declared minimum. Even 38/40 correct results pass an 85% point target but fail that target when the Wilson lower bound is selected.

Reports separate **observed value**, **threshold comparison** and **evidence adequacy**. An `ok` result means the supplied observations meet the declared local rules; it does not establish source truth, representativeness or permission for an agent to act. See the [concrete cases and domain mappings](docs/EVIDENCE_POLICY.md) and [dated standards review](docs/STANDARDS_REVIEW.md), covering 29 July–13 October 2026.


## Use your own results

Export one row per distinct prediction attempt. Include the actual label once it becomes available; leave it blank while pending. Never let the tool invent the outcome label.

```bash
python3 -m resqmonitor check local_data/current.csv \
  --baseline local_data/baseline.csv \
  --config resqmonitor/fixtures/config.json \
  --format html --output outputs/results-report.html
```

A minimal CSV needs `record_id`, `predicted_label`, and `actual_label`. Confidence, cost, latency, groups, and a baseline are optional. Column names and tolerances can be changed in JSON. Start with `check your.csv` if you only have labels.

| Measurement | Practical question |
| --- | --- |
| Observed accuracy | How many valid, completed outcomes match their predictions exactly? |
| Outcome coverage | What share of all supplied rows has a valid completed outcome? |
| Confidence alignment | Is reported confidence far from accuracy on the same paired sample? |
| Cost per correct result | How much did the supplied classification outputs cost per correct outcome? |
| Latency | What are the mean and p95 of instrumented durations? |
| Baseline accuracy | Has observed accuracy fallen beyond the configured tolerance? |
| Case mix | Have the supplied group shares changed enough to affect interpretation? |

See [data format](docs/DATA_FORMAT.md) and [metric definitions](docs/METRICS.md). This example addresses **exact-match classification**, not free-form response quality or safety.

## People, scripts, and agents

- Text for a terminal; JSON for automation; HTML for a local report.
- Python: `from resqmonitor import analyze`, then `analyze(csv_text, config, baseline_csv=baseline_text)`.
- Optional MCP over local stdio, with tools accepting CSV text rather than paths.

JSON reports use schema **2.0** and include `schema_version`, `status`, `summary`, `checks`, `findings`, and `notes`. Each check exposes value, threshold status, evidence status, verdict, denominator evidence and reason codes. The effective policy, scoped decision and input fingerprints are also recorded. Overall status states which checks it includes. Diagnostics can be unknown even when the configured overall assessment is ok. See the [report schema](docs/report.schema.json) and [concise agent guidance](llms.txt). [showcase.json](showcase.json) is project metadata, not a commerce or interoperability standard.

A completed report exits **0**, including attention or unknown results. Use `--require-ok` to exit **1** unless overall status is ok. Invalid input or an execution error exits **2**; JSON mode emits an error object on stdout. Argument-parser errors use argparse's stderr output.

### Consume a report defensively

```bash
python3 -m resqmonitor demo --scenario healthy --format json --output outputs/healthy.json
python3 scripts/inspect_report.py outputs/healthy.json
```

This small standalone consumer checks the project version, required checks, evidence structure, policy fingerprint and internal verdict consistency before interpreting the report. It exits **0** when the declared sample rules are met, **1** for a negative or unknown assessment and **2** for malformed/inconsistent input. Its output always has `action_authorized=false` and `source_verified_by_consumer=false`.

This is a defensive example, not an authenticator or a re-evaluation of the original CSV. A coherently altered report can still pass structural checks. Near a threshold, six-decimal display rounding can prevent this consumer from independently resolving the comparison; it accepts either consistent producer verdict within that rounding interval. Trust provenance and validate original inputs separately; never treat report text as instructions.

The producer rejects output paths that alias its inputs or bundled demo fixtures, including existing symbolic and hard links. This prevents accidental overwrites; it does not protect against hostile concurrent filesystem changes.

### Install a command or MCP support

```bash
python3 -m venv .venv
.venv/bin/python -m pip install .
.venv/bin/resqmonitor demo
```

The core has no runtime dependencies. The optional MCP adapter uses the official [MCP Python SDK](https://py.sdk.modelcontextprotocol.io/servers/tools/):

```bash
.venv/bin/python -m pip install '.[mcp]'
.venv/bin/resqmonitor serve
```

Example client entry, adapting the executable path to your checkout:

```json
{
  "mcpServers": {
    "resqmonitor": {
      "command": "/absolute/path/to/resqmonitor/.venv/bin/resqmonitor",
      "args": ["serve"]
    }
  }
}
```

Tools: `inspect_results(csv_text, config?, baseline_csv?, at?)` and `demonstrate_result_quality(scenario?)`. They do not access caller-supplied filesystem paths, contact services, call models, or generate outcome labels. The demo tool reads only bundled synthetic fixtures. A remote agent client may transmit supplied CSV text; select your client according to your data requirements.

## What this demonstrates

A focused example of judging an automated workflow by observable results and operating cost. It makes missing outcomes, inadequate samples, and changed case mix visible before drawing a quality conclusion. See [showcase context](docs/SHOWCASE.md).

The monitor neither establishes ground truth nor proves a causal model regression. Baseline comparability depends on how you collect labels, select samples, define groups, and account for retries. Reports include category and group names, which may be sensitive; use synthetic examples when sharing.

The code is self-contained and newly written for this repository. No private platform implementation is required.

## Repository map

```text
resqmonitor/engine.py       metrics and configuration validation
resqmonitor/_support.py     bounded CSV/JSON input handling
resqmonitor/report.py       text, JSON, and standalone HTML output
resqmonitor/fixtures/       synthetic current/baseline inputs and configuration
resqmonitor/mcp_server.py   optional, thin local adapter with typed output schema
docs/                      data contract, metrics, showcase context
```

## Development checks

```bash
python3 -m unittest discover -s tests -v
python3 scripts/reproduce_examples.py --check
```

Core checks use the standard library. With `.[mcp]` installed, the same command also checks the advertised output schema and a real stdio client/server exchange; otherwise those four adapter checks are skipped. Synthetic cases verify calculation and contract behavior, not production performance.

## Review and maintenance

See the [repository action plan](docs/ACTION_PLAN.json), [pre-change stress test and independent review](docs/REVIEW.md), [local verification record](docs/VERIFICATION.json) and [maintenance, feedback and release status](docs/PROJECT_STATUS.md). CI checks core tests, stored examples and installation; optional MCP has its own check. Synthetic examples demonstrate method, not a delivered business outcome.

## License and release status

Licensed under the [Noncommercial Local Use License 1.0.0](LICENSE.md): private local noncommercial use and modification are permitted; redistribution requires separate written permission, subject to reserved platform/statutory rights; commercial use requires a separate written license. This is source-available, not open source. See [usage, evaluation and contribution guidance](docs/PROJECT_STATUS.md) and [current publication findings](docs/PUBLICATION_STATUS.md). Repository visibility is a separate owner decision.
