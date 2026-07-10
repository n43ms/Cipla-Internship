from __future__ import annotations

import hashlib
from datetime import date
from typing import Any

from ingestion.loaders.common import canonical_sheet_data, iter_mapped_rows
from ingestion.models import LoadResult, WorkbookProfile, to_decimal
from ingestion.normalizers import (
    fx_for_country,
    month_start,
    normalize_country_name,
    normalize_event_name,
)
from ingestion.normalizers.engagements import classify_engagement
from ingestion.normalizers.sponsorship import classify_sponsorship
from ingestion.schema_maps import ERS_CONFERENCE_SCHEMA
from ingestion.validators import IssueCollector


def load_ers_conference(profile: WorkbookProfile) -> LoadResult:
    issues = IssueCollector()
    records: list[dict[str, Any]] = []
    rows_seen = 0

    for sheet in canonical_sheet_data(profile):
        for row_number, row in iter_mapped_rows(sheet, ERS_CONFERENCE_SCHEMA):
            rows_seen += 1
            country = normalize_country_name(row.get("country"))
            month = _month_from_value(row.get("month"))
            intervention_id = _clean_text(row.get("intervention_id"))
            doctor_name = _clean_text(row.get("doctor_name"))
            if not country or month is None or not intervention_id:
                issues.add(
                    "error",
                    "ers_required_field_missing",
                    "ERS row is missing country, month, or event code.",
                    entity_type="doctor_engagement",
                    sheet_name=sheet.name,
                    row_number=row_number,
                    raw_value=row,
                )
                continue
            if not doctor_name:
                issues.add(
                    "warning",
                    "ers_missing_doctor_name",
                    "ERS row has no doctor name and cannot be linked to a doctor.",
                    entity_type="doctor_engagement",
                    field_name="doctor_name",
                    sheet_name=sheet.name,
                    row_number=row_number,
                    raw_value=None,
                )
                continue

            issues.add(
                "warning",
                "ers_missing_pcode",
                (
                    "ERS conference row has no P-code; it remains weakly linked until a "
                    "doctor master or mapping source provides one."
                ),
                entity_type="doctor_engagement",
                field_name="pcode_normalized",
                sheet_name=sheet.name,
                row_number=row_number,
                raw_value=None,
            )

            fx = fx_for_country(country)
            sponsorship = classify_sponsorship(
                row.get("intervention_type"),
                "ERS Conference",
                row.get("intervention_name"),
            )
            engagement = classify_engagement(
                row.get("intervention_type"),
                "ERS Conference",
                row.get("intervention_name"),
                "honorarium",
            )
            honorarium_local = to_decimal(row.get("honorarium_local"))
            honorarium_usd = to_decimal(row.get("honorarium_usd"))
            records.append(
                {
                    "country": country,
                    "month_start_date": month,
                    "region": None,
                    "territory_code": None,
                    "fs_hq": None,
                    "request_date": None,
                    "expected_intervention_date": month,
                    "intervention_id": intervention_id,
                    "intervention_name": (
                        _clean_text(row.get("intervention_name")) or "ERS Conference"
                    ),
                    "intervention_name_normalized": normalize_event_name(
                        row.get("intervention_name") or "ERS Conference"
                    ),
                    "intervention_type": row.get("intervention_type"),
                    "intervention_subtype": "ERS Conference",
                    "pcode_raw": None,
                    "pcode_normalized": None,
                    "doctor_segment": None,
                    "doctor_name": doctor_name,
                    "estimated_intervention_amount_local": None,
                    "btu_expense_local": None,
                    "expense_against_advance_local": None,
                    "btc_expense_local": None,
                    "total_actual_intervention_expense_local": None,
                    "fmv_speciality": row.get("speciality"),
                    "fmv_tier": None,
                    "fmv_role": "conference",
                    "fmv_amount_local": honorarium_local,
                    "contract_id": None,
                    "contracted_amount_local": honorarium_local,
                    "contract_saving_local": None,
                    "status": "historical_ers",
                    "is_sponsorship": sponsorship.is_sponsorship,
                    "sponsorship_class": sponsorship.sponsorship_class,
                    "engagement_class": engagement.engagement_class,
                    "classification_reason": (
                        sponsorship.reason if sponsorship.is_sponsorship else engagement.reason
                    ),
                    "classification_confidence": max(
                        sponsorship.confidence if sponsorship.is_sponsorship else 0,
                        engagement.confidence,
                    ),
                    "currency_code": "USD" if honorarium_usd is not None else fx.currency_code,
                    "fx_rate_to_usd": 1 if honorarium_usd is not None else fx.rate_to_usd,
                    "fx_rate_source": (
                        "source_usd_column" if honorarium_usd is not None else fx.rate_source
                    ),
                    "fx_rate_date": fx.rate_date,
                    "fx_rate_status": "official" if honorarium_usd is not None else fx.rate_status,
                    "fmv_amount_usd": honorarium_usd,
                    "contracted_amount_usd": honorarium_usd,
                    "contract_saving_usd": None,
                    "source_sheet_name": sheet.name,
                    "source_row_number": row_number,
                    "source_row_hash": _row_hash(profile.file_hash, sheet.name, row_number, row),
                }
            )

    return LoadResult(
        "ers_conference",
        rows_seen,
        len(records),
        rows_seen - len(records),
        records,
        issues.issues,
        {
            "missing_pcode_count": sum(
                1 for issue in issues.issues if issue.error_code == "ers_missing_pcode"
            ),
            "usd_amount_count": sum(
                1 for record in records if record["contracted_amount_usd"] is not None
            ),
        },
    )


def _clean_text(value: object) -> str | None:
    if value is None:
        return None
    text = str(value).strip()
    return text or None


def _month_from_value(value: object) -> date | None:
    parsed = month_start(value)
    return parsed.value


def _row_hash(file_hash: str, sheet_name: str, row_number: int, row: dict[str, object]) -> str:
    payload = f"{file_hash}|{sheet_name}|{row_number}|{row}"
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()
