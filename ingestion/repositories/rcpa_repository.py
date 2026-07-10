from __future__ import annotations

from typing import Any

from sqlalchemy import text

from ingestion.repositories.canonical_repository import BATCH_SIZE, CanonicalRepository


class RcpaRepository(CanonicalRepository):
    def replace_rcpa_doctor_month_summaries(
        self, *, ingestion_run_id: str, source_file_id: str, records: list[dict[str, Any]]
    ) -> None:
        self.session.execute(
            text("delete from rcpa_doctor_month_summary where source_file_id = :source_file_id"),
            {"source_file_id": source_file_id},
        )
        if not records:
            return
        statement = text(
            """
            insert into rcpa_doctor_month_summary (
                source_file_id, ingestion_run_id, country_id, calendar_month_id, pcode_raw,
                pcode_normalized, doctor_name, speciality, doctor_class, patch_name,
                territory_name, active_status,
                mapping_provenance, mapping_note, source_mapping_method, competitor_filter_note,
                own_prescription_qty, own_prescription_value_local,
                competitor_prescription_qty, competitor_prescription_value_local,
                total_prescription_qty, total_prescription_value_local, currency_code,
                row_count_aggregated
            )
            values (
                :source_file_id, :ingestion_run_id, :country_id, :calendar_month_id, :pcode_raw,
                :pcode_normalized, :doctor_name, :speciality, :doctor_class, :patch_name,
                :territory_name, :active_status,
                :mapping_provenance, :mapping_note, :source_mapping_method, :competitor_filter_note,
                :own_prescription_qty, :own_prescription_value_local,
                :competitor_prescription_qty, :competitor_prescription_value_local,
                :total_prescription_qty, :total_prescription_value_local, :currency_code,
                :row_count_aggregated
            )
            on conflict (
                source_file_id, country_id, calendar_month_id, pcode_normalized, currency_code
            ) do update
            set
                ingestion_run_id = excluded.ingestion_run_id,
                doctor_name = excluded.doctor_name,
                speciality = excluded.speciality,
                doctor_class = excluded.doctor_class,
                patch_name = excluded.patch_name,
                territory_name = excluded.territory_name,
                active_status = excluded.active_status,
                mapping_provenance = excluded.mapping_provenance,
                mapping_note = excluded.mapping_note,
                source_mapping_method = excluded.source_mapping_method,
                competitor_filter_note = excluded.competitor_filter_note,
                own_prescription_qty = excluded.own_prescription_qty,
                own_prescription_value_local = excluded.own_prescription_value_local,
                competitor_prescription_qty = excluded.competitor_prescription_qty,
                competitor_prescription_value_local = excluded.competitor_prescription_value_local,
                total_prescription_qty = excluded.total_prescription_qty,
                total_prescription_value_local = excluded.total_prescription_value_local,
                row_count_aggregated = excluded.row_count_aggregated
            """
        )
        rows = self._rows_with_ids(ingestion_run_id, source_file_id, records)
        for batch in _chunks(rows):
            self.session.execute(statement, batch)

    def replace_rcpa_doctor_brand_summaries(
        self, *, ingestion_run_id: str, source_file_id: str, records: list[dict[str, Any]]
    ) -> None:
        self.session.execute(
            text("delete from rcpa_doctor_brand_summary where source_file_id = :source_file_id"),
            {"source_file_id": source_file_id},
        )
        if not records:
            return
        statement = text(
            """
            insert into rcpa_doctor_brand_summary (
                source_file_id, ingestion_run_id, country_id, first_calendar_month_id,
                last_calendar_month_id, pcode_normalized, doctor_name, brand_group,
                own_or_competitor, prescription_qty, prescription_value_local, currency_code,
                row_count_aggregated
            )
            values (
                :source_file_id, :ingestion_run_id, :country_id, :first_calendar_month_id,
                :last_calendar_month_id, :pcode_normalized, :doctor_name, :brand_group,
                :own_or_competitor, :prescription_qty, :prescription_value_local, :currency_code,
                :row_count_aggregated
            )
            on conflict (
                source_file_id,
                country_id,
                pcode_normalized,
                brand_group,
                own_or_competitor,
                currency_code
            ) do update
            set
                ingestion_run_id = excluded.ingestion_run_id,
                first_calendar_month_id = excluded.first_calendar_month_id,
                last_calendar_month_id = excluded.last_calendar_month_id,
                doctor_name = excluded.doctor_name,
                prescription_qty = excluded.prescription_qty,
                prescription_value_local = excluded.prescription_value_local,
                row_count_aggregated = excluded.row_count_aggregated
            """
        )
        rows = [
            {
                **record,
                "ingestion_run_id": ingestion_run_id,
                "source_file_id": source_file_id,
                "country_id": self.country_id(str(record["country"])),
                "first_calendar_month_id": self.month_id(record["first_month_start_date"]),
                "last_calendar_month_id": self.month_id(record["last_month_start_date"]),
            }
            for record in records
        ]
        for batch in _chunks(rows):
            self.session.execute(statement, batch)

    def replace_rcpa_country_brand_month_summaries(
        self, *, ingestion_run_id: str, source_file_id: str, records: list[dict[str, Any]]
    ) -> None:
        self.session.execute(
            text(
                """
                delete from rcpa_country_brand_month_summary
                where source_file_id = :source_file_id
                """
            ),
            {"source_file_id": source_file_id},
        )
        if not records:
            return
        statement = text(
            """
            insert into rcpa_country_brand_month_summary (
                source_file_id, ingestion_run_id, country_id, calendar_month_id, brand_group,
                own_or_competitor, prescription_qty, prescription_value_local, currency_code,
                row_count_aggregated
            )
            values (
                :source_file_id, :ingestion_run_id, :country_id, :calendar_month_id, :brand_group,
                :own_or_competitor, :prescription_qty, :prescription_value_local, :currency_code,
                :row_count_aggregated
            )
            on conflict (
                source_file_id,
                country_id,
                calendar_month_id,
                brand_group,
                own_or_competitor,
                currency_code
            ) do update
            set
                ingestion_run_id = excluded.ingestion_run_id,
                prescription_qty = excluded.prescription_qty,
                prescription_value_local = excluded.prescription_value_local,
                row_count_aggregated = excluded.row_count_aggregated
            """
        )
        rows = self._rows_with_ids(ingestion_run_id, source_file_id, records)
        for batch in _chunks(rows):
            self.session.execute(statement, batch)

    def upsert_doctors_from_rcpa(self, records: list[dict[str, Any]]) -> None:
        rows_by_key: dict[tuple[str, str], dict[str, Any]] = {}
        for record in records:
            key = (str(record["country"]), str(record["pcode_normalized"]))
            month_start_date = record.get("month_start_date")
            rows_by_key[key] = {
                "country_id": self.country_id(str(record["country"])),
                "calendar_month_id": (
                    self.month_id(month_start_date) if month_start_date is not None else None
                ),
                "pcode_normalized": record["pcode_normalized"],
                "latest_doctor_name": record.get("doctor_name"),
                "speciality": record.get("speciality"),
                "doctor_class": record.get("doctor_class"),
                "patch_name": record.get("patch_name"),
                "active_status": record.get("active_status"),
                "source_count": 1,
            }
        if not rows_by_key:
            return
        statement = text(
            """
            insert into doctors (
                country_id,
                pcode_normalized,
                latest_doctor_name,
                speciality,
                doctor_class,
                patch_name,
                active_status, first_seen_month_id, last_seen_month_id, source_count, updated_at
            )
            values (
                :country_id,
                :pcode_normalized,
                :latest_doctor_name,
                :speciality,
                :doctor_class,
                :patch_name,
                :active_status, :calendar_month_id, :calendar_month_id, :source_count, now()
            )
            on conflict (country_id, pcode_normalized) do update
            set
                latest_doctor_name = coalesce(
                    excluded.latest_doctor_name,
                    doctors.latest_doctor_name
                ),
                speciality = coalesce(excluded.speciality, doctors.speciality),
                doctor_class = coalesce(excluded.doctor_class, doctors.doctor_class),
                patch_name = coalesce(excluded.patch_name, doctors.patch_name),
                active_status = coalesce(excluded.active_status, doctors.active_status),
                first_seen_month_id = coalesce(
                    doctors.first_seen_month_id,
                    excluded.first_seen_month_id
                ),
                last_seen_month_id = coalesce(
                    excluded.last_seen_month_id,
                    doctors.last_seen_month_id
                ),
                source_count = doctors.source_count + 1,
                updated_at = now()
            """
        )
        for batch in _chunks(list(rows_by_key.values())):
            self.session.execute(statement, batch)

    def _rows_with_ids(
        self, ingestion_run_id: str, source_file_id: str, records: list[dict[str, Any]]
    ) -> list[dict[str, Any]]:
        return [
            {
                **record,
                "ingestion_run_id": ingestion_run_id,
                "source_file_id": source_file_id,
                "country_id": self.country_id(str(record["country"])),
                "calendar_month_id": self.month_id(record["month_start_date"]),
            }
            for record in records
        ]


def _chunks(rows: list[dict[str, Any]], size: int = BATCH_SIZE) -> list[list[dict[str, Any]]]:
    return [rows[index : index + size] for index in range(0, len(rows), size)]
