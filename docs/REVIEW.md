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

## Verification and remaining decisions

See [verification results](VERIFICATION.json), [the action plan](ACTION_PLAN.json) and [project status](PROJECT_STATUS.md). Automated tests and saved-report replay check the implementation and its declared examples. They cannot establish label truth, representative sampling, model authenticity or deployment suitability.

Licensing, contribution rights, visibility and release remain owner decisions. They are prerequisites for broad reuse, not code defects to resolve by silently assigning a license.
