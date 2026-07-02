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
                with latest_file_runs as (
                    select distinct on (irf.source_file_id)
                        irf.source_file_id,
                        irf.ingestion_run_id
                    from ingestion_run_files irf
                    join ingestion_runs ir on ir.id = irf.ingestion_run_id
                    order by irf.source_file_id, ir.started_at desc
                )
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
                join latest_file_runs lfr
                  on lfr.source_file_id = ve.source_file_id
                 and lfr.ingestion_run_id = ve.ingestion_run_id
                left join source_files sf on sf.id = ve.source_file_id
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

    def source_file_quality(self) -> list[dict[str, Any]]:
        rows = self.session.execute(
            text(
                """
                select distinct on (sf.id)
                    sf.original_filename as source_file,
                    sf.source_type,
                    irf.status,
                    coalesce(irf.rows_seen, 0)::integer as rows_seen,
                    coalesce(irf.rows_loaded, 0)::integer as rows_loaded,
                    coalesce(irf.rows_skipped, 0)::integer as rows_skipped,
                    coalesce(irf.warnings, 0)::integer as warning_count,
                    coalesce(irf.errors, 0)::integer as error_count,
                    sf.period_start::text,
                    sf.period_end::text,
                    case
                        when sf.source_type = 'rcpa' then 'compact_online_summary'
                        else 'canonical_rows'
                    end as storage_mode,
                    case
                        when sf.source_type = 'rcpa'
                            then 'Rows loaded are compact online RCPA summary rows; raw prescription detail is represented in local detail extracts.'
                        else null
                    end as row_count_note
                from source_files sf
                left join ingestion_run_files irf on irf.source_file_id = sf.id
                left join ingestion_runs ir on ir.id = irf.ingestion_run_id
                order by sf.id, ir.started_at desc nulls last, sf.original_filename
                """
            )
        ).mappings()
        return [dict(row) for row in rows]

    def unmatched_by_source(self) -> list[dict[str, Any]]:
        rows = self.session.execute(
            text(
                """
                select
                    source_type,
                    coalesce(unmatched_reason_code, 'unknown') as reason_code,
                    count(*)::integer as record_count
                from mv_unmatched_events
                where is_primary_phase4_scope
                group by source_type, coalesce(unmatched_reason_code, 'unknown')
                order by record_count desc, source_type, reason_code
                """
            )
        ).mappings()
        return [dict(row) for row in rows]

    def unmatched_records(self, limit: int = 50) -> list[dict[str, Any]]:
        return self.unmatched_records_page(page=1, page_size=limit)[1]

    def unmatched_records_page(
        self,
        *,
        page: int = 1,
        page_size: int = 50,
        country: str | None = None,
        month: str | None = None,
        source_type: str | None = None,
        reason_code: str | None = None,
    ) -> tuple[int, list[dict[str, Any]]]:
        offset = max(page - 1, 0) * page_size
        params = {
            "country": country,
            "month": month,
            "source_type": source_type,
            "reason_code": reason_code,
            "limit": page_size,
            "offset": offset,
        }
        where = """
            where is_primary_phase4_scope
              and (
                cast(:country as text) is null
                or lower(country_code) = lower(cast(:country as text))
                or lower(country_name) = lower(cast(:country as text))
              )
              and (
                cast(:month as text) is null
                or to_char(month_start_date, 'YYYY-MM') = cast(:month as text)
              )
              and (cast(:source_type as text) is null or source_type = cast(:source_type as text))
              and (cast(:reason_code as text) is null or unmatched_reason_code = cast(:reason_code as text))
        """
        total = self.session.execute(text(f"select count(*)::integer from mv_unmatched_events {where}"), params).scalar_one()
        rows = self.session.execute(
            text(
                f"""
                select
                    source_type,
                    country_name as country,
                    month_label as month,
                    event_name,
                    event_type,
                    unmatched_reason_code as reason_code,
                    unmatched_reason_detail as reason_detail,
                    candidate_match,
                    confidence
                from mv_unmatched_events
                {where}
                order by country_name, month_start_date, source_type, event_name
                limit :limit
                offset :offset
                """
            ),
            params,
        ).mappings()
        return int(total or 0), [dict(row) for row in rows]

    def fx_quality(self) -> list[dict[str, Any]]:
        rows = self.session.execute(
            text(
                """
                select
                    er.currency_code,
                    er.fx_rate_status as rate_status,
                    max(er.fx_rate_to_usd) as rate_to_usd,
                    max(er.fx_rate_date)::text as rate_date,
                    max(er.fx_rate_source) as source,
                    count(*)::integer as row_count
                from execution_requests er
                group by er.currency_code, er.fx_rate_status
                union all
                select
                    ex.currency_code,
                    ex.rate_status,
                    ex.rate_to_usd,
                    ex.rate_date::text,
                    ex.source,
                    0::integer as row_count
                from exchange_rates ex
                where not exists (
                    select 1
                    from execution_requests er
                    where er.currency_code = ex.currency_code
                      and er.fx_rate_status = ex.rate_status
                )
                order by currency_code, rate_status
                """
            )
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
        brands = self.session.execute(
            text(
                """
                select distinct brand_group as value, brand_group as label
                from rcpa_doctor_brand_summary
                where brand_group is not null and btrim(brand_group) <> ''
                order by brand_group
                limit 150
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
            "brands": [dict(row) for row in brands],
            "roi_segments": [dict(row) for row in roi_segments],
            "latest_ingestion_status": str(latest["status"]) if latest else "unknown",
        }
