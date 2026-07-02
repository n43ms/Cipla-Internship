from __future__ import annotations

from decimal import Decimal, InvalidOperation
from typing import Any

from ingestion.models import ParseResult


INVALID_VALUES = {"", "nan", "none", "null", "0", "0.0", "-"}


def normalize_pcode(value: Any) -> ParseResult:
    if value is None:
        return ParseResult(None, value, "missing", "Pcode is blank")
    text = str(value).strip()
    if text.lower() in INVALID_VALUES:
        return ParseResult(None, value, "missing", "Pcode is blank or zero-like")
    if isinstance(value, str) and len(text) > 1 and text.startswith("0") and not set(text) - set("0123456789"):
        return ParseResult(text, value, "ok")
    try:
        decimal_value = Decimal(text.replace(",", ""))
        if decimal_value == 0:
            return ParseResult(None, value, "missing", "Pcode is zero-like")
        if decimal_value == decimal_value.to_integral_value():
            return ParseResult(str(decimal_value.quantize(Decimal("1"))), value, "ok")
    except (InvalidOperation, ValueError):
        pass
    return ParseResult(" ".join(text.split()), value, "ok")
