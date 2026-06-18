from __future__ import annotations

from typing import Any

from ingestion.normalizers.events import normalize_event_name


def derive_sri_lanka_may_snapshots(requests: list[dict[str, Any]]) -> list[dict[str, Any]]:
    groups: dict[tuple[str, str, str, object], dict[str, Any]] = {}
    for request in requests:
        if str(request.get("country") or "").casefold() != "sri lanka":
            continue
        month = request.get("month_start_date")
        if str(month) != "2026-05-01":
            continue
        event_name = str(request.get("intervention_name") or "").strip()
        if not event_name:
            continue
        key = (
            normalize_event_name(event_name),
            str(request.get("intervention_type") or ""),
            str(request.get("intervention_sub_type") or ""),
            month,
        )
        if key not in groups:
            groups[key] = {
                "country": "Sri Lanka",
                "month_start_date": month,
                "therapy": None,
                "event_type": request.get("intervention_type"),
                "event_name": event_name,
                "event_name_normalized": key[0],
                "planned_hcps": None,
                "engaged_hcps": 0,
                "raised_request_count": 0,
                "yp_total_doctors": None,
                "raised_total_doctors": 0,
                "approved_total_doctors": 0,
                "request_total_doctors": 0,
                "event_created_count": 0,
                "snapshot_source": "derived_from_consolidation",
                "status_source_value": "derived from consolidation",
                "normalized_status": "action_due",
                "source_sheet_name": "Working",
                "source_row_number": 0,
            }
        row = groups[key]
        row["raised_request_count"] = int(row["raised_request_count"] or 0) + 1
        row["event_created_count"] = int(row["event_created_count"] or 0) + 1
        row["engaged_hcps"] = int(row["engaged_hcps"] or 0) + int(request.get("attended_customer_count") or 0)
        row["raised_total_doctors"] = int(row["raised_total_doctors"] or 0) + int(request.get("expected_customer_count") or 0)
        row["approved_total_doctors"] = int(row["approved_total_doctors"] or 0) + int(request.get("attended_customer_count") or 0)
        row["request_total_doctors"] = int(row["request_total_doctors"] or 0) + int(request.get("expected_customer_count") or 0)
        if request.get("request_approval_status") in {"approved", "confirmed"} or request.get("attended_customer_count"):
            row["normalized_status"] = "executed"
    return list(groups.values())
