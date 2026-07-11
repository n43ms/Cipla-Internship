from __future__ import annotations

import re
from typing import Any

PCODE_PATTERN = re.compile(r"\b(?:\d{4,}|\d{2,}\.\d+)\b")
CONTRACT_ID_PATTERN = re.compile(
    r"(?i)\b(?:contract|agreement)\s*(?:id|no\.?|number)?\s*[:#-]?\s*[A-Z]{0,4}[-/ ]?\d{2,}\b"
)
MONEY_PATTERN = re.compile(
    r"(?i)\b(?:usd|lkr|npr|mmk|aed|omr|myr|rs\.?|₹|\$)\s*[\d,]+(?:\.\d+)?\b|"
    r"\b[\d,]{5,}(?:\.\d+)?\s*(?:usd|lkr|npr|mmk|aed|omr|myr|rs\.?)\b"
)
DOCTOR_NAME_PATTERN = re.compile(
    r"(?i)\b(?:dr\.?|doctor|hcp|pcode\s+for)\s+([A-Z][A-Za-z.'-]+(?:\s+[A-Z][A-Za-z.'-]+){0,3})"
)
RAW_SOURCE_PATTERN = re.compile(
    r"(?is)(?:source\s+row|raw\s+row|workbook\s+row|raw\s+source|source\s+excerpt)\s*[:=]\s*.+"
)


def redact_text(value: str) -> tuple[str, bool]:
    """Mask identifiers and source-like snippets before provider calls or persistence."""

    redacted = value
    redacted = RAW_SOURCE_PATTERN.sub("[SOURCE_EXCERPT]", redacted)
    redacted = CONTRACT_ID_PATTERN.sub("[CONTRACT_ID]", redacted)
    redacted = MONEY_PATTERN.sub("[AMOUNT]", redacted)
    redacted = PCODE_PATTERN.sub("[PCODE]", redacted)

    def _mask_name(match: re.Match[str]) -> str:
        prefix = match.group(0)[: match.group(0).lower().find(match.group(1).lower())]
        return f"{prefix}[NAME]"

    redacted = DOCTOR_NAME_PATTERN.sub(_mask_name, redacted)
    return redacted, redacted != value


def redact_payload(value: Any) -> tuple[Any, bool]:
    """Recursively redact strings inside structured AI context."""

    changed = False
    if isinstance(value, str):
        return redact_text(value)
    if isinstance(value, list):
        items = []
        for item in value:
            redacted_item, item_changed = redact_payload(item)
            items.append(redacted_item)
            changed = changed or item_changed
        return items, changed
    if isinstance(value, tuple):
        items = []
        for item in value:
            redacted_item, item_changed = redact_payload(item)
            items.append(redacted_item)
            changed = changed or item_changed
        return tuple(items), changed
    if isinstance(value, dict):
        result = {}
        for key, item in value.items():
            redacted_item, item_changed = redact_payload(item)
            result[key] = redacted_item
            changed = changed or item_changed
        return result, changed
    return value, False
