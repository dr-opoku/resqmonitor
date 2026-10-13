"""Input handling for a bounded, local CSV showcase."""

from __future__ import annotations

import csv
import io
import json
import math
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

MAX_BYTES = 5 * 1024 * 1024
MAX_ROWS = 50_000


def read_file(path: Path) -> str:
    """Bound input before decoding it, including files whose size changes while read."""
    with path.open("rb") as stream:
        data = stream.read(MAX_BYTES + 1)
    if len(data) > MAX_BYTES:
        raise ValueError("Input file exceeds the 5 MiB limit.")
    return data.decode("utf-8-sig")


def read_csv(text: str) -> tuple[list[str], list[dict[str, str]]]:
    """Reject ambiguous headers and malformed rows rather than silently dropping them."""
    if len(text.encode("utf-8")) > MAX_BYTES:
        raise ValueError("CSV input exceeds the 5 MiB limit.")
    reader = csv.reader(io.StringIO(text.lstrip("\ufeff"), newline=""), strict=True)
    try:
        raw_header = next(reader, None)
        if not raw_header:
            raise ValueError("CSV input must include a header, even when there are no rows.")
        header = [cell.strip() for cell in raw_header]
        if any(not name for name in header) or len(header) != len(set(header)):
            raise ValueError("CSV headers must be nonempty and unique.")
        rows = []
        for cells in reader:
            if not cells:
                continue
            if len(cells) != len(header):
                raise ValueError(f"CSV line {reader.line_num} has the wrong number of fields.")
            if len(rows) >= MAX_ROWS:
                raise ValueError("CSV input exceeds the 50,000-row limit.")
            rows.append(dict(zip(header, (cell.strip() for cell in cells))))
    except csv.Error as exc:
        raise ValueError(f"Malformed CSV: {exc}") from exc
    return header, rows


def json_object(text: str) -> dict[str, Any]:
    if len(text.encode("utf-8")) > MAX_BYTES:
        raise ValueError("Configuration exceeds the 5 MiB limit.")

    def reject_constant(value: str) -> None:
        raise ValueError(f"Non-finite JSON constant is not allowed: {value}")

    def unique_keys(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
        result: dict[str, Any] = {}
        for key, value in pairs:
            if key in result:
                raise ValueError(f"Duplicate configuration key: {key}")
            result[key] = value
        return result

    value = json.loads(text, parse_constant=reject_constant, object_pairs_hook=unique_keys)
    if not isinstance(value, dict):
        raise ValueError("Configuration must be a JSON object.")
    return value


def finite_number(value: Any, name: str, minimum: float | None = None) -> float:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise ValueError(f"{name} must be a finite number.")
    try:
        number = float(value)
    except OverflowError as exc:
        raise ValueError(f"{name} must be a finite number.") from exc
    if not math.isfinite(number) or (minimum is not None and number < minimum):
        raise ValueError(f"{name} must be finite and at least {minimum}.")
    return number


def numeric_cell(value: str) -> float | None:
    try:
        number = float(value)
        return number if math.isfinite(number) else None
    except (ValueError, OverflowError):
        return None


def timestamp(value: str) -> datetime:
    parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    if parsed.tzinfo is None or parsed.utcoffset() is None:
        raise ValueError("Timestamps require a timezone, for example 2026-10-13T12:00:00Z.")
    return parsed.astimezone(timezone.utc)


def reference_time(value: str | datetime | None) -> datetime:
    if value is None:
        return datetime.now(timezone.utc)
    if isinstance(value, str):
        return timestamp(value)
    if not isinstance(value, datetime) or value.tzinfo is None or value.utcoffset() is None:
        raise ValueError("Reference time must be a timezone-aware datetime or ISO timestamp.")
    return value.astimezone(timezone.utc)


def string_list(value: Any, name: str, allow_empty: bool = True) -> list[str]:
    if not isinstance(value, list) or any(not isinstance(x, str) or not x.strip() for x in value):
        raise ValueError(f"{name} must be a list of nonempty strings.")
    if len(value) != len(set(value)) or (not allow_empty and not value):
        raise ValueError(f"{name} must contain unique values and meet its minimum length.")
    return value


def check(label: str, value: float | None, unit: str, evidence: dict[str, Any],
          message: str, minimum: float | None = None, maximum: float | None = None,
          enough_evidence: bool = True) -> dict[str, Any]:
    if value is None or not enough_evidence:
        status = "unknown"
    elif (minimum is not None and value < minimum) or (maximum is not None and value > maximum):
        status = "attention"
    else:
        status = "ok"
    return {
        "label": label, "status": status,
        "value": round(value, 6) if value is not None else None,
        "unit": unit, "message": message, "evidence": evidence,
    }


def overall(checks: list[dict[str, Any]], findings: list[dict[str, Any]]) -> str:
    if findings or any(item["status"] == "attention" for item in checks):
        return "attention"
    return "unknown" if any(item["status"] == "unknown" for item in checks) else "ok"
