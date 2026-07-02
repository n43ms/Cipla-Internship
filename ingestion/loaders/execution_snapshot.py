from __future__ import annotations

from ingestion.loaders.common import canonical_sheet_data, iter_mapped_rows
from ingestion.models import LoadResult, WorkbookProfile, to_int
from ingestion.normalizers import month_start, normalize_country_name, normalize_event_name, normalize_execution_status
from ingestion.schema_maps import EXECUTION_SCHEMA
from ingestion.validators import IssueCollector


def load_execution_snapshot(profile: WorkbookProfile) -> LoadResult:
    issues = IssueCollector()
    records: list[dict[str, object]] = []
    rows_seen = 0
    sheets = canonical_sheet_data(profile)
    dedicated_countries = {
        country
        for country in (normalize_country_name(sheet.name) for sheet in sheets if sheet.name.lower() != "yp")
        if country
    }
    for sheet in sheets:
        inferred_country = None if sheet.name.lower() == "yp" else sheet.name
        for row_number, row in iter_mapped_rows(sheet, EXECUTION_SCHEMA):
            rows_seen += 1
            month = month_start(row.get("month") or _month_from_filename(profile.original_filename))
            event_name = row.get("event_name")
            country = normalize_country_name(row.get("country") or inferred_country or profile.country_scope)
            if sheet.name.lower() == "yp" and country in dedicated_countries:
                continue
            if not event_name or not month.value or not country:
                issues.add(
                    "warning",
                    "execution_row_skipped",
                    "Execution snapshot row is missing country, month, or event name",
                    entity_type="execution_snapshot",
                    sheet_name=sheet.name,
                    row_number=row_number,
                    raw_value=row,
                )
                continue
            planned_hcps = to_int(row.get("planned_hcps"))
            yp_total_doctors = to_int(row.get("yp_total_doctors"))
            engaged_hcps = to_int(row.get("engaged_hcps"))
            approved_total_doctors = to_int(row.get("approved_total_doctors"))
            raised_count = to_int(row.get("raised_request_count"))
            raised_total_doctors = to_int(row.get("raised_total_doctors"))
            request_total_doctors = to_int(row.get("request_total_doctors"))
            event_created_count = to_int(row.get("event_created_count"))
            planned_hcps = planned_hcps if planned_hcps is not None else yp_total_doctors
            engaged_hcps = engaged_hcps if engaged_hcps is not None else approved_total_doctors
            raised_count = raised_count if raised_count is not None else event_created_count
            records.append(
                {
                    "country": country,
                    "month_start_date": month.value,
                    "therapy": row.get("therapy"),
                    "event_type": row.get("event_type"),
                    "event_name": str(event_name).strip(),
                    "event_name_normalized": normalize_event_name(event_name),
                    "planned_hcps": planned_hcps,
                    "engaged_hcps": engaged_hcps,
                    "raised_request_count": raised_count,
                    "yp_total_doctors": yp_total_doctors,
                    "raised_total_doctors": raised_total_doctors,
                    "approved_total_doctors": approved_total_doctors,
                    "request_total_doctors": request_total_doctors,
                    "event_created_count": event_created_count,
                    "snapshot_source": "monthly_planner",
                    "status_source_value": None if row.get("status") is None else str(row.get("status")),
                    "normalized_status": normalize_execution_status(row.get("status"), raised_request_count=raised_count),
                    "source_sheet_name": sheet.name,
                    "source_row_number": row_number,
                }
            )
    if "Sri Lanka" not in {record["country"] for record in records} and "may" in profile.original_filename.lower():
        issues.add(
            "info",
            "sri_lanka_may_tab_missing",
            "May execution workbook has no Sri Lanka tab; later reconciliation derives evidence from consolidation",
            entity_type="execution_snapshot",
        )
    return LoadResult("execution_snapshot", rows_seen, len(records), rows_seen - len(records), records, issues.issues)


def _month_from_filename(filename: str) -> str | None:
    lowered = filename.lower()
    if "apr" in lowered:
        return "Apr-26"
    if "may" in lowered:
        return "May-26"
    return None
