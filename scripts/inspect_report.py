"""Inspect a report's declared evidence; never authorize a downstream action."""
import argparse
import hashlib
import json
import math
from pathlib import Path
import sys

TOOL = "resqmonitor"
STATUSES = {"ok", "attention", "unknown"}
EVIDENCE = {"sufficient", "insufficient", "missing", "invalid", "not_configured"}


def require(condition, message):
    if not condition:
        raise ValueError(message)


def inspect_report(report):
    """Check structural consistency, not authenticity or the underlying CSV."""
    require(isinstance(report, dict), "Report must be an object")
    require(report.get("schema_version") == "2.0" and report.get("tool") == TOOL,
            "Unsupported report version or tool")
    if report.get("status") == "error":
        return {"assessment": "input_error", "source_verified_by_consumer": False, "action_authorized": False}
    status = report.get("status")
    require(isinstance(status, str) and status in STATUSES, "Missing or invalid status")
    decision = report.get("decision")
    require(isinstance(decision, dict), "Missing decision")
    require(decision.get("scope") == "supplied_observations" and
            decision.get("action_authorized") is False, "Unexpected scope or action authority")
    require(decision.get("outcome") == {"ok": "criteria_met", "attention": "criteria_not_met", "unknown": "undetermined"}[status],
            "Inconsistent aggregate decision")
    required = decision.get("required_checks")
    require(isinstance(required, list) and required and all(isinstance(x, str) for x in required)
            and len(set(required)) == len(required), "Missing or invalid required checks")
    core = {"accuracy", "outcome_coverage"}
    require(core <= set(required), "Core checks are absent from required scope")
    checks = report.get("checks")
    require(isinstance(checks, dict) and set(required) <= set(checks), "Required check is missing")
    for name, item in checks.items():
        require(isinstance(item, dict), f"Invalid check: {name}")
        require(all(isinstance(item.get(key), str) and item[key] in allowed for key, allowed in
                    (("status", STATUSES), ("threshold_status", STATUSES), ("evidence_status", EVIDENCE))),
                f"Missing check verdict fields: {name}")
        require(isinstance(item.get("evidence"), dict) and bool(item["evidence"]), f"Missing evidence: {name}")
        reasons = item.get("reason_codes")
        require(isinstance(reasons, list) and all(isinstance(x, str) for x in reasons), f"Invalid reason codes: {name}")
        value = item.get("value")
        require(value is None or (type(value) in (int, float) and abs(value) <= 1e308 and math.isfinite(value)), f"Invalid value: {name}")
        if item["status"] != "unknown":
            require(item["evidence_status"] == "sufficient" and item["status"] == item["threshold_status"],
                    f"Verdict contradicts evidence: {name}")
        if item["status"] == "ok":
            require(value is not None and not reasons, f"Positive verdict has absent or qualified evidence: {name}")
            threshold = item.get("threshold")
            require(isinstance(threshold, dict) and any(threshold.get(k) is not None for k in ("minimum", "maximum")),
                    f"Positive check has no target: {name}")
        threshold = item.get("threshold")
        require(isinstance(threshold, dict), f"Missing threshold: {name}")
        for key in ("minimum", "maximum", "assessment_value"):
            number = threshold.get(key)
            require(number is None or (type(number) in (int, float) and abs(number) <= 1e308 and math.isfinite(number)), f"Invalid threshold: {name}")
        assessed = threshold.get("assessment_value")
        minimum, maximum = threshold.get("minimum"), threshold.get("maximum")
        # The producer compares unrounded values but displays six decimals.
        # At a displayed boundary either verdict can therefore be consistent.
        if assessed is None or (minimum is None and maximum is None):
            consistent = item["threshold_status"] == "unknown"
        else:
            tolerance = 0.0000005 + math.ulp(assessed)
            if item["threshold_status"] == "ok":
                consistent = ((minimum is None or assessed + tolerance >= minimum) and
                              (maximum is None or assessed - tolerance <= maximum))
            else:
                consistent = item["threshold_status"] == "attention" and (
                    (minimum is not None and assessed - tolerance < minimum) or
                    (maximum is not None and assessed + tolerance > maximum))
        require(consistent, f"Threshold comparison is inconsistent: {name}")
    policy, provenance = report.get("policy"), report.get("provenance")
    require(isinstance(policy, dict) and isinstance(provenance, dict), "Missing policy or provenance")
    encoded = json.dumps(policy, sort_keys=True, separators=(",", ":"), ensure_ascii=False, allow_nan=False)
    require(hashlib.sha256(encoded.encode()).hexdigest() == provenance.get("policy_sha256"), "Policy fingerprint mismatch")
    require(isinstance(provenance.get("input_sha256"), dict) and bool(provenance["input_sha256"]), "Missing input identity")
    require(all(key in provenance for key in ("source_verification", "context_verification", "generalization")), "Missing provenance limits")
    findings = report.get("findings")
    require(isinstance(findings, list), "Missing findings")
    states = [checks[name]["status"] for name in required]
    expected_status = "attention" if findings or "attention" in states else ("unknown" if "unknown" in states else "ok")
    require(status == expected_status, "Aggregate status contradicts required checks or findings")
    return {"assessment": {"ok": "sample_rules_met", "attention": "criteria_not_met", "unknown": "insufficient_evidence"}[status],
            "scope": "supplied_observations", "synthetic": report.get("synthetic"),
            "source_verified_by_consumer": False, "action_authorized": False,
            "required_checks": required}


def _pairs(pairs):
    obj = {}
    for key, value in pairs:
        require(key not in obj, "Duplicate JSON key")
        obj[key] = value
    return obj


def _float(value):
    number = float(value)
    require(math.isfinite(number), "Nonfinite JSON number")
    return number


def _constant(value):
    raise ValueError(f"Nonfinite JSON number: {value}")


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("report", help="JSON file, or - for stdin")
    args = parser.parse_args(argv)
    try:
        if args.report == "-":
            raw = sys.stdin.buffer.read(20_000_001).decode("utf-8")
        else:
            with Path(args.report).open("rb") as stream:
                raw = stream.read(20_000_001).decode("utf-8")
        require(len(raw.encode("utf-8")) <= 20_000_000, "Report exceeds 20 MB")
        report = json.loads(raw, object_pairs_hook=_pairs, parse_float=_float, parse_constant=_constant)
        result = inspect_report(report)
        code = 2 if result["assessment"] == "input_error" else (1 if result["assessment"] != "sample_rules_met" else 0)
    except (ValueError, TypeError, KeyError, OSError, OverflowError, RecursionError) as exc:
        result = {"assessment": "invalid_report", "message": str(exc), "source_verified_by_consumer": False, "action_authorized": False}
        code = 2
    print(json.dumps(result, allow_nan=False))
    return code


if __name__ == "__main__":
    raise SystemExit(main())
