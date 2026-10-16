"""Readable output without external assets, scripts, or network requests."""

from __future__ import annotations

import html
import json
from typing import Any


def as_json(report: dict[str, Any]) -> str:
    return json.dumps(report, indent=2, ensure_ascii=False, allow_nan=False) + "\n"


def as_text(report: dict[str, Any]) -> str:
    lines = [
        f"{report['tool']} | {report['dataset']} | {report['status'].upper()}",
        f"Evaluated at: {report['evaluated_at']}",
        f"Decision: {report['decision']['outcome']} for supplied observations; no action authorized.",
    ]
    if report.get("synthetic"):
        lines.append("SYNTHETIC DEMO: fixed reference time; no real customer data.")
    lines.append("Sample: " + json.dumps(report["summary"], ensure_ascii=False, allow_nan=False))
    lines.append("")
    for item in report["checks"].values():
        value = "unknown" if item["value"] is None else f"{item['value']} {item['unit']}"
        lines.append(f"{item['label']}: {value} [{item['status']}]")
        lines.append(f"  Threshold: {item['threshold_status']}; evidence: {item['evidence_status']}")
        lines.append("  Reasons: " + (", ".join(item["reason_codes"]) or "None under the declared policy"))
        lines.append("  Rule: " + json.dumps(item["threshold"], allow_nan=False))
        lines.append(f"  {item['message']}")
        lines.append("  Evidence: " + json.dumps(item["evidence"], ensure_ascii=False, allow_nan=False))
    if report["findings"]:
        lines.append("\nFindings:")
        lines.extend(f"- {item['code']}: {item['message']}" for item in report["findings"])
    lines.append("\nPolicy and provenance:")
    lines.append(json.dumps({key: report[key] for key in ("policy", "provenance")}, ensure_ascii=False, allow_nan=False))
    lines.append("\nScope:")
    lines.extend(f"- {note}" for note in report["notes"])
    return "\n".join(lines) + "\n"


def as_html(report: dict[str, Any]) -> str:
    escape = lambda value: html.escape(str(value), quote=True)
    cards = []
    for item in report["checks"].values():
        value = "Unknown" if item["value"] is None else f"{item['value']} {item['unit']}"
        evidence = escape(json.dumps(item["evidence"], indent=2, ensure_ascii=False, allow_nan=False))
        cards.append(
            f'<article><h2>{escape(item["label"])}</h2>'
            f'<p class="value">{escape(value)}</p>'
            f'<p class="badge {escape(item["status"])}">{escape(item["status"].upper())}</p>'
            f'<p>Threshold: <strong>{escape(item["threshold_status"])}</strong> · '
            f'Evidence: <strong>{escape(item["evidence_status"])}</strong></p>'
            f'<p>{escape(", ".join(item["reason_codes"]) or "No evidence issues under the declared policy")}</p>'
            f'<p>{escape(item["message"])}</p>'
            f'<p>Rule: {escape(json.dumps(item["threshold"], allow_nan=False))}</p>'
            f'<details><summary>Calculation evidence</summary><pre>{evidence}</pre></details></article>'
        )
    findings = "".join(
        f'<li><strong>{escape(item["code"])}</strong>: {escape(item["message"])}</li>'
        for item in report["findings"]
    ) or "<li>No threshold findings. Check unknown measurements before drawing conclusions.</li>"
    notes = "".join(f"<li>{escape(note)}</li>" for note in report["notes"])
    synthetic = '<p class="demo">Synthetic demonstration · fixed reference time</p>' if report.get("synthetic") else ""
    title = escape(f"{report['tool']} — {report['dataset']}")
    summary = escape(json.dumps(report["summary"], ensure_ascii=False))
    metadata = escape(json.dumps({key: report[key] for key in ("policy", "provenance")}, indent=2, ensure_ascii=False))
    return f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>{title}</title><style>
body{{font:16px/1.6 system-ui,sans-serif;color:#172b43;background:#f3f6fa;margin:0}}
main{{max-width:1100px;margin:auto;padding:32px 20px}}h1{{line-height:1.2;margin-bottom:8px}}
h2{{font-size:1.1rem;margin:0}}.grid{{display:grid;grid-template-columns:repeat(auto-fit,minmax(270px,1fr));gap:16px}}
article,section{{background:white;border:1px solid #ccd6e3;border-radius:12px;padding:20px;margin-top:20px}}
.value{{font-size:2rem;font-weight:700;margin:12px 0}}.badge{{display:inline-block;padding:3px 10px;border-radius:6px;font-weight:700}}
.ok{{background:#d7f1df;color:#174c2d}}.attention{{background:#fff0c9;color:#614100}}.unknown{{background:#e7edf5;color:#35455e}}
.demo{{font-weight:600;color:#5a3a00}}pre{{white-space:pre-wrap;overflow-wrap:anywhere;font-size:.85rem}}
summary{{cursor:pointer;text-decoration:underline}}footer{{margin-top:24px;color:#425570}}@media print{{body{{background:white}}article{{break-inside:avoid}}}}
</style></head><body><main><header><h1>{title}</h1>
<p>Overall status: <strong>{escape(report["status"].upper())}</strong> · {escape(report["evaluated_at"])}</p>
<p>{escape(report["decision"]["outcome"])} for supplied observations. No action authorized.</p>
{synthetic}<p>{summary}</p></header><div class="grid">{''.join(cards)}</div>
<section><h2>Findings</h2><ul>{findings}</ul></section>
<section><h2>Policy and provenance</h2><details><summary>Declared rules and input fingerprints</summary><pre>{metadata}</pre></details></section>
<section><h2>What this report establishes</h2><ul>{notes}</ul></section>
<footer>Local calculations. No model calls, telemetry, or external page assets.</footer>
</main></body></html>
"""
