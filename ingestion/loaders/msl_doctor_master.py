from __future__ import annotations

import hashlib
from typing import Any

from ingestion.loaders.common import canonical_sheet_data, iter_mapped_rows
from ingestion.models import LoadResult, WorkbookProfile
from ingestion.normalizers import normalize_country_name, normalize_pcode
from ingestion.normalizers.doctors import normalize_doctor_name_key
from ingestion.schema_maps import MSL_DOCTOR_MASTER_SCHEMA
from ingestion.validators import IssueCollector


def load_msl_doctor_master(profile: WorkbookProfile) -> LoadResult:
    issues = IssueCollector()
    records: list[dict[str, Any]] = []
    rows_seen = 0
    missing_pcode_count = 0
    missing_doctor_name_count = 0

    for sheet in canonical_sheet_data(profile):
        for row_number, row in iter_mapped_rows(sheet, MSL_DOCTOR_MASTER_SCHEMA):
            rows_seen += 1
            country = normalize_country_name(row.get("country") or profile.country_scope)
            pcode = normalize_pcode(row.get("pcode"))
            doctor_name = _clean_text(row.get("doctor_name"))
            doctor_name_normalized = normalize_doctor_name_key(doctor_name)
            territory_name = _clean_text(row.get("territory_name"))
            if not country or not pcode.value or not doctor_name_normalized:
                if not pcode.value:
                    missing_pcode_count += 1
                if not doctor_name_normalized:
                    missing_doctor_name_count += 1
                issues.add(
                    "warning",
                    "msl_master_row_skipped",
                    (
                        "MSL row is missing country, P-code, or doctor name and cannot be "
                        "used as a doctor master mapping."
                    ),
                    entity_type="doctor_master_mapping",
                    sheet_name=sheet.name,
                    row_number=row_number,
                    raw_value=row,
                )
                continue

            records.append(
                {
                    "country": country,
                    "pcode_raw": None if row.get("pcode") is None else str(row.get("pcode")),
                    "pcode_normalized": pcode.value,
                    "doctor_name": doctor_name,
                    "doctor_short_name": _clean_text(row.get("doctor_short_name")),
                    "doctor_name_normalized": doctor_name_normalized,
                    "territory_name": territory_name,
                    "territory_id": _clean_text(row.get("territory_id")),
                    "patch": _clean_text(row.get("patch")),
                    "patch_name": _clean_text(row.get("patch_name")),
                    "legacy_code": _clean_text(row.get("legacy_code")),
                    "speciality": _clean_text(row.get("speciality")),
                    "doctor_class": _clean_text(row.get("doctor_class")),
                    "taskforce": _clean_text(row.get("taskforce")),
                    "rep_name": _clean_text(row.get("rep_name")),
                    "rep_code": _clean_text(row.get("rep_code")),
                    "employee_id": _clean_text(row.get("employee_id")),
                    "manager_name": _clean_text(row.get("manager_name")),
                    "town": _clean_text(row.get("town")),
                    "cis_no": _clean_text(row.get("cis_no")),
                    "registration_no": _clean_text(row.get("registration_no")),
                    "gender": _clean_text(row.get("gender")),
                    "source_sheet_name": sheet.name,
                    "source_row_number": row_number,
                    "source_row_hash": _row_hash(profile.file_hash, sheet.name, row_number, row),
                }
            )

    duplicate_name_keys = _duplicate_name_keys(records)
    return LoadResult(
        "msl_doctor_master",
        rows_seen,
        len(records),
        rows_seen - len(records),
        records,
        issues.issues,
        {
            "doctor_master_mapping_count": len(records),
            "missing_pcode_count": missing_pcode_count,
            "missing_doctor_name_count": missing_doctor_name_count,
            "duplicate_country_name_key_count": duplicate_name_keys,
        },
    )


def _clean_text(value: object) -> str | None:
    if value is None:
        return None
    text = " ".join(str(value).strip().split())
    return text or None


def _row_hash(file_hash: str, sheet_name: str, row_number: int, row: dict[str, object]) -> str:
    payload = f"{file_hash}|{sheet_name}|{row_number}|{row}"
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def _duplicate_name_keys(records: list[dict[str, Any]]) -> int:
    seen: dict[tuple[object, object], set[object]] = {}
    for record in records:
        key = (record["country"], record["doctor_name_normalized"])
        seen.setdefault(key, set()).add(record["pcode_normalized"])
    return sum(1 for pcodes in seen.values() if len(pcodes) > 1)
