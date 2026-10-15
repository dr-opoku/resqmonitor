# Showcase stress review — 15 October 2026

## Purpose and sequence

Improve visible usefulness, first-run clarity, evidence discipline and professional reference value. The existing source was inspected, baseline tests and adversarial probes were recorded, and the proposed plan was externally reviewed **before repository changes**. The baseline commit was `68e547ff04b30dd405bd26b8b9e99e6f5af395dc`.

One AGY review per repository was requested with **`gemini-3.8-flash-high`**, the adapter's Gemini 3.8 Flash (High) selector. The three repositories were mounted read-only for the reviewer. File hashes remained unchanged at the pre-edit gate. This records the requested selector; backend model identity was not independently attested.

The reviewer assessed a curated plan/source packet, not every helper or fixture, and did not execute tests. Its recommendations were checked against actual code. This was not a second comprehensive security audit, a market validation or a CV verification. Full local review records are kept outside the repositories; the implementation decisions follow below.

## Accepted findings and repairs

- Protect input/config/baseline files from output collisions, including symbolic and hard links.
- Describe confusion counts as external case analysis; core measures exact categorical label agreement, not asymmetric financial loss.
- Provide defensive consumer, authored-label provenance, cost scope and reproducible case.

## Findings bounded or rejected after source inspection

- No naming ban on llm-eval; clarify the scope of the naming instruction.
- No reason-code deduplication repair: _support.check already deduplicates.
- No new confusion matrix or financial-loss engine: a documented external fixture analysis suffices.
- Keep descriptive rounding and existing unrounded threshold assessment.
- Do not treat a wholly missing cost series as known zero or claim workflow costs absent from supplied records.

## International examples informing presentation

- [Oracle](https://github.com/steipete/oracle): make the first useful command and a local preview legible.
- [Evidently](https://github.com/evidentlyai/evidently): connect a small example with inspectable reports and tests.
- [Promptfoo](https://github.com/promptfoo/promptfoo): keep configurations, evaluation and repeatable checks visible.
- [AGENTS.md](https://agents.md/): provide concise repository instructions for coding agents.

These references informed the entry point, examples and verification. They do not establish a universal showcase standard, explain why a specific repository receives stars or prove demand for this code.

## Professional relevance

The reference can support a conversation about specifying a decision, defining evidence, coordinating correction/acceptance and making limits inspectable by technical and business stakeholders. It does not establish enterprise rollout experience, organizational adoption, savings or proprietary platform capability. Those claims need separate project evidence. No private platform implementation is required or included.

## Additional local regression finding

The report producer compares unrounded measurements and displays six decimals. The example consumer therefore permits either consistent verdict within the display-rounding interval at a threshold. Tests cover these boundaries and reject clearly inconsistent comparisons. The consumer cannot independently recompute an exact comparison from rounded display values.

## Python-version regression found by GitHub CI

The first Python 3.11 CI replay exposed different floating-point aggregates from Python 3.12. A focused regression test reproduced the failure before the repair. Explicit `math.fsum` accumulation now reproduces the stored examples on both locally available versions. Original responses, frozen requirements and sample eligibility outcomes were preserved. An unrepresentable total cost remains null, as before.

## Verification and remaining decisions

See [verification results](VERIFICATION.json), [the action plan](ACTION_PLAN.json) and [project status](PROJECT_STATUS.md). Automated tests and saved-report replay check the implementation and its declared examples. They cannot establish label truth, representative sampling, model authenticity or deployment suitability.

Licensing, contribution rights, visibility and release remain owner decisions. They are prerequisites for broad reuse, not code defects to resolve by silently assigning a license.

## Second pre-edit review — 15 October 2026

Before this round of repository edits, baseline tests passed and tracked-file hashes matched the stated baseline commit. Two complete static reviews were obtained: **G = AGY `gemini-3.8-flash-high`**, **C = Claude Code `claude-sonnet-5-5`**. These are requested selectors, not independent backend attestations. Claude received source and tests; AGY omitted test source and saved example JSON to fit its interface. Neither reviewer executed tests. An initial AGY CLI invocation failed before model execution; its corrected invocation completed. Neither final review was truncated.

Local runtime counterexamples were recorded before repairs. Model findings are suggestions checked against actual behavior, not automatically accepted evidence. X denotes a finding transferred from the sibling review and reproduced here. The earlier sections above remain historical.

| ID | Reviewer finding | Decision | Source check and reason | Verification |
| --- | --- | --- | --- | --- |
| C1 | Low: tiny costs lose precision in text/HTML. | Accepted | Reproduced 0.021053 displayed as 0.02, and 0.0504 above a 0.05 maximum displayed as 0.05. Preserve the serialized value; keep unrounded comparisons. | `tests/test_review_regressions.py` |
| C2 / G1 | Low / medium: missing cost observations reported as known zero. | Accepted | Reproduced absent column, missing cell and empty cohort. Emit null when no valid cost exists; retain measured zero. No observations yields missing evidence; partial totals remain partial. | `tests/test_review_regressions.py` |
| C3 | Low: deeply nested config may raise an unhandled RecursionError. | Accepted after local reproduction | 100,000 nested levels reproduced before edits; rethrow decoder RecursionError as ValueError so CLI returns structured exit 2. | `tests/test_review_regressions.py` |
| C4 | Low: review findings lack individual adjudication. | Accepted / bounded | Append individual decisions for this round; keep prior record intact rather than rewriting historical decisions. | `docs/REVIEW.md` |
| C5 / G2 | Info / low: constant consumer branch for sibling tool. | Accepted | Remove unreachable branch; retain only accuracy and outcome_coverage as mandatory core. | `tests/test_stress.py` |
| G3 | Low: omitted confusion cells not explicitly zero. | Accepted | Name the three omitted pairings as zero in both cohorts. Existing fixture-count tests verify complete nonzero cells and sums of 40. | `tests/test_case_study.py` |
| G4 | Low: fixture alias protection may not support direct zip import. | Bounded; no feature added | Support checkout and normal pip-installed wheel files, both exercised. Direct execution inside a zip archive is not a supported distribution path; no demonstrated overwrite on supported paths. | `Packaging verification; resqmonitor/__main__.py` |
| G5 | Low: evidence precedence absent from generated schema descriptions. | Bounded; no schema edit | EVIDENCE_POLICY already documents precedence; schema enums define possible values. Keep generated MCP/JSON schema equality rather than hand-editing a generated copy. | `docs/EVIDENCE_POLICY.md; tests/test_mcp.py` |

Full prompts, responses, failed invocations and pre-edit hashes are retained in the private audit workspace; this table contains the public decision trail without host details. See [the current action plan](ACTION_PLAN.json) and [verification](VERIFICATION.json). Review and tests establish bounded example behavior, not independent data truth, enterprise outcomes or license rights.
