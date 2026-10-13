"""Compare predictions with outcomes using explicit, bounded evidence."""

from __future__ import annotations

import math
from collections import Counter
from datetime import datetime
from typing import Any

from ._support import check, finite_number, numeric_cell, overall, read_csv, reference_time

DEFAULTS: dict[str, Any] = {
    "dataset_name": "Local classification results",
    "id_column": "record_id",
    "prediction_column": "predicted_label",
    "outcome_column": "actual_label",
    "confidence_column": "confidence",
    "cost_column": "cost",
    "latency_column": "latency_ms",
    "group_column": "group",
    "cost_unit": "EUR",
    "min_evaluated_rows": 30,
    "min_accuracy_pct": 85,
    "min_outcome_coverage_pct": 90,
    "max_confidence_gap_pp": 10,
    "allowed_accuracy_drop_pp": 10,
    "max_case_mix_shift_pct": 20,
    "max_cost_per_correct": None,
    "max_mean_latency_ms": None,
}


def configuration(supplied: dict[str, Any] | None) -> dict[str, Any]:
    supplied = {} if supplied is None else supplied
    if not isinstance(supplied, dict):
        raise ValueError("Configuration must be an object.")
    extra = set(supplied) - set(DEFAULTS)
    if extra:
        raise ValueError(f"Unknown configuration keys: {', '.join(sorted(extra))}")
    cfg = {**DEFAULTS, **supplied}
    required_names = ("dataset_name", "id_column", "prediction_column", "outcome_column", "cost_unit")
    for name in required_names:
        if not isinstance(cfg[name], str) or not cfg[name].strip():
            raise ValueError(f"{name} must be a nonempty string.")
    for name in ("confidence_column", "cost_column", "latency_column", "group_column"):
        if cfg[name] is not None and (not isinstance(cfg[name], str) or not cfg[name].strip()):
            raise ValueError(f"{name} must be a nonempty string, or null.")
    columns = [cfg[name] for name in (
        "id_column", "prediction_column", "outcome_column", "confidence_column",
        "cost_column", "latency_column", "group_column",
    ) if cfg[name] is not None]
    if len(columns) != len(set(columns)):
        raise ValueError("Each configured role must use a distinct column.")
    minimum = cfg["min_evaluated_rows"]
    if isinstance(minimum, bool) or not isinstance(minimum, int) or minimum < 1:
        raise ValueError("min_evaluated_rows must be a positive integer.")
    for name in (
        "min_accuracy_pct", "min_outcome_coverage_pct", "max_confidence_gap_pp",
        "allowed_accuracy_drop_pp", "max_case_mix_shift_pct",
    ):
        if finite_number(cfg[name], name, 0) > 100:
            raise ValueError(f"{name} must be between 0 and 100.")
    for name in ("max_cost_per_correct", "max_mean_latency_ms"):
        if cfg[name] is not None and finite_number(cfg[name], name, 0) == 0:
            raise ValueError(f"{name} must be positive, or null.")
    return cfg


def wilson_interval(correct: int, total: int) -> list[float] | None:
    """95% Wilson interval, conditional on an independent binomial sample."""
    if not total:
        return None
    z = 1.959963984540054
    rate = correct / total
    denominator = 1 + z * z / total
    center = (rate + z * z / (2 * total)) / denominator
    margin = z * math.sqrt(rate * (1 - rate) / total + z * z / (4 * total * total)) / denominator
    return [round(100 * max(0, center - margin), 6), round(100 * min(1, center + margin), 6)]


def _sample(csv_text: str, cfg: dict[str, Any], label: str) -> dict[str, Any]:
    header, rows = read_csv(csv_text)
    mandatory = {cfg[name] for name in ("id_column", "prediction_column", "outcome_column")}
    missing = sorted(mandatory - set(header))
    if missing:
        raise ValueError(f"{label} CSV is missing required columns: {', '.join(missing)}")
    ids = Counter(row[cfg["id_column"]] for row in rows if row[cfg["id_column"]])
    duplicate = {index for index, row in enumerate(rows) if ids[row[cfg["id_column"]]] > 1}
    invalid = {index for index, row in enumerate(rows)
               if not row[cfg["id_column"]] or not row[cfg["prediction_column"]]} | duplicate
    pending = {index for index, row in enumerate(rows)
               if index not in invalid and not row[cfg["outcome_column"]]}
    evaluated = [index for index in range(len(rows)) if index not in invalid | pending]
    correct = [index for index in evaluated
               if rows[index][cfg["prediction_column"]] == rows[index][cfg["outcome_column"]]]
    labels = {row[column] for row in rows for column in (
        cfg["prediction_column"], cfg["outcome_column"],
    ) if row[column]}
    if len(labels) > 100:
        raise ValueError(f"{label} CSV exceeds the 100-label limit.")
    group_column = cfg["group_column"]
    if group_column and group_column in header:
        groups = {row[group_column] for row in rows if row[group_column]}
        if len(groups) > 100:
            raise ValueError(f"{label} CSV exceeds the 100-group limit.")
    accuracy = 100 * len(correct) / len(evaluated) if evaluated else None
    coverage = 100 * len(evaluated) / len(rows) if rows else None
    return {
        "header": header, "rows": rows, "evaluated_indices": evaluated,
        "correct_indices": set(correct),
        "summary": {
            "rows": len(rows), "evaluated_rows": len(evaluated), "correct_rows": len(correct),
            "pending_rows": len(pending), "invalid_rows": len(invalid),
            "duplicate_id_rows": len(duplicate), "accuracy_pct": accuracy,
            "outcome_coverage_pct": coverage,
            "accuracy_wilson_95_pct": wilson_interval(len(correct), len(evaluated)),
        },
        "invalid_record_numbers": [index + 1 for index in sorted(invalid)[:10]],
    }


def _measurement(sample: dict[str, Any], column: str | None, maximum: float | None = None
                 ) -> tuple[dict[int, float], list[int]]:
    if column is None or column not in sample["header"]:
        return {}, []
    values: dict[int, float] = {}
    invalid: list[int] = []
    for index, row in enumerate(sample["rows"]):
        value = numeric_cell(row[column])
        if value is None or value < 0 or (maximum is not None and value > maximum):
            invalid.append(index + 1)
        else:
            values[index] = value
    return values, invalid


def _groups(sample: dict[str, Any], cfg: dict[str, Any]) -> dict[str, Any]:
    column = cfg["group_column"]
    if column is None or column not in sample["header"]:
        return {"observed": False, "missing_group_rows": len(sample["rows"]), "groups": []}
    rows = sample["rows"]
    assigned = Counter(row[column] for row in rows if row[column])
    evaluated = Counter(rows[index][column] for index in sample["evaluated_indices"] if rows[index][column])
    correct = Counter(rows[index][column] for index in sample["correct_indices"] if rows[index][column])
    return {
        "observed": True, "missing_group_rows": sum(not row[column] for row in rows),
        "groups": [{
            "group": group, "rows": assigned[group], "evaluated_rows": evaluated[group],
            "correct_rows": correct[group],
            "accuracy_pct": round(100 * correct[group] / evaluated[group], 6) if evaluated[group] else None,
            "enough_evidence": evaluated[group] >= cfg["min_evaluated_rows"],
        } for group in sorted(assigned)],
    }


def analyze(csv_text: str, config: dict[str, Any] | None = None, *,
            baseline_csv: str | None = None, at: str | datetime | None = None) -> dict[str, Any]:
    """Analyze categorical predictions. Ground-truth labels must be supplied by the caller."""
    cfg = configuration(config)
    current = _sample(csv_text, cfg, "Current")
    summary = current["summary"]
    rows = current["rows"]
    total = summary["rows"]
    evaluated = summary["evaluated_rows"]
    correct = summary["correct_rows"]
    enough = evaluated >= cfg["min_evaluated_rows"]
    findings: list[dict[str, Any]] = []
    if summary["invalid_rows"]:
        findings.append({
            "code": "INVALID_RESULT_ROWS", "count": summary["invalid_rows"],
            "sample_record_numbers": current["invalid_record_numbers"],
            "message": "Missing IDs/predictions and every occurrence of duplicate IDs are excluded from accuracy.",
        })
    checks: dict[str, dict[str, Any]] = {}
    checks["accuracy"] = check(
        "Observed accuracy", summary["accuracy_pct"], "%",
        {"correct_rows": correct, "evaluated_rows": evaluated,
         "minimum_evaluated_rows": cfg["min_evaluated_rows"],
         "wilson_95_interval_pct": summary["accuracy_wilson_95_pct"],
         "minimum_accuracy_pct": cfg["min_accuracy_pct"]},
        "Exact label matches among valid, completed outcomes. Small samples keep an unknown verdict.",
        minimum=cfg["min_accuracy_pct"], enough_evidence=enough,
    )
    checks["outcome_coverage"] = check(
        "Outcome coverage", summary["outcome_coverage_pct"], "%",
        {"evaluated_rows": evaluated, "all_rows": total, "pending_rows": summary["pending_rows"],
         "invalid_rows": summary["invalid_rows"], "minimum_pct": cfg["min_outcome_coverage_pct"]},
        "Valid completed outcomes divided by all supplied rows, including pending and invalid rows.",
        minimum=cfg["min_outcome_coverage_pct"],
    )
    confidence, invalid_confidence = _measurement(current, cfg["confidence_column"], 1)
    cost, invalid_cost = _measurement(current, cfg["cost_column"])
    latency, invalid_latency = _measurement(current, cfg["latency_column"])
    for name, invalid in (
        ("confidence", invalid_confidence), ("cost", invalid_cost), ("latency", invalid_latency),
    ):
        if invalid:
            findings.append({
                "code": f"INVALID_{name.upper()}", "count": len(invalid),
                "sample_record_numbers": invalid[:10],
                "message": f"Missing or invalid {name} values make this measurement incomplete.",
            })
    paired = [index for index in current["evaluated_indices"] if index in confidence]
    mean_confidence = math.fsum(confidence[index] / len(paired) for index in paired) if paired else None
    paired_accuracy = 100 * sum(index in current["correct_indices"] for index in paired) / len(paired) if paired else None
    gap = abs(100 * mean_confidence - paired_accuracy) if mean_confidence is not None else None
    checks["confidence_alignment"] = check(
        "Confidence alignment", gap, "pp",
        {"paired_rows": len(paired), "mean_confidence_pct": 100 * mean_confidence if paired else None,
         "paired_accuracy_pct": paired_accuracy, "maximum_gap_pp": cfg["max_confidence_gap_pp"],
         "minimum_paired_rows": cfg["min_evaluated_rows"]},
        "Absolute gap between mean reported confidence and accuracy on paired rows; this is a warning heuristic.",
        maximum=cfg["max_confidence_gap_pp"],
        enough_evidence=len(paired) >= cfg["min_evaluated_rows"] and len(paired) == evaluated,
    )
    # Divide before summing to keep finite, very large inputs from overflowing intermediates.
    cost_complete = len(cost) == total and evaluated == total and enough and correct > 0
    try:
        cost_per_correct = math.fsum(value / correct for value in cost.values()) if cost_complete else None
    except OverflowError as exc:
        raise ValueError("Cost per correct result exceeds the finite numeric range.") from exc
    if cost_per_correct is not None and not math.isfinite(cost_per_correct):
        raise ValueError("Cost per correct result exceeds the finite numeric range.")
    known_cost = sum(cost.values())
    checks["cost_per_correct"] = check(
        "Cost per correct result", cost_per_correct, cfg["cost_unit"],
        {"cost_rows": len(cost), "all_rows": total, "correct_rows": correct,
         "known_total_cost": known_cost if math.isfinite(known_cost) else None,
         "cost_unit": cfg["cost_unit"], "maximum": cfg["max_cost_per_correct"],
         "all_outcomes_complete": evaluated == total and total > 0},
        "Total cost of all supplied attempts divided by correct outcomes. Incomplete or zero-success samples are unknown.",
        maximum=cfg["max_cost_per_correct"],
    )
    mean_latency = math.fsum(value / len(latency) for value in latency.values()) if latency else None
    ordered_latency = sorted(latency.values())
    p95 = ordered_latency[math.ceil(0.95 * len(ordered_latency)) - 1] if ordered_latency else None
    checks["latency"] = check(
        "Mean latency", mean_latency, "ms",
        {"latency_rows": len(latency), "all_rows": total, "p95_ms": p95,
         "maximum_mean_ms": cfg["max_mean_latency_ms"]},
        "Mean and nearest-rank p95 over instrumented rows; incomplete latency coverage keeps the verdict unknown.",
        maximum=cfg["max_mean_latency_ms"], enough_evidence=bool(total) and len(latency) == total,
    )
    groups = _groups(current, cfg)
    baseline = _sample(baseline_csv, cfg, "Baseline") if baseline_csv is not None else None
    baseline_groups = _groups(baseline, cfg) if baseline is not None else None
    baseline_summary = baseline["summary"] if baseline is not None else None
    delta = None
    comparable = False
    if baseline is not None:
        if baseline_summary["invalid_rows"]:
            findings.append({
                "code": "INVALID_BASELINE_ROWS", "count": baseline_summary["invalid_rows"],
                "message": "Baseline contains invalid or duplicate result records; review the comparison.",
            })
        if summary["accuracy_pct"] is not None and baseline_summary["accuracy_pct"] is not None:
            delta = summary["accuracy_pct"] - baseline_summary["accuracy_pct"]
        comparable = (
            enough and baseline_summary["evaluated_rows"] >= cfg["min_evaluated_rows"]
            and summary["outcome_coverage_pct"] >= cfg["min_outcome_coverage_pct"]
            and baseline_summary["outcome_coverage_pct"] >= cfg["min_outcome_coverage_pct"]
            and not summary["invalid_rows"] and not baseline_summary["invalid_rows"]
        )
    checks["baseline_accuracy"] = check(
        "Accuracy change from baseline", delta, "pp",
        {"current_accuracy_pct": summary["accuracy_pct"],
         "baseline_accuracy_pct": baseline_summary["accuracy_pct"] if baseline_summary else None,
         "current_evaluated_rows": evaluated,
         "baseline_evaluated_rows": baseline_summary["evaluated_rows"] if baseline_summary else None,
         "allowed_drop_pp": cfg["allowed_accuracy_drop_pp"]},
        "Current minus baseline accuracy. Samples and outcome coverage must meet their minimums; this is descriptive, not causal.",
        minimum=-cfg["allowed_accuracy_drop_pp"], enough_evidence=comparable,
    )
    shift = None
    group_coverage = (
        baseline_groups is not None and groups["observed"] and baseline_groups["observed"]
        and total > 0 and baseline_summary["rows"] > 0
        and groups["missing_group_rows"] == 0 and baseline_groups["missing_group_rows"] == 0
    )
    if group_coverage:
        current_mix = {item["group"]: item["rows"] / total for item in groups["groups"]}
        baseline_mix = {item["group"]: item["rows"] / baseline_summary["rows"]
                        for item in baseline_groups["groups"]}
        shift = 50 * sum(abs(current_mix.get(group, 0) - baseline_mix.get(group, 0))
                         for group in set(current_mix) | set(baseline_mix))
    checks["case_mix"] = check(
        "Case mix shift", shift, "%",
        {"current_groups": groups, "baseline_groups": baseline_groups,
         "maximum_shift_pct": cfg["max_case_mix_shift_pct"]},
        "Total variation in supplied group shares. Changed case mix may affect accuracy comparisons.",
        maximum=cfg["max_case_mix_shift_pct"], enough_evidence=comparable and bool(group_coverage),
    )
    critical = ["accuracy", "outcome_coverage"]
    if cfg["confidence_column"] in current["header"]:
        critical.append("confidence_alignment")
    if cfg["max_cost_per_correct"] is not None:
        critical.append("cost_per_correct")
    if cfg["max_mean_latency_ms"] is not None:
        critical.append("latency")
    if baseline is not None:
        critical.append("baseline_accuracy")
        if groups["observed"] and baseline_groups["observed"]:
            critical.append("case_mix")
    for name in critical:
        if checks[name]["status"] == "attention":
            findings.append({"code": f"CHECK_{name.upper()}", "message": f"{checks[name]['label']} does not meet its configured threshold."})
    return {
        "schema_version": "1.0", "tool": "resqmonitor", "dataset": cfg["dataset_name"],
        "evaluated_at": reference_time(at).isoformat(), "synthetic": False,
        "status": overall([checks[name] for name in critical], findings),
        "summary": summary, "checks": checks, "findings": findings,
        "baseline_summary": baseline_summary, "groups": groups,
        "notes": [
            "Overall status covers: " + ", ".join(critical) + ". Other diagnostics remain separately visible.",
            "Outcome labels are supplied evidence, not independently established ground truth.",
            "Exact-match classification metrics do not assess free-form text quality or safety.",
            "Sample-size limits and Wilson intervals do not establish representativeness or causal model regression.",
            "Group accuracies below the minimum evaluated count are descriptive only; check subgroup counts separately.",
            "Reports include aggregate counts, category/group names and record numbers, not IDs or raw rows.",
            "Include failed attempts and retries in costs upstream; use one declared currency/unit without conversion.",
        ],
    }
