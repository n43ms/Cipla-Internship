from __future__ import annotations

from typing import Any

from sqlalchemy import text
from sqlalchemy.orm import Session

from ingestion.repositories.canonical_repository import CanonicalRepository


class RcpaRepository(CanonicalRepository):
    def upsert_rcpa_aggregates(
        self, *, ingestion_run_id: str, source_file_id: str, records: list[dict[str, Any]]
    ) -> None:
        if not records:
            return
        self.session.execute(
            text(
                """
                insert into rcpa_prescriptions (
                    source_file_id, ingestion_run_id, country_id, calendar_month_id, pcode_raw,
                    pcode_normalized, doctor_name, brand_group, sku, own_or_competitor,
                    prescription_qty, prescription_value_local, currency_code, prescription_value_usd,
                    row_count_aggregated
                )
                values (
                    :source_file_id, :ingestion_run_id, :country_id, :calendar_month_id, :pcode_raw,
                    :pcode_normalized, :doctor_name, :brand_group, :sku, :own_or_competitor,
                    :prescription_qty, :prescription_value_local, :currency_code, :prescription_value_usd,
                    :row_count_aggregated
                )
                on conflict (
                    source_file_id, country_id, calendar_month_id, pcode_normalized,
                    brand_group, sku, own_or_competitor, currency_code
                ) do update
                set
                    ingestion_run_id = excluded.ingestion_run_id,
                    doctor_name = excluded.doctor_name,
                    prescription_qty = excluded.prescription_qty,
                    prescription_value_local = excluded.prescription_value_local,
                    prescription_value_usd = excluded.prescription_value_usd,
                    row_count_aggregated = excluded.row_count_aggregated
                """
            ),
            [
                {
                    **record,
                    "ingestion_run_id": ingestion_run_id,
                    "source_file_id": source_file_id,
                    "country_id": self.country_id(str(record["country"])),
                    "calendar_month_id": self.month_id(record["month_start_date"]),
                }
                for record in records
            ],
        )

    def upsert_doctors_from_rcpa(self, records: list[dict[str, Any]]) -> None:
        rows_by_key: dict[tuple[str, str], dict[str, Any]] = {}
        for record in records:
            key = (str(record["country"]), str(record["pcode_normalized"]))
            rows_by_key[key] = {
                "country_id": self.country_id(str(record["country"])),
                "pcode_normalized": record["pcode_normalized"],
                "latest_doctor_name": record.get("doctor_name"),
                "source_count": 1,
            }
        if not rows_by_key:
            return
        self.session.execute(
            text(
                """
                insert into doctors (
                    country_id, pcode_normalized, latest_doctor_name, source_count, updated_at
                )
                values (
                    :country_id, :pcode_normalized, :latest_doctor_name, :source_count, now()
                )
                on conflict (country_id, pcode_normalized) do update
                set
                    latest_doctor_name = coalesce(excluded.latest_doctor_name, doctors.latest_doctor_name),
                    source_count = doctors.source_count + 1,
                    updated_at = now()
                """
            ),
            list(rows_by_key.values()),
        )
