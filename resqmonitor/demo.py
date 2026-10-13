"""Bundled, entirely synthetic classification examples."""

from __future__ import annotations

from importlib.resources import files
from typing import Any

from ._support import json_object
from .engine import analyze

SCENARIOS = ("healthy", "degraded", "unknown")
DEMO_AT = "2026-10-13T12:00:00Z"


def demo(scenario: str = "degraded") -> dict[str, Any]:
    if scenario not in SCENARIOS:
        raise ValueError(f"Unknown scenario: {scenario}")
    fixtures = files("resqmonitor").joinpath("fixtures")
    report = analyze(
        fixtures.joinpath(f"{scenario}.csv").read_text(encoding="utf-8"),
        json_object(fixtures.joinpath("config.json").read_text(encoding="utf-8")),
        baseline_csv=fixtures.joinpath("baseline.csv").read_text(encoding="utf-8"),
        at=DEMO_AT,
    )
    report.update(synthetic=True, scenario=scenario)
    return report
