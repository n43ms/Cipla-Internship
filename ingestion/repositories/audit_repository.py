from __future__ import annotations

from typing import Any

from sqlalchemy import text
from sqlalchemy.orm import Session

from ingestion.models import SourceFile, ValidationIssue, WorkbookProfile


class AuditRepository:
    def __init__(self, session: Session) -> None:
        self.session = session

    def create_run(self, *, triggered_by: str = "local_cli") -> str:
        return str(
            self.session.execute(
                text(
                    """
                    insert into ingestion_runs (status, triggered_by)
                    values ('running', :triggered_by)
                    returning id
                    """
                ),
                {"triggered_by": triggered_by},
            ).scalar_one()
        )

    def upsert_source_file(self, source_file: SourceFile, profile: WorkbookProfile | None = None) -> str:
        source_type = profile.source_type if profile else source_file.source_type
        detected_sheet_count = profile.detected_sheet_count if profile else 0
        country_scope = profile.country_scope if profile else source_file.country_scope
        return str(
            self.session.execute(
                text(
                    """
                    insert into source_files (
                        original_filename,
                        file_hash,
                        file_type,
                        source_type,
                        country_scope,
                        period_start,
                        period_end,
                        detected_sheet_count
                    )
                    values (
                        :original_filename,
                        :file_hash,
                        :file_type,
                        :source_type,
                        :country_scope,
                        :period_start,
                        :period_end,
                        :detected_sheet_count
                    )
                    on conflict (file_hash) do update
                    set
                        source_type = excluded.source_type,
                        country_scope = excluded.country_scope,
                        detected_sheet_count = excluded.detected_sheet_count
                    returning id
                    """
                ),
                {
                    "original_filename": source_file.original_filename,
                    "file_hash": source_file.file_hash,
                    "file_type": source_file.file_type,
                    "source_type": source_type,
                    "country_scope": country_scope,
                    "period_start": source_file.period_start,
                    "period_end": source_file.period_end,
                    "detected_sheet_count": detected_sheet_count,
                },
            ).scalar_one()
        )

    def upsert_run_file(
        self,
        *,
        ingestion_run_id: str,
        source_file_id: str,
        profile: WorkbookProfile,
        status: str,
        rows_seen: int,
        rows_loaded: int,
        rows_skipped: int,
        warnings: int,
        errors: int,
    ) -> str:
        return str(
            self.session.execute(
                text(
                    """
                    insert into ingestion_run_files (
                        ingestion_run_id,
                        source_file_id,
                        local_path_snapshot,
                        status,
                        sheets_profiled,
                        rows_seen,
                        rows_loaded,
                        rows_skipped,
                        warnings,
                        errors,
                        profile_json
                    )
                    values (
                        :ingestion_run_id,
                        :source_file_id,
                        :local_path_snapshot,
                        :status,
                        :sheets_profiled,
                        :rows_seen,
                        :rows_loaded,
                        :rows_skipped,
                        :warnings,
                        :errors,
                        cast(:profile_json as json)
                    )
                    on conflict (ingestion_run_id, source_file_id) do update
                    set
                        status = excluded.status,
                        sheets_profiled = excluded.sheets_profiled,
                        rows_seen = excluded.rows_seen,
                        rows_loaded = excluded.rows_loaded,
                        rows_skipped = excluded.rows_skipped,
                        warnings = excluded.warnings,
                        errors = excluded.errors,
                        profile_json = excluded.profile_json
                    returning id
                    """
                ),
                {
                    "ingestion_run_id": ingestion_run_id,
                    "source_file_id": source_file_id,
                    "local_path_snapshot": str(profile.path),
                    "status": status,
                    "sheets_profiled": profile.detected_sheet_count,
                    "rows_seen": rows_seen,
                    "rows_loaded": rows_loaded,
                    "rows_skipped": rows_skipped,
                    "warnings": warnings,
                    "errors": errors,
                    "profile_json": _json(profile.to_json()),
                },
            ).scalar_one()
        )

    def insert_validation_issues(
        self,
        *,
        ingestion_run_id: str,
        source_file_id: str | None,
        issues: list[ValidationIssue],
    ) -> None:
        if not issues:
            return
        self.session.execute(
            text(
                """
                insert into validation_errors (
                    ingestion_run_id,
                    source_file_id,
                    sheet_name,
                    row_number,
                    severity,
                    entity_type,
                    field_name,
                    error_code,
                    message,
                    raw_value
                )
                values (
                    :ingestion_run_id,
                    :source_file_id,
                    :sheet_name,
                    :row_number,
                    :severity,
                    :entity_type,
                    :field_name,
                    :error_code,
                    :message,
                    :raw_value
                )
                """
            ),
            [
                {
                    "ingestion_run_id": ingestion_run_id,
                    "source_file_id": source_file_id,
                    "sheet_name": issue.sheet_name,
                    "row_number": issue.row_number,
                    "severity": issue.severity,
                    "entity_type": issue.entity_type,
                    "field_name": issue.field_name,
                    "error_code": issue.error_code,
                    "message": issue.message,
                    "raw_value": issue.raw_value,
                }
                for issue in issues
            ],
        )

    def complete_run(
        self,
        *,
        ingestion_run_id: str,
        status: str,
        source_file_count: int,
        total_rows_seen: int,
        total_rows_loaded: int,
        total_rows_skipped: int,
        warning_count: int,
        error_count: int,
        summary_json: dict[str, Any],
    ) -> None:
        self.session.execute(
            text(
                """
                update ingestion_runs
                set
                    completed_at = now(),
                    status = :status,
                    source_file_count = :source_file_count,
                    total_rows_seen = :total_rows_seen,
                    total_rows_loaded = :total_rows_loaded,
                    total_rows_skipped = :total_rows_skipped,
                    warning_count = :warning_count,
                    error_count = :error_count,
                    summary_json = cast(:summary_json as json)
                where id = :ingestion_run_id
                """
            ),
            {
                "ingestion_run_id": ingestion_run_id,
                "status": status,
                "source_file_count": source_file_count,
                "total_rows_seen": total_rows_seen,
                "total_rows_loaded": total_rows_loaded,
                "total_rows_skipped": total_rows_skipped,
                "warning_count": warning_count,
                "error_count": error_count,
                "summary_json": _json(summary_json),
            },
        )

    def update_source_file_period_from_canonical(self, source_file_id: str) -> None:
        self.session.execute(
            text(
                """
                with file_periods as (
                    select min(month_start_date) as period_start, max(month_start_date) as period_end
                    from (
                        select cm.month_start_date
                        from plan_events pe
                        join calendar_months cm on cm.id = pe.calendar_month_id
                        where pe.source_file_id = :source_file_id
                        union all
                        select cm.month_start_date
                        from execution_snapshots es
                        join calendar_months cm on cm.id = es.calendar_month_id
                        where es.source_file_id = :source_file_id
                        union all
                        select cm.month_start_date
                        from execution_requests er
                        join calendar_months cm on cm.id = er.calendar_month_id
                        where er.source_file_id = :source_file_id
                        union all
                        select cm.month_start_date
                        from doctor_engagement_facts def
                        join calendar_months cm on cm.id = def.calendar_month_id
                        where def.source_file_id = :source_file_id
                        union all
                        select cm.month_start_date
                        from rcpa_doctor_month_summary rdm
                        join calendar_months cm on cm.id = rdm.calendar_month_id
                        where rdm.source_file_id = :source_file_id
                        union all
                        select cm.month_start_date
                        from rcpa_country_brand_month_summary rcb
                        join calendar_months cm on cm.id = rcb.calendar_month_id
                        where rcb.source_file_id = :source_file_id
                        union all
                        select cm.month_start_date
                        from rcpa_doctor_brand_summary rdb
                        join calendar_months cm on cm.id = rdb.first_calendar_month_id
                        where rdb.source_file_id = :source_file_id
                        union all
                        select cm.month_start_date
                        from rcpa_doctor_brand_summary rdb
                        join calendar_months cm on cm.id = rdb.last_calendar_month_id
                        where rdb.source_file_id = :source_file_id
                    ) months
                )
                update source_files sf
                set period_start = fp.period_start,
                    period_end = fp.period_end
                from file_periods fp
                where sf.id = :source_file_id
                  and fp.period_start is not null
                """
            ),
            {"source_file_id": source_file_id},
        )


def _json(value: Any) -> str:
    import json

    return json.dumps(value, default=str)
