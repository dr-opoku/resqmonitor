# Publication follow-up — 19 October 2026

## Scope and current status

This follow-up addresses the owner's request to correct the llm-eval decoder failure and remove obsolete license-pending statements. It follows a read-only publication audit and an independent Claude Code review requested with `claude-fable-5-1`. The actual review completed without a fallback selector and included its ending. This records the adapter's selector, not independent attestation of the model provider or backend. The external reviewer assessed supplied material; implementing-agent checks are recorded separately. No model was called by regression tests.

The owner-selected [Noncommercial Local Use License 1.0.0](../LICENSE.md) is now included unchanged. README, agent guidance, project metadata and package metadata identify the same license. This resolves the missing-file and inconsistent current-status findings. It does not establish legal enforceability, production fitness or permission to publish the repository. Earlier dated review/test records retain their historical scope; see the dated follow-up in [verification](VERIFICATION.json).

## Remaining rights and presentation decisions

- **Generated reports:** HTML templates, styles and software-authored explanatory text are embedded in reports. The current output clause does not expressly permit sharing protected embedded material. A narrowly scoped report-output exception could resolve this without licensing redistribution of the tool; it has not been adopted.
- **Business evaluation:** the present license treats evaluation preparing a commercial application as commercial use. A company cannot infer free execution rights from a runnable demo. A limited evaluation exception would require an explicit additional grant; none is implied here.
- **Contributions:** private qualifying local modifications are permitted. Public modified copies and patches containing protected repository material need permission beyond the reserved platform/statutory rights. Contribution workflow and any commercial relicensing permission should be agreed before accepting code. Issue reports with synthetic reproductions are welcome.
- **Commercial delivery:** no published price, checkout or automated license fulfillment exists. An inquiry or payment alone does not grant rights. The repository is source-available, not open source.

## Repository-specific findings

### Corrected

- The HTML description now says local review, rather than implying an unrestricted right to share generated reports.

### Still present; presentation inconsistency

The report note "Overall status covers: ... Other diagnostics remain separately visible" is incomplete: findings can also change the overall status, even when the configured required checks pass. For example, an absent optional cost column is allowed; an invalid value in a supplied cost column creates a finding and can yield `attention`. [Evidence policy](EVIDENCE_POLICY.md) describes this behavior. The note should explicitly say "required checks plus findings" in a separate change that also regenerates saved reports. No metric or status rule was changed in this follow-up.

### Still present; bounded improvements

- Optional MCP code imports `typing_extensions` directly, while the extra currently relies on the MCP SDK to supply it transitively.
- Terminal output includes caller-supplied labels without control-character sanitization.

Authored outcome labels are supplied evidence, not independently adjudicated truth. The classifier example does not assess free-form answer quality, safety or enterprise deployment readiness.
