from __future__ import annotations

from typing import Any

from sqlalchemy import text
from sqlalchemy.orm import Session


class DataQualityRepository:
    def __init__(self, session: Session) -> None:
        self.session = session

    def summary(self) -> dict[str, Any] | None:
        row = self.session.execute(text("select * from mv_data_quality limit 1")).mappings().first()
        return dict(row) if row else None

    def latest_ingestion(self) -> dict[str, Any] | None:
        row = self.session.execute(
            text(
                """
                select *
                from ingestion_runs
                order by started_at desc
                limit 1
                """
            )
        ).mappings().first()
        return dict(row) if row else None

    def validation_issues(self, limit: int = 25) -> list[dict[str, Any]]:
        rows = self.session.execute(
            text(
                """
                select
                    ve.severity,
                    sf.original_filename as source_file,
                    ve.sheet_name,
                    ve.row_number,
                    ve.entity_type,
                    ve.field_name,
                    ve.error_code,
                    ve.message
                from validation_errors ve
                left join source_files sf on sf.id = ve.source_file_id
                where ve.ingestion_run_id in (
                    select id from ingestion_runs order by started_at desc limit 5
                )
                order by
                    case ve.severity when 'error' then 1 when 'warning' then 2 else 3 end,
                    sf.original_filename,
                    ve.row_number nulls last
                limit :limit
                """
            ),
            {"limit": limit},
        ).mappings()
        return [dict(row) for row in rows]

    def filters(self) -> dict[str, Any]:
        countries = self.session.execute(
            text("select code as value, name as label from countries order by name")
        ).mappings()
        months = self.session.execute(
            text(
                """
                select distinct to_char(month_start_date, 'YYYY-MM') as value, month_label as label
                from calendar_months
                where id in (
                    select calendar_month_id from plan_events
                    union select calendar_month_id from execution_requests
                    union select calendar_month_id from execution_snapshots
                )
                order by value desc
                """
            )
        ).mappings()
        intervention_types = self.session.execute(
            text(
                """
                select distinct intervention_type as value, intervention_type as label
                from execution_requests
                where intervention_type is not null and btrim(intervention_type) <> ''
                order by intervention_type
                """
            )
        ).mappings()
        specialities = self.session.execute(
            text(
                """
                select distinct speciality as value, speciality as label
                from mv_doctor_roi
                where speciality is not null and btrim(speciality) <> ''
                order by speciality
                limit 100
                """
            )
        ).mappings()
        doctor_classes = self.session.execute(
            text(
                """
                select distinct doctor_class as value, doctor_class as label
                from mv_doctor_roi
                where doctor_class is not null and btrim(doctor_class) <> ''
                order by doctor_class
                """
            )
        ).mappings()
        roi_segments = self.session.execute(
            text(
                """
                select distinct roi_segment as value, replace(roi_segment, '_', ' ') as label
                from mv_doctor_roi
                order by roi_segment
                """
            )
        ).mappings()
        latest = self.latest_ingestion()
        return {
            "countries": [dict(row) for row in countries],
            "months": [dict(row) for row in months],
            "intervention_types": [dict(row) for row in intervention_types],
            "specialities": [dict(row) for row in specialities],
            "doctor_classes": [dict(row) for row in doctor_classes],
            "roi_segments": [dict(row) for row in roi_segments],
            "latest_ingestion_status": str(latest["status"]) if latest else "unknown",
        }
