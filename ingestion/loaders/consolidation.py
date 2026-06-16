from __future__ import annotations

import hashlib

from ingestion.loaders.common import canonical_sheet_data, iter_mapped_rows
from ingestion.loaders.request_doctors import split_request_doctors
from ingestion.models import LoadResult, WorkbookProfile, to_decimal
from ingestion.normalizers import (
    currency_for_country,
    month_start,
    normalize_country_name,
    normalize_event_name,
    normalize_workflow_status,
)
from ingestion.schema_maps import CONSOLIDATION_SCHEMA
from ingestion.validators import IssueCollector


def load_consolidation(profile: WorkbookProfile) -> LoadResult:
    issues = IssueCollector()
    records: list[dict[str, object]] = []
    request_doctors: list[dict[str, object]] = []
    rows_seen = 0
    for sheet in canonical_sheet_data(profile):
        for row_number, row in iter_mapped_rows(sheet, CONSOLIDATION_SCHEMA):
            rows_seen += 1
            month = month_start(row.get("month"))
            country = normalize_country_name(row.get("country"))
            intervention_name = row.get("intervention_name")
            if not month.value or not country or not intervention_name:
                issues.add(
                    "error",
                    "consolidation_required_field_missing",
                    "Consolidation row is missing country, month, or intervention name",
                    entity_type="execution_request",
                    sheet_name=sheet.name,
                    row_number=row_number,
                    raw_value=row,
                )
                continue
            req_id = _clean_text(row.get("req_id"))
            request_uid = req_id or _fallback_request_uid(profile.file_hash, sheet.name, row_number, row)
            estimated = to_decimal(row.get("estimated_intervention"))
            confirmed = to_decimal(row.get("confirmed_contracted_amount"))
            currency_code = currency_for_country(country) or "UNKNOWN"
            record = {
                "request_key": request_uid,
                "req_id": req_id,
                "request_uid": request_uid,
                "country": country,
                "month_start_date": month.value,
                "rep_code": row.get("rep_code"),
                "rep_name": row.get("rep_name"),
                "venue": row.get("venue"),
                "intervention_name": str(intervention_name).strip(),
                "intervention_name_normalized": normalize_event_name(intervention_name),
                "intervention_type": row.get("intervention_type"),
                "intervention_sub_type": row.get("intervention_sub_type"),
                "estimated_intervention_local": estimated,
                "confirmed_contracted_amount_local": confirmed,
                "confirmed_vs_estimated_variance_local": (confirmed - estimated) if estimated and confirmed else None,
                "actual_total_expense_local": to_decimal(row.get("actual_total_expense")),
                "actual_btu_expense_local": to_decimal(row.get("actual_btu_expense")),
                "actual_btc_expense_local": to_decimal(row.get("actual_btc_expense")),
                "association_amount_local": to_decimal(row.get("association_amount")),
                "currency_code": currency_code,
                "fx_rate_status": "official" if currency_code == "LKR" else "missing",
                "request_approval_status": normalize_workflow_status(row.get("request_approval_status")),
                "request_confirmation_status": normalize_workflow_status(row.get("request_confirmation_status")),
                "post_approval_status": normalize_workflow_status(row.get("post_approval_status")),
                "post_confirmation_status": normalize_workflow_status(row.get("post_confirmation_status")),
                "current_owner_stage": row.get("current_owner_stage"),
                "approval_chain_json": {},
                "source_row_number": row_number,
            }
            records.append(record)
            request_doctors.extend(
                split_request_doctors(
                    request_key=request_uid,
                    attendance_type="expected",
                    doctors_raw=row.get("expected_doctors"),
                    pcodes_raw=row.get("expected_pcodes"),
                )
            )
            request_doctors.extend(
                split_request_doctors(
                    request_key=request_uid,
                    attendance_type="actual",
                    doctors_raw=row.get("actual_doctors"),
                    pcodes_raw=row.get("actual_pcodes"),
                )
            )
    return LoadResult(
        "consolidation",
        rows_seen,
        len(records),
        rows_seen - len(records),
        records,
        issues.issues,
        {"request_doctors": request_doctors},
    )


def _clean_text(value: object) -> str | None:
    if value is None:
        return None
    text = str(value).strip()
    return text or None


def _fallback_request_uid(file_hash: str, sheet_name: str, row_number: int, row: dict[str, object]) -> str:
    payload = f"{file_hash}|{sheet_name}|{row_number}|{row.get('country')}|{row.get('month')}|{row.get('intervention_name')}"
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()[:32]

