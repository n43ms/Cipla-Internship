from __future__ import annotations

from decimal import Decimal

from ingestion.loaders.common import canonical_sheet_data, iter_mapped_rows
from ingestion.models import LoadResult, WorkbookProfile, to_decimal
from ingestion.normalizers import (
    currency_for_country,
    month_start,
    normalize_country_name,
    normalize_pcode,
)
from ingestion.schema_maps import RCPA_SCHEMA
from ingestion.validators import IssueCollector


def load_rcpa(profile: WorkbookProfile) -> LoadResult:
    issues = IssueCollector()
    rows_seen = 0
    detail_aggregate: dict[tuple[object, ...], dict[str, object]] = {}
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
            if key not in detail_aggregate:
                detail_aggregate[key] = {
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
            detail_aggregate[key]["prescription_qty"] += quantity  # type: ignore[operator]
            detail_aggregate[key]["prescription_value_local"] += to_decimal(row.get("value")) or Decimal("0")  # type: ignore[operator]
            detail_aggregate[key]["row_count_aggregated"] += 1  # type: ignore[operator]
    detail_records = list(detail_aggregate.values())
    doctor_month = _doctor_month_summaries(detail_records)
    doctor_brand = _doctor_brand_summaries(detail_records)
    country_brand_month = _country_brand_month_summaries(detail_records)
    online_rows_loaded = len(doctor_month) + len(doctor_brand) + len(country_brand_month)
    source_rows_loaded = sum(int(r["row_count_aggregated"]) for r in detail_records)
    return LoadResult(
        "rcpa",
        rows_seen,
        online_rows_loaded,
        rows_seen - source_rows_loaded,
        doctor_month,
        issues.issues,
        summaries={
            "rcpa_detail_records": detail_records,
            "rcpa_doctor_brand_summary": doctor_brand,
            "rcpa_country_brand_month_summary": country_brand_month,
            "rcpa_detail_record_count": len(detail_records),
            "rcpa_online_record_count": online_rows_loaded,
        },
    )


def _doctor_month_summaries(records: list[dict[str, object]]) -> list[dict[str, object]]:
    summaries: dict[tuple[object, ...], dict[str, object]] = {}
    for record in records:
        key = (
            record["country"],
            record["month_start_date"],
            record["pcode_normalized"],
            record["currency_code"],
        )
        if key not in summaries:
            summaries[key] = {
                "country": record["country"],
                "month_start_date": record["month_start_date"],
                "pcode_raw": record.get("pcode_raw"),
                "pcode_normalized": record["pcode_normalized"],
                "doctor_name": record.get("doctor_name"),
                "speciality": record.get("speciality"),
                "doctor_class": record.get("doctor_class"),
                "patch_name": record.get("patch_name"),
                "active_status": record.get("active_status"),
                "own_prescription_qty": Decimal("0"),
                "own_prescription_value_local": Decimal("0"),
                "competitor_prescription_qty": Decimal("0"),
                "competitor_prescription_value_local": Decimal("0"),
                "total_prescription_qty": Decimal("0"),
                "total_prescription_value_local": Decimal("0"),
                "currency_code": record["currency_code"],
                "row_count_aggregated": 0,
            }
        summary = summaries[key]
        qty = _decimal(record.get("prescription_qty"))
        value = _decimal(record.get("prescription_value_local"))
        owner = _owner_bucket(record.get("own_or_competitor"))
        if owner == "own":
            summary["own_prescription_qty"] += qty  # type: ignore[operator]
            summary["own_prescription_value_local"] += value  # type: ignore[operator]
        elif owner == "competitor":
            summary["competitor_prescription_qty"] += qty  # type: ignore[operator]
            summary["competitor_prescription_value_local"] += value  # type: ignore[operator]
        summary["total_prescription_qty"] += qty  # type: ignore[operator]
        summary["total_prescription_value_local"] += value  # type: ignore[operator]
        summary["row_count_aggregated"] += int(record.get("row_count_aggregated") or 0)  # type: ignore[operator]
    return list(summaries.values())


def _doctor_brand_summaries(records: list[dict[str, object]]) -> list[dict[str, object]]:
    summaries: dict[tuple[object, ...], dict[str, object]] = {}
    for record in records:
        key = (
            record["country"],
            record["pcode_normalized"],
            record["brand_group"],
            _owner_bucket(record.get("own_or_competitor")),
            record["currency_code"],
        )
        if key not in summaries:
            summaries[key] = {
                "country": record["country"],
                "first_month_start_date": record["month_start_date"],
                "last_month_start_date": record["month_start_date"],
                "pcode_normalized": record["pcode_normalized"],
                "doctor_name": record.get("doctor_name"),
                "brand_group": record["brand_group"],
                "own_or_competitor": _owner_bucket(record.get("own_or_competitor")),
                "prescription_qty": Decimal("0"),
                "prescription_value_local": Decimal("0"),
                "currency_code": record["currency_code"],
                "row_count_aggregated": 0,
            }
        summary = summaries[key]
        month_start = record["month_start_date"]
        if month_start < summary["first_month_start_date"]:  # type: ignore[operator]
            summary["first_month_start_date"] = month_start
        if month_start > summary["last_month_start_date"]:  # type: ignore[operator]
            summary["last_month_start_date"] = month_start
        summary["prescription_qty"] += _decimal(record.get("prescription_qty"))  # type: ignore[operator]
        summary["prescription_value_local"] += _decimal(record.get("prescription_value_local"))  # type: ignore[operator]
        summary["row_count_aggregated"] += int(record.get("row_count_aggregated") or 0)  # type: ignore[operator]
    return list(summaries.values())


def _country_brand_month_summaries(records: list[dict[str, object]]) -> list[dict[str, object]]:
    summaries: dict[tuple[object, ...], dict[str, object]] = {}
    for record in records:
        key = (
            record["country"],
            record["month_start_date"],
            record["brand_group"],
            _owner_bucket(record.get("own_or_competitor")),
            record["currency_code"],
        )
        if key not in summaries:
            summaries[key] = {
                "country": record["country"],
                "month_start_date": record["month_start_date"],
                "brand_group": record["brand_group"],
                "own_or_competitor": _owner_bucket(record.get("own_or_competitor")),
                "prescription_qty": Decimal("0"),
                "prescription_value_local": Decimal("0"),
                "currency_code": record["currency_code"],
                "row_count_aggregated": 0,
            }
        summary = summaries[key]
        summary["prescription_qty"] += _decimal(record.get("prescription_qty"))  # type: ignore[operator]
        summary["prescription_value_local"] += _decimal(record.get("prescription_value_local"))  # type: ignore[operator]
        summary["row_count_aggregated"] += int(record.get("row_count_aggregated") or 0)  # type: ignore[operator]
    return list(summaries.values())


def _owner_bucket(value: object) -> str:
    text = _text(value)
    if not text:
        return "unknown"
    normalized = text.lower()
    if normalized in {"own", "cipla"} or "own" in normalized:
        return "own"
    if normalized in {"competitor", "comp"} or "competitor" in normalized:
        return "competitor"
    return normalized


def _decimal(value: object) -> Decimal:
    if isinstance(value, Decimal):
        return value
    return to_decimal(value) or Decimal("0")


def _text(value: object) -> str | None:
    if value is None:
        return None
    text = str(value).strip()
    return text or None
