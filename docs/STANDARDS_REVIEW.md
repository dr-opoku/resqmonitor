# Standards and practice review

Reviewed **13 October 2026**. Recent-development window: **29 July–13 October 2026** (about 2.5 months). This is a targeted review of primary sources, not an exhaustive survey or a conformance certification.

## Dated developments inside the window

| Date | Primary source and maturity | Relevance to this showcase |
| --- | --- | --- |
| 7 August 2026 | [NIST TEVV-Athlon, AI 200-2 initial public draft](https://www.nist.gov/artificial-intelligence/ai-research/tevv-athlon-framework-evaluating-ai-systems); comment period closed 6 October | Adapt assessments to organizational objectives. This is a draft framework, not a finalized requirement or a prescribed minimum sample. |
| 22 August 2026 | [MCP roadmap](https://modelcontextprotocol.io/development/roadmap); priorities, not release commitments | Work on consistent result semantics, agent identity and delegated authority reinforces the need to distinguish reporting from permission to act. |
| 26 August 2026 | [AWS framework-independent AgentCore evaluation example](https://aws.amazon.com/blogs/machine-learning/evaluate-any-agent-framework-with-amazon-bedrock-agentcore-evaluations/); vendor implementation guidance | Uses trace/span telemetry for evaluations across agent frameworks. It is practical adoption evidence, not a universal evaluation standard or an adoption-rate estimate. |
| 2 October 2026 | [Official MCP Python SDK v2.3.0](https://github.com/modelcontextprotocol/python-sdk/releases/tag/v2.3.0); SDK release | The optional adapter's declared SDK range starts at this release. Its typed return contract exposes an output schema. |

## Existing foundations and work still evolving

- [MCP tools specification, 28 July 2026](https://modelcontextprotocol.io/specification/2026-07-28/server/tools) is one day **before** the review window. Structured results must conform when an output schema is declared; tool execution errors are distinct from normal results. Annotations are hints whose trust depends on the server. Structured output is an existing mechanism, not an August–October invention. See also the [SDK structured-output documentation](https://py.sdk.modelcontextprotocol.io/servers/structured-output/).
- [W3C Data Quality Vocabulary](https://www.w3.org/TR/vocab-dqv/) is an older **Working Group Note**, not a new Recommendation. It separates quality measurements, policies and provenance, and leaves fitness for purpose to the consumer. This report follows that conceptual separation; it does not emit RDF/DQV.
- [NIST statistical guidance on confidence intervals](https://www.itl.nist.gov/div898/handbook/prc/section2/prc241.htm) predates the window. Intervals and their assumptions are established practice. The Wilson interval in Result Quality Monitor is not a new agent-specific technique.
- [OpenTelemetry GenAI conventions](https://github.com/open-telemetry/semantic-conventions-genai) are actively evolving. At review time the repository's schema URL was `TODO`, the changelog contained an `Unreleased` section, and its GitHub releases list was empty. This is not evidence of a newly stable, universal GenAI evaluation contract. No telemetry is emitted here.

## Implementation judgment

**Our inference:** agent recipients benefit from the same evidence discipline as people, with explicit machine-readable scope, rules, unknown states and reason codes. The sources above do not establish a universal "evidence strength" score, universally safe sample count, or permission for an agent to act on a green result.

The implementation therefore provides:

1. Observed value, threshold comparison and evidence adequacy as separate fields.
2. Declared context, the complete effective policy, evaluation time and input/policy fingerprints.
3. A bounded decision over named checks; source authenticity, reference validity and generalization remain unverified.
4. The same meanings in text, HTML, JSON and the optional typed MCP output.

A production host could associate this report with a trace and use its own authority and escalation rules. Tracing, identity, delegation, provenance authentication, outcome-label governance and domain validation are outside this example. Licensing was not assessed or changed in this review.
