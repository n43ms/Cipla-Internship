from __future__ import annotations

import csv
import gzip
import re
from datetime import date
from decimal import Decimal
from pathlib import Path
from typing import Any

from ingestion.models import WorkbookProfile

RCPA_DETAIL_FIELDS = [
    "country",
    "month_start_date",
    "pcode_raw",
    "pcode_normalized",
    "doctor_name",
    "speciality",
    "doctor_class",
    "patch_name",
    "active_status",
    "brand_group",
    "sku",
    "sku_detail",
    "own_or_competitor",
    "prescription_qty",
    "prescription_value_local",
    "currency_code",
    "prescription_value_usd",
    "row_count_aggregated",
]


def export_rcpa_detail_records(
    *, profile: WorkbookProfile, records: list[dict[str, Any]], processed_dir: Path
) -> Path | None:
    if not records:
        return None
    processed_dir.mkdir(parents=True, exist_ok=True)
    output_path = processed_dir / f"rcpa_detail_{_safe_stem(profile.original_filename)}_{profile.file_hash[:12]}.csv.gz"
    with gzip.open(output_path, "wt", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=RCPA_DETAIL_FIELDS, extrasaction="ignore")
        writer.writeheader()
        for record in records:
            writer.writerow({field: _serialize(record.get(field)) for field in RCPA_DETAIL_FIELDS})
    return output_path


def _safe_stem(filename: str) -> str:
    stem = Path(filename).stem.lower()
    stem = re.sub(r"[^a-z0-9]+", "_", stem).strip("_")
    return stem[:80] or "workbook"


def _serialize(value: object) -> object:
    if isinstance(value, date):
        return value.isoformat()
    if isinstance(value, Decimal):
        return str(value)
    return value
