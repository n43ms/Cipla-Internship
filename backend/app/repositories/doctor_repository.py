from __future__ import annotations

from typing import Any

from sqlalchemy import text
from sqlalchemy.orm import Session

from backend.app.repositories.base import pagination


class DoctorRepository:
    def __init__(self, session: Session) -> None:
        self.session = session

    def roi_rows(
        self,
        country: str | None,
        segment: str | None,
        quadrant: str | None,
        page: int,
        page_size: int,
    ) -> tuple[int, list[dict[str, Any]], dict[str, int], dict[str, int]]:
        limit, offset = pagination(page, page_size)
        params = {
            "country": country,
            "segment": segment,
            "quadrant": quadrant,
            "limit": limit,
            "offset": offset,
        }
        where = """
            where (
                cast(:country as text) is null
                or lower(country_code) = lower(cast(:country as text))
                or lower(country_name) = lower(cast(:country as text))
            )
            and (cast(:segment as text) is null or roi_segment = cast(:segment as text))
            and (cast(:quadrant as text) is null or quadrant_label = cast(:quadrant as text))
        """
        total = int(self.session.execute(text(f"select count(*) from mv_doctor_roi {where}"), params).scalar_one())
        rows = self.session.execute(
            text(
                f"""
                select *
                from mv_doctor_roi
                {where}
                order by
                    dark_horse_flag desc,
                    cipla_prescription_qty desc,
                    total_roi_spend_usd desc,
                    doctor_name nulls last,
                    pcode_normalized
                limit :limit offset :offset
                """
            ),
            params,
        ).mappings()
        quadrant_rows = self.session.execute(
            text(
                """
                select quadrant_label, count(*)::integer as count
                from mv_doctor_roi
                where (
                    cast(:country as text) is null
                    or lower(country_code) = lower(cast(:country as text))
                    or lower(country_name) = lower(cast(:country as text))
                )
                group by quadrant_label
                """
            ),
            params,
        ).mappings()
        segment_rows = self.session.execute(
            text(
                """
                select roi_segment, count(*)::integer as count
                from mv_doctor_roi
                where (
                    cast(:country as text) is null
                    or lower(country_code) = lower(cast(:country as text))
                    or lower(country_name) = lower(cast(:country as text))
                )
                group by roi_segment
                """
            ),
            params,
        ).mappings()
        return (
            total,
            [dict(row) for row in rows],
            {str(row["quadrant_label"]): int(row["count"]) for row in quadrant_rows},
            {str(row["roi_segment"]): int(row["count"]) for row in segment_rows},
        )

    def doctor_profile(self, country_code: str, pcode: str) -> dict[str, Any] | None:
        row = self.session.execute(
            text(
                """
                select *
                from mv_doctor_roi
                where lower(country_code) = lower(:country_code)
                  and pcode_normalized = :pcode
                limit 1
                """
            ),
            {"country_code": country_code, "pcode": pcode},
        ).mappings().first()
        return dict(row) if row else None

    def engagement_history(self, country_code: str, pcode: str) -> list[dict[str, Any]]:
        rows = self.session.execute(
            text(
                """
                select
                    er.req_id as request_id,
                    er.intervention_name,
                    er.intervention_type,
                    cm.month_label as month,
                    er.actual_intervention_date,
                    er.total_roi_spend_usd,
                    er.fx_rate_status
                from request_doctors rd
                join execution_requests er on er.id = rd.execution_request_id
                join countries c on c.id = er.country_id
                join calendar_months cm on cm.id = er.calendar_month_id
                where lower(c.code) = lower(:country_code)
                  and rd.pcode_normalized = :pcode
                  and rd.attendance_type = 'actual'
                order by cm.month_start_date desc, er.actual_intervention_date desc nulls last
                limit 50
                """
            ),
            {"country_code": country_code, "pcode": pcode},
        ).mappings()
        return [dict(row) for row in rows]

    def prescription_trend(self, country_code: str, pcode: str) -> list[dict[str, Any]]:
        rows = self.session.execute(
            text(
                """
                select
                    cm.month_label as month,
                    own_prescription_qty as cipla_prescription_qty,
                    competitor_prescription_qty,
                    total_prescription_qty
                from rcpa_doctor_month_summary rdms
                join countries c on c.id = rdms.country_id
                join calendar_months cm on cm.id = rdms.calendar_month_id
                where lower(c.code) = lower(:country_code)
                  and rdms.pcode_normalized = :pcode
                order by cm.month_start_date
                """
            ),
            {"country_code": country_code, "pcode": pcode},
        ).mappings()
        return [dict(row) for row in rows]

    def brand_mix(self, country_code: str, pcode: str) -> list[dict[str, Any]]:
        rows = self.session.execute(
            text(
                """
                select brand_group, own_or_competitor, prescription_qty, prescription_value_local
                from rcpa_doctor_brand_summary rdbs
                join countries c on c.id = rdbs.country_id
                where lower(c.code) = lower(:country_code)
                  and rdbs.pcode_normalized = :pcode
                order by prescription_qty desc nulls last
                limit 50
                """
            ),
            {"country_code": country_code, "pcode": pcode},
        ).mappings()
        return [dict(row) for row in rows]
