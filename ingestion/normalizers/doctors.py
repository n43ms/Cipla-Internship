from __future__ import annotations

import re

_NON_WORD = re.compile(r"[^a-z0-9]+")


def normalize_doctor_name_key(value: object) -> str | None:
    if value is None:
        return None
    text = str(value).strip().lower()
    if not text:
        return None
    return _NON_WORD.sub(" ", text).strip() or None
