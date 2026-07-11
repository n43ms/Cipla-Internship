from __future__ import annotations

import hashlib
from decimal import Decimal

from ingestion.loaders.common import canonical_sheet_data, iter_mapped_rows
from ingestion.loaders.request_doctors import split_request_doctors
from ingestion.models import LoadResult, WorkbookProfile, to_date, to_decimal, to_int
from ingestion.normalizers import (
    fx_for_country,
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
            intervention_date = to_date(row.get("intervention_date"))
            intervention_end_date = to_date(row.get("intervention_end_date"))
            actual_intervention_date = to_date(row.get("actual_intervention_date"))
            month = _month_from_row(row, intervention_date, actual_intervention_date)
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
            request_uid = req_id or _fallback_request_uid(
                profile.file_hash,
                sheet.name,
                row_number,
                row,
            )
            estimated = to_decimal(row.get("estimated_intervention"))
            confirmed = to_decimal(row.get("confirmed_contracted_amount"))
            actual_total = to_decimal(row.get("actual_total_expense"))
            actual_btu = to_decimal(row.get("actual_btu_expense"))
            actual_btc = to_decimal(row.get("actual_btc_expense"))
            if actual_total is None and (actual_btu is not None or actual_btc is not None):
                actual_total = (actual_btu or Decimal("0")) + (actual_btc or Decimal("0"))
            fx = fx_for_country(country)
            request_approval_status = normalize_workflow_status(row.get("request_approval_status"))
            request_confirmation_status = normalize_workflow_status(
                row.get("request_confirmation_status")
            )
            post_approval_status = normalize_workflow_status(row.get("post_approval_status"))
            post_confirmation_status = normalize_workflow_status(
                row.get("post_confirmation_status")
            )
            record = {
                "request_key": request_uid,
                "req_id": req_id,
                "request_uid": request_uid,
                "country": country,
                "month_start_date": month.value,
                "rep_code": row.get("rep_code"),
                "rep_name": row.get("rep_name"),
                "fs_hq": row.get("fs_hq"),
                "intervention_date": intervention_date,
                "intervention_end_date": intervention_end_date,
                "actual_intervention_date": actual_intervention_date,
                "venue": row.get("venue"),
                "intervention_name": str(intervention_name).strip(),
                "intervention_name_normalized": normalize_event_name(intervention_name),
                "intervention_type": row.get("intervention_type"),
                "intervention_sub_type": row.get("intervention_sub_type"),
                "topic_remarks": row.get("topic_remarks"),
                "estimated_intervention_local": estimated,
                "confirmed_contracted_amount_local": confirmed,
                "confirmed_vs_estimated_variance_local": (
                    (confirmed - estimated) if estimated and confirmed else None
                ),
                "actual_total_expense_local": actual_total,
                "actual_btu_expense_local": actual_btu,
                "actual_btc_expense_local": actual_btc,
                "total_btc_local": to_decimal(row.get("total_btc")),
                "expected_btu_local": to_decimal(row.get("expected_btu")),
                "association_amount_local": to_decimal(row.get("association_amount")),
                "association_contract_id": row.get("association_contract_id"),
                "association_deliverables": row.get("association_deliverables"),
                "currency_code": fx.currency_code,
                "fx_rate_to_usd": fx.rate_to_usd,
                "fx_rate_source": fx.rate_source,
                "fx_rate_date": fx.rate_date,
                "fx_rate_status": fx.rate_status,
                "estimated_intervention_usd": fx.to_usd(estimated),
                "confirmed_contracted_amount_usd": fx.to_usd(confirmed),
                "actual_total_expense_usd": fx.to_usd(actual_total),
                "actual_btu_expense_usd": fx.to_usd(actual_btu),
                "actual_btc_expense_usd": fx.to_usd(actual_btc),
                "direct_hcp_spend_local": actual_btu,
                "overhead_spend_local": actual_btc,
                "total_roi_spend_local": actual_total,
                "direct_hcp_spend_usd": fx.to_usd(actual_btu),
                "overhead_spend_usd": fx.to_usd(actual_btc),
                "total_roi_spend_usd": fx.to_usd(actual_total),
                "expected_customer_count": to_int(row.get("expected_customer_count")),
                "attended_customer_count": to_int(row.get("attended_customer_count")),
                "expected_category_raw": row.get("expected_category_raw"),
                "attended_category_raw": row.get("attended_category_raw"),
                "request_approval_status": request_approval_status,
                "request_confirmation_status": request_confirmation_status,
                "post_approval_status": post_approval_status,
                "post_confirmation_status": post_confirmation_status,
                "expense_submitted_date": to_date(row.get("expense_submitted_date")),
                "expense_confirmed_date": to_date(row.get("expense_confirmed_date")),
                "current_owner_stage": _current_owner_stage(
                    row.get("current_owner_stage"),
                    row.get("request_approval_status"),
                    row.get("request_confirmation_status"),
                    row.get("post_approval_status"),
                    row.get("post_confirmation_status"),
                    request_approval_status,
                    request_confirmation_status,
                    post_approval_status,
                    post_confirmation_status,
                ),
                "approval_status": normalize_workflow_status(row.get("approval_status")),
                "confirmation_status": normalize_workflow_status(row.get("confirmation_status")),
                "cancellation_reason": row.get("cancellation_reason"),
                "city": row.get("city"),
                "state": row.get("state"),
                "approval_chain_json": {
                    f"level_{level}": row.get(f"level_{level}_approval")
                    for level in range(1, 7)
                    if row.get(f"level_{level}_approval") is not None
                },
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


def _month_from_row(
    row: dict[str, object],
    intervention_date,
    actual_intervention_date,
):
    month = month_start(row.get("month"))
    if month.value:
        return month
    for candidate in (actual_intervention_date, intervention_date):
        if candidate:
            return month_start(candidate)
    return month


def _fallback_request_uid(
    file_hash: str,
    sheet_name: str,
    row_number: int,
    row: dict[str, object],
) -> str:
    payload = (
        f"{file_hash}|{sheet_name}|{row_number}|{row.get('country')}|"
        f"{row.get('month')}|{row.get('intervention_name')}"
    )
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()[:32]


def _current_owner_stage(
    raw_owner_stage: object,
    raw_request_approval_status: object,
    raw_request_confirmation_status: object,
    raw_post_approval_status: object,
    raw_post_confirmation_status: object,
    request_approval_status: str | None,
    request_confirmation_status: str | None,
    post_approval_status: str | None,
    post_confirmation_status: str | None,
) -> str:
    raw_text = _clean_text(raw_owner_stage)
    if raw_text:
        return raw_text
    named_owner = (
        _pending_with(raw_request_approval_status, "request approval")
        or _pending_with(raw_request_confirmation_status, "request confirmation")
        or _pending_with(raw_post_approval_status, "post report approval")
        or _pending_with(raw_post_confirmation_status, "post report confirmation")
    )
    if named_owner:
        return named_owner
    if request_approval_status in {"pending_owner", "pending_confirmation", "pending"}:
        return "request approval pending"
    if request_confirmation_status in {"pending_owner", "pending_confirmation", "pending"}:
        return "request confirmation pending"
    pending_post_statuses = {
        "pending_owner",
        "pending_confirmation",
        "pending",
        "sent_for_correction",
    }
    if post_approval_status in pending_post_statuses:
        return "post report approval pending"
    if post_confirmation_status in pending_post_statuses:
        return "post report confirmation pending"
    if post_approval_status == "draft" or post_confirmation_status == "draft":
        return "post report not submitted"
    if request_approval_status in {"deleted", "rejected"}:
        return f"request {request_approval_status}"
    if post_approval_status == "approved" or post_confirmation_status in {"approved", "confirmed"}:
        return "post report approved"
    if request_approval_status in {"approved", "confirmed"} or request_confirmation_status in {
        "approved",
        "confirmed",
    }:
        return "request approved; report pending"
    return "unknown"


def _pending_with(value: object, stage: str) -> str | None:
    raw_text = _clean_text(value)
    if not raw_text:
        return None
    normalized = " ".join(raw_text.split())
    lowered = normalized.casefold()
    marker = "pending with "
    if marker not in lowered:
        return None
    owner_start = lowered.index(marker) + len(marker)
    owner = normalized[owner_start:].strip(" .:-")
    if not owner:
        return f"{stage} pending"
    return f"{stage} pending with {owner}"
