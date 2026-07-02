from __future__ import annotations

from typing import Any


def normalize_execution_status(value: Any, *, raised_request_count: int | None = None) -> str:
    if value is None or str(value).strip() == "":
        return "action_due" if not raised_request_count else "unknown"
    text = str(value).strip().lower()
    if text in {"1", "executed", "execute", "done", "completed", "complete"}:
        return "executed"
    if text in {"0", "action due", "action_due", "pending", "planned", "not executed"}:
        return "action_due"
    if "cancel" in text:
        return "cancelled"
    if "delay" in text:
        return "delayed"
    return "unknown"

