from __future__ import annotations

import hashlib
from datetime import date
from typing import Any

from ingestion.loaders.common import canonical_sheet_data, iter_mapped_rows
from ingestion.models import LoadResult, WorkbookProfile, to_date, to_decimal
from ingestion.normalizers import (
    fx_for_country,
    month_start,
    normalize_country_name,
    normalize_event_name,
    normalize_pcode,
)
from ingestion.normalizers.contract_economics import normalize_contract_economics
from ingestion.normalizers.engagements import classify_engagement
from ingestion.normalizers.sponsorship import classify_sponsorship
from ingestion.schema_maps import DOCTOR_CONTRACT_SCHEMA
from ingestion.validators import IssueCollector


def load_doctor_wise_intervention(profile: WorkbookProfile) -> LoadResult:
    issues = IssueCollector()
    records: list[dict[str, Any]] = []
    rows_seen = 0

    for sheet in canonical_sheet_data(profile):
        for row_number, row in iter_mapped_rows(sheet, DOCTOR_CONTRACT_SCHEMA):
            rows_seen += 1
            country = normalize_country_name(row.get("country"))
            intervention_id = _clean_text(row.get("intervention_id"))
            doctor_name = _clean_text(row.get("doctor_name"))
            pcode_raw = _clean_text(row.get("doctor_code"))
            pcode_result = normalize_pcode(pcode_raw)
            pcode = pcode_result.value
            if not country or not intervention_id or not doctor_name:
                issues.add(
                    "error",
                    "doctor_wise_required_field_missing",
                    "Doctor-wise row is missing country, intervention ID, or doctor name.",
                    entity_type="doctor_engagement",
                    sheet_name=sheet.name,
                    row_number=row_number,
                    raw_value=row,
                )
                continue
            if not pcode:
                issues.add(
                    "warning",
                    "doctor_wise_missing_pcode",
                    "Doctor-wise row has no usable P-code; it will remain weakly linked.",
                    entity_type="doctor_engagement",
                    field_name="doctor_code",
                    sheet_name=sheet.name,
                    row_number=row_number,
                    raw_value=pcode_raw,
                )

            request_date = to_date(row.get("request_date"))
            expected_date = to_date(row.get("expected_intervention_date"))
            month = _month_from_dates(expected_date, request_date, row.get("month"))
            if month is None:
                issues.add(
                    "error",
                    "doctor_wise_month_missing",
                    "Doctor-wise row has no request or expected intervention date for month assignment.",
                    entity_type="doctor_engagement",
                    field_name="expected_intervention_date",
                    sheet_name=sheet.name,
                    row_number=row_number,
                    raw_value=row.get("expected_intervention_date"),
                )
                continue

            fx = fx_for_country(country)
            economics = normalize_contract_economics(
                country=country,
                fmv_amount=row.get("fmv_amount"),
                contracted_amount=row.get("contracted_amount"),
                fx=fx,
            )
            sponsorship = classify_sponsorship(
                row.get("intervention_type"),
                row.get("intervention_subtype"),
                row.get("intervention_name"),
            )
            engagement = classify_engagement(
                row.get("intervention_type"),
                row.get("intervention_subtype"),
                row.get("fmv_role"),
                row.get("intervention_name"),
            )
            if engagement.engagement_class == "unclassified":
                issues.add(
                    "warning",
                    "doctor_wise_unclassified_engagement_label",
                    "Doctor-wise row has no deterministic sponsorship or engagement classification.",
                    entity_type="doctor_engagement",
                    field_name="intervention_type",
                    sheet_name=sheet.name,
                    row_number=row_number,
                    raw_value=row.get("intervention_type"),
                )
            record = {
                "country": country,
                "month_start_date": month,
                "region": row.get("region"),
                "territory_code": row.get("territory_code"),
                "fs_hq": row.get("fs_hq"),
                "request_date": request_date,
                "expected_intervention_date": expected_date,
                "intervention_id": intervention_id,
                "intervention_name": _clean_text(row.get("intervention_name")),
                "intervention_name_normalized": normalize_event_name(row.get("intervention_name")),
                "intervention_type": row.get("intervention_type"),
                "intervention_subtype": row.get("intervention_subtype"),
                "pcode_raw": pcode_raw,
                "pcode_normalized": pcode,
                "doctor_segment": row.get("doctor_segment"),
                "doctor_name": doctor_name,
                "estimated_intervention_amount_local": to_decimal(
                    row.get("estimated_intervention_amount")
                ),
                "btu_expense_local": to_decimal(row.get("btu_expense")),
                "expense_against_advance_local": to_decimal(row.get("expense_against_advance")),
                "btc_expense_local": to_decimal(row.get("btc_expense")),
                "total_actual_intervention_expense_local": to_decimal(
                    row.get("total_actual_intervention_expense")
                ),
                "fmv_speciality": row.get("fmv_speciality"),
                "fmv_tier": row.get("fmv_tier"),
                "fmv_role": row.get("fmv_role"),
                "fmv_amount_local": economics.fmv_amount_local,
                "contract_id": row.get("contract_id"),
                "contracted_amount_local": economics.contracted_amount_local,
                "contract_saving_local": economics.contract_saving_local,
                "status": row.get("status"),
                "is_sponsorship": sponsorship.is_sponsorship,
                "sponsorship_class": sponsorship.sponsorship_class,
                "engagement_class": engagement.engagement_class,
                "classification_reason": (
                    sponsorship.reason
                    if sponsorship.is_sponsorship
                    else engagement.reason
                ),
                "classification_confidence": max(
                    sponsorship.confidence if sponsorship.is_sponsorship else 0,
                    engagement.confidence,
                ),
                "currency_code": fx.currency_code,
                "fx_rate_to_usd": fx.rate_to_usd,
                "fx_rate_source": fx.rate_source,
                "fx_rate_date": fx.rate_date,
                "fx_rate_status": fx.rate_status,
                "fmv_amount_usd": economics.fmv_amount_usd,
                "contracted_amount_usd": economics.contracted_amount_usd,
                "contract_saving_usd": economics.contract_saving_usd,
                "source_sheet_name": sheet.name,
                "source_row_number": row_number,
                "source_row_hash": _row_hash(profile.file_hash, sheet.name, row_number, row),
            }
            records.append(record)

    return LoadResult(
        "doctor_contract",
        rows_seen,
        len(records),
        rows_seen - len(records),
        records,
        issues.issues,
        {
            "missing_pcode_count": sum(
                1 for issue in issues.issues if issue.error_code == "doctor_wise_missing_pcode"
            ),
            "missing_fmv_count": sum(1 for record in records if record["fmv_amount_local"] is None),
            "missing_contracted_value_count": sum(
                1 for record in records if record["contracted_amount_local"] is None
            ),
        },
    )


def _clean_text(value: object) -> str | None:
    if value is None:
        return None
    text = str(value).strip()
    return text or None


def _month_from_dates(*values: object) -> date | None:
    for value in values:
        parsed_date = to_date(value)
        if parsed_date:
            return date(parsed_date.year, parsed_date.month, 1)
        parsed_month = month_start(value)
        if parsed_month.value:
            return parsed_month.value
    return None


def _row_hash(file_hash: str, sheet_name: str, row_number: int, row: dict[str, object]) -> str:
    payload = f"{file_hash}|{sheet_name}|{row_number}|{row}"
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()
