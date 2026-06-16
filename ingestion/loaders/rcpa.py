from __future__ import annotations

from collections import defaultdict
from decimal import Decimal

from ingestion.loaders.common import canonical_sheet_data, iter_mapped_rows
from ingestion.models import LoadResult, WorkbookProfile, to_decimal
from ingestion.normalizers import currency_for_country, month_start, normalize_country_name, normalize_pcode
from ingestion.schema_maps import RCPA_SCHEMA
from ingestion.validators import IssueCollector


def load_rcpa(profile: WorkbookProfile) -> LoadResult:
    issues = IssueCollector()
    rows_seen = 0
    aggregate: dict[tuple[object, ...], dict[str, object]] = {}
    for sheet in canonical_sheet_data(profile):
        for row_number, row in iter_mapped_rows(sheet, RCPA_SCHEMA):
            rows_seen += 1
            country = normalize_country_name(row.get("country") or profile.country_scope)
            month = month_start(row.get("month"))
            pcode = normalize_pcode(row.get("pcode"))
            brand = _text(row.get("brand_group"))
            sku = _text(row.get("sku")) or brand
            own_or_competitor = _text(row.get("own_or_competitor")) or "unknown"
            quantity = to_decimal(row.get("quantity")) or Decimal("0")
            if not country or not month.value or not pcode.value or not brand:
                issues.add(
                    "warning",
                    "rcpa_row_skipped",
                    "RCPA row is missing country, month, Pcode, or brand",
                    entity_type="rcpa_prescription",
                    sheet_name=sheet.name,
                    row_number=row_number,
                    raw_value=row,
                )
                continue
            currency_code = currency_for_country(country) or "UNKNOWN"
            key = (country, month.value, pcode.value, brand, sku, own_or_competitor.lower(), currency_code)
            if key not in aggregate:
                aggregate[key] = {
                    "country": country,
                    "month_start_date": month.value,
                    "pcode_raw": None if row.get("pcode") is None else str(row.get("pcode")),
                    "pcode_normalized": pcode.value,
                    "doctor_name": row.get("doctor_name"),
                    "speciality": row.get("speciality"),
                    "doctor_class": row.get("doctor_class"),
                    "patch_name": row.get("patch_name"),
                    "active_status": row.get("active_status"),
                    "brand_group": brand,
                    "sku": sku,
                    "sku_detail": row.get("sku_detail"),
                    "own_or_competitor": own_or_competitor.lower(),
                    "prescription_qty": Decimal("0"),
                    "prescription_value_local": Decimal("0"),
                    "currency_code": currency_code,
                    "prescription_value_usd": None,
                    "row_count_aggregated": 0,
                }
            aggregate[key]["prescription_qty"] += quantity  # type: ignore[operator]
            aggregate[key]["prescription_value_local"] += to_decimal(row.get("value")) or Decimal("0")  # type: ignore[operator]
            aggregate[key]["row_count_aggregated"] += 1  # type: ignore[operator]
    records = list(aggregate.values())
    return LoadResult("rcpa", rows_seen, len(records), rows_seen - sum(r["row_count_aggregated"] for r in records), records, issues.issues)


def _text(value: object) -> str | None:
    if value is None:
        return None
    text = str(value).strip()
    return text or None
