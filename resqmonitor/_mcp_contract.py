"""Typed output contract for the optional MCP adapter, not a core dependency."""

from typing import Any, Literal
from typing_extensions import NotRequired, TypedDict

Status = Literal["ok", "attention", "unknown"]


class Threshold(TypedDict):
    minimum: float | None
    maximum: float | None
    basis: Literal["point_estimate", "wilson_lower_bound"]
    assessment_value: float | None


class Check(TypedDict):
    label: str
    status: Status
    value: float | None
    unit: str
    message: str
    evidence: dict[str, Any]
    threshold_status: Status
    evidence_status: Literal["sufficient", "insufficient", "missing", "invalid", "not_configured"]
    reason_codes: list[str]
    threshold: Threshold


class Decision(TypedDict):
    outcome: Literal["criteria_met", "criteria_not_met", "undetermined"]
    scope: Literal["supplied_observations"]
    required_checks: list[str]
    action_authorized: Literal[False]


class Provenance(TypedDict):
    input_sha256: dict[str, str | None]
    policy_sha256: str
    source_verification: Literal["not_performed"]
    context_verification: Literal["not_performed"]
    generalization: Literal["not_assessed"]


class Report(TypedDict):
    schema_version: Literal["2.0"]
    tool: Literal["resqmonitor"]
    dataset: str
    evaluated_at: str
    synthetic: bool
    status: Status
    decision: Decision
    policy: dict[str, Any]
    provenance: Provenance
    summary: dict[str, Any]
    checks: dict[str, Check]
    findings: list[dict[str, Any]]
    notes: list[str]
    scenario: NotRequired[str]
    baseline_summary: dict[str, Any] | None
    groups: dict[str, Any]
