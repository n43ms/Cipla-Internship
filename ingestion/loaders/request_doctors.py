from __future__ import annotations

import re
from typing import Any

from ingestion.normalizers import normalize_pcode


SPLIT_PATTERN = re.compile(r"[\n;,|]+")


def split_multi_value(value: Any) -> list[str]:
    if value is None:
        return []
    text = str(value).strip()
    if not text:
        return []
    return [part.strip() for part in SPLIT_PATTERN.split(text) if part.strip()]


def split_request_doctors(
    *,
    request_key: str,
    attendance_type: str,
    doctors_raw: Any,
    pcodes_raw: Any,
    classes_raw: Any = None,
) -> list[dict[str, Any]]:
    doctors = split_multi_value(doctors_raw)
    pcodes = split_multi_value(pcodes_raw)
    classes = split_multi_value(classes_raw)
    count = max(len(doctors), len(pcodes), len(classes), 1 if doctors_raw or pcodes_raw else 0)
    records: list[dict[str, Any]] = []
    for index in range(count):
        pcode_raw = pcodes[index] if index < len(pcodes) else None
        pcode = normalize_pcode(pcode_raw)
        parse_status = "parsed" if pcode.value else "missing_pcode"
        if pcode.status in {"ambiguous", "invalid"}:
            parse_status = pcode.status
        records.append(
            {
                "request_key": request_key,
                "attendance_type": attendance_type,
                "doctor_name_raw": doctors[index] if index < len(doctors) else None,
                "doctor_class_raw": classes[index] if index < len(classes) else None,
                "pcode_raw": None if pcode_raw is None else str(pcode_raw),
                "pcode_normalized": pcode.value,
                "parse_status": parse_status,
                "source_position": index + 1,
            }
        )
    return records
