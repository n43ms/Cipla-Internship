from __future__ import annotations

from ingestion.loaders.common import canonical_sheet_data, iter_mapped_rows
from ingestion.models import LoadResult, WorkbookProfile, to_int
from ingestion.normalizers import fiscal_year_for, month_start, normalize_country_name, normalize_event_name
from ingestion.schema_maps import PLANNER_SCHEMA
from ingestion.validators import IssueCollector


def load_planner(profile: WorkbookProfile) -> LoadResult:
    issues = IssueCollector()
    records: list[dict[str, object]] = []
    rows_seen = 0
    for sheet in canonical_sheet_data(profile):
        for row_number, row in iter_mapped_rows(sheet, PLANNER_SCHEMA):
            rows_seen += 1
            month = month_start(row.get("month"))
            event_name = row.get("event_name")
            country = normalize_country_name(row.get("country") or profile.country_scope)
            if not event_name or not month.value or not country:
                issues.add(
                    "warning",
                    "planner_required_field_missing",
                    "Planner row is missing country, month, or event name",
                    entity_type="plan_event",
                    sheet_name=sheet.name,
                    row_number=row_number,
                    raw_value=row,
                )
                continue
            records.append(
                {
                    "country": country,
                    "month_start_date": month.value,
                    "fiscal_year": fiscal_year_for(month.value),
                    "therapy": row.get("therapy"),
                    "event_type": row.get("event_type"),
                    "event_name": str(event_name).strip(),
                    "event_name_normalized": normalize_event_name(event_name),
                    "central_or_local": row.get("central_or_local"),
                    "brand_name_1": row.get("brand_name_1"),
                    "brand_name_2": row.get("brand_name_2"),
                    "planned_total_hcps": to_int(row.get("planned_total_hcps")),
                    "planned_patients": to_int(row.get("planned_patients")),
                    "planned_pharmacies": to_int(row.get("planned_pharmacies")),
                    "total_planned_cost_usd": row.get("total_planned_cost_usd"),
                    "source_sheet_name": sheet.name,
                    "source_row_number": row_number,
                }
            )
    return LoadResult("planner", rows_seen, len(records), rows_seen - len(records), records, issues.issues)
