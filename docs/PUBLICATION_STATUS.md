# Publication follow-up — 19 October 2026

## Latest disclosure preparation

The subsequent [disclosure review](DISCLOSURE_REVIEW.md) covers Git history,
Actions logs, GitHub text surfaces and completed branch cleanup. It preserves
the evidence chain and records the remaining publication/deployment boundaries.
The dated findings below retain their original implementation-review scope.

## Scope and current status

This follow-up records corrections to resqmonitor's overall-status explanation, optional MCP dependency declaration, terminal display handling and current license status. It follows a read-only publication audit and an independent Claude Code review requested with `claude-fable-5-1`. The actual review completed without a fallback selector and included its ending. This records the adapter's selector, not independent attestation of the model provider or backend. The external reviewer assessed supplied material; implementing-agent checks are recorded separately. No model was called by regression tests.

The owner-selected [Noncommercial Local Use License 1.1.0](../LICENSE.md) is included. Version 1.1.0 adds the owner-approved completed report exception to version 1.0.0; the noncommercial qualifier explicitly applies to copying, display and distribution, not just report presentation. README, agent guidance, project metadata and package metadata identify the same license. This resolves the missing-file and inconsistent current-status findings. It does not establish legal enforceability, production fitness or permission to publish the repository. Earlier dated review/test records retain their historical scope; see the dated follow-up in [verification](VERIFICATION.json).

## Rights, presentation and remaining decisions

- **Generated reports — resolved:** section 3 permits noncommercial copying, display and distribution of lawfully generated completed reports, including embedded HTML/CSS, labels and explanatory text. Recipients may further display/share on the same terms. Preserve included notices and identify changes to findings. Template/component extraction and software redistribution are not permitted by this exception; third-party rights remain unaffected. Check confidentiality and data rights before sharing.
- **Business evaluation:** the present license treats evaluation preparing a commercial application as commercial use. A company cannot infer free execution rights from a runnable demo. A limited evaluation exception would require an explicit additional grant; none is implied here.
- **Contributions:** private qualifying local modifications are permitted. Public modified copies and patches containing protected repository material need permission beyond the reserved platform/statutory rights. Contribution workflow and any commercial relicensing permission should be agreed before accepting code. Issue reports with synthetic reproductions are welcome.
- **Commercial delivery:** no published price, checkout or automated license fulfillment exists. An inquiry or payment alone does not grant rights. The repository is source-available, not open source.

## Repository-specific findings

### Corrected

- The HTML description now says local review, rather than implying an unrestricted right to share generated reports.

### Corrected in the integration follow-up

- The generated note now states that overall status combines required checks and recorded findings. An absent optional cost column remains allowed; an invalid value in a supplied cost column produces a finding and can yield `attention` even when all required checks pass. All four saved synthetic scenarios were regenerated in JSON, text and HTML; metric values, status rules and fingerprints are unchanged.
- The optional MCP extra directly declares `typing_extensions>=4.13`, matching the direct import. The offline core still has no runtime dependencies.
- Human-readable text reports and handled CLI error messages visibly escape terminal controls, including ESC, carriage return, C1 controls and bidirectional formatting controls. JSON retains original strings; HTML retains separate escaping. Newlines/tabs remain for layout; this is display hygiene, not an authenticated log. Argument-parser diagnostics and separately invoked consumers are outside this helper's scope.

Focused regressions reproduced the incomplete status note and unsafe terminal rendering before correction. See the integration entry in [verification](VERIFICATION.json).

Authored outcome labels are supplied evidence, not independently adjudicated truth. The classifier example does not assess free-form answer quality, safety or enterprise deployment readiness.
