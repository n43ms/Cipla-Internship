from __future__ import annotations

from datetime import date, datetime, timedelta
from typing import Any

from ingestion.models import ParseResult


MONTHS = {
    "jan": 1,
    "january": 1,
    "feb": 2,
    "february": 2,
    "mar": 3,
    "march": 3,
    "apr": 4,
    "april": 4,
    "may": 5,
    "jun": 6,
    "june": 6,
    "jul": 7,
    "july": 7,
    "aug": 8,
    "august": 8,
    "sep": 9,
    "sept": 9,
    "september": 9,
    "oct": 10,
    "october": 10,
    "nov": 11,
    "november": 11,
    "dec": 12,
    "december": 12,
}


def fiscal_year_for(month_value: date) -> str:
    year = month_value.year + 1 if month_value.month >= 4 else month_value.year
    return f"FY{str(year)[-2:]}"


def excel_serial_to_date(serial: int | float) -> date:
    return date(1899, 12, 30) + timedelta(days=int(serial))


def month_start(value: Any) -> ParseResult:
    if value is None:
        return ParseResult(None, value, "missing", "month is blank")
    if isinstance(value, datetime):
        return ParseResult(date(value.year, value.month, 1), value, "ok")
    if isinstance(value, date):
        return ParseResult(date(value.year, value.month, 1), value, "ok")
    if isinstance(value, int | float) and not isinstance(value, bool) and 20000 <= float(value) <= 60000:
        parsed = excel_serial_to_date(value)
        return ParseResult(date(parsed.year, parsed.month, 1), value, "ok_excel_serial")
    text = str(value).strip()
    if not text or text.lower() in {"nan", "none", "null"}:
        return ParseResult(None, value, "missing", "month is blank")
    normalized = text.lower().replace("'", "-").replace("/", "-").replace("_", "-")
    parts = [part for part in normalized.replace(",", " ").replace(".", " ").replace("-", " ").split() if part]
    if len(parts) >= 2:
        first, second = parts[0], parts[1]
        if first in MONTHS:
            year = _parse_year(second)
            if year:
                return ParseResult(date(year, MONTHS[first], 1), value, "ok")
        if second in MONTHS:
            year = _parse_year(first)
            if year:
                return ParseResult(date(year, MONTHS[second], 1), value, "ok")
    return ParseResult(None, value, "invalid", f"unrecognized month value: {value}")


def _parse_year(value: str) -> int | None:
    digits = "".join(char for char in value if char.isdigit())
    if not digits:
        return None
    parsed = int(digits)
    if parsed < 100:
        return 2000 + parsed
    if 1900 <= parsed <= 2100:
        return parsed
    return None

