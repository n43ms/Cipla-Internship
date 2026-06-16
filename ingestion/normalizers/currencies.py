from __future__ import annotations

from typing import Any


COUNTRY_CURRENCY = {
    "nepal": "NPR",
    "np": "NPR",
    "sri lanka": "LKR",
    "srilanka": "LKR",
    "lk": "LKR",
    "myanmar": "MMK",
    "mm": "MMK",
    "oman": "OMR",
    "uae": "AED",
    "malaysia": "MYR",
}

COUNTRY_CODE = {
    "nepal": "NP",
    "np": "NP",
    "sri lanka": "LK",
    "srilanka": "LK",
    "lk": "LK",
    "myanmar": "MM",
    "mm": "MM",
    "oman": "OM",
    "uae": "AE",
    "malaysia": "MY",
}


def normalize_country_name(value: Any) -> str | None:
    if value is None:
        return None
    text = " ".join(str(value).strip().split())
    if not text:
        return None
    lowered = text.lower()
    if lowered in {"srilanka", "sl", "lk"}:
        return "Sri Lanka"
    if lowered == "np":
        return "Nepal"
    if lowered == "mm":
        return "Myanmar"
    if lowered == "uae":
        return "UAE"
    return text.title() if text.upper() != text else text


def country_code(value: Any) -> str | None:
    name = normalize_country_name(value)
    if not name:
        return None
    return COUNTRY_CODE.get(name.lower(), name[:2].upper())


def currency_for_country(value: Any) -> str | None:
    name = normalize_country_name(value)
    if not name:
        return None
    return COUNTRY_CURRENCY.get(name.lower())

