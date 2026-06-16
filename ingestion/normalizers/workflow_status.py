from __future__ import annotations

from typing import Any


def normalize_workflow_status(value: Any) -> str | None:
    if value is None:
        return None
    text = " ".join(str(value).strip().lower().replace("_", " ").split())
    if not text or text in {"nan", "none", "null"}:
        return None
    if "sent" in text and "correction" in text:
        return "sent_for_correction"
    if "reject" in text:
        return "rejected"
    if "delete" in text:
        return "deleted"
    if "approve" in text or text in {"approved", "yes"}:
        return "approved"
    if "confirm" in text:
        return "confirmed"
    if "draft" in text:
        return "draft"
    if "pending" in text:
        return "pending"
    return text.replace(" ", "_")

