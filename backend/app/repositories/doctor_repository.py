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
        roi_segment: str | None,
        quadrant: str | None,
        month_start: str | None,
        month_end: str | None,
        brand: str | None,
        speciality: str | None,
        doctor_class: str | None,
        include_out_of_scope: bool,
        page: int,
        page_size: int,
        sort: str = "darkHorse",
        sort_direction: str = "desc",
    ) -> tuple[int, list[dict[str, Any]], dict[str, int], dict[str, int], dict[str, int]]:
        limit, offset = pagination(page, page_size)
        order_by = _doctor_order_by(sort, sort_direction)
        params = {
            "country": country,
            "roi_segment": roi_segment,
            "quadrant": quadrant,
            "month_start": month_start,
            "month_end": month_end,
            "brand": brand,
            "speciality": speciality,
            "doctor_class": doctor_class,
            "include_out_of_scope": include_out_of_scope,
            "limit": limit,
            "offset": offset,
        }
        where = """
            where (
                cast(:country as text) is null
                or lower(country_code) = lower(cast(:country as text))
                or lower(country_name) = lower(cast(:country as text))
            )
            and (cast(:roi_segment as text) is null or roi_segment = cast(:roi_segment as text))
            and (cast(:quadrant as text) is null or quadrant_label = cast(:quadrant as text))
            and (
                cast(:month_start as text) is null
                or last_engagement_date is null
                or last_engagement_date >= to_date(cast(:month_start as text), 'YYYY-MM')
            )
            and (
                cast(:month_end as text) is null
                or first_engagement_date is null
                or first_engagement_date < (
                    to_date(cast(:month_end as text), 'YYYY-MM') + interval '1 month'
                )
            )
            and (
                cast(:speciality as text) is null
                or lower(speciality) = lower(cast(:speciality as text))
            )
            and (
                cast(:doctor_class as text) is null
                or lower(doctor_class) = lower(cast(:doctor_class as text))
            )
            and (
                cast(:include_out_of_scope as boolean)
                or cast(:country as text) is not null
                or country_code in ('NP', 'LK')
            )
            and (
                cast(:brand as text) is null
                or exists (
                    select 1
                    from rcpa_doctor_brand_summary rdbs
                    join countries bc on bc.id = rdbs.country_id
                    where lower(bc.code) = lower(mv_doctor_roi.country_code)
                      and rdbs.pcode_normalized = mv_doctor_roi.pcode_normalized
                      and lower(rdbs.brand_group) = lower(cast(:brand as text))
                )
            )
        """
        total = int(
            self.session.execute(
                text(f"select count(*) from mv_doctor_roi {where}"),
                params,
            ).scalar_one()
        )
        rows = self.session.execute(
            text(
                f"""
                select *
                from mv_doctor_roi
                {where}
                order by {order_by}
                limit :limit offset :offset
                """
            ),
            params,
        ).mappings()
        quality = self.session.execute(
            text(
                f"""
                select
                    count(*) filter (where dark_horse_flag)::integer as dark_horse_count,
                    count(*) filter (where not has_rcpa)::integer as no_rcpa_count,
                    count(*) filter (where has_missing_fx)::integer as missing_fx_count,
                    count(*) filter (where has_provisional_fx)::integer as provisional_fx_count
                from mv_doctor_roi
                {where}
                """
            ),
            params,
        ).mappings().first()
        quadrant_rows = self.session.execute(
            text(
                f"""
                select quadrant_label, count(*)::integer as count
                from mv_doctor_roi
                {where}
                group by quadrant_label
                """
            ),
            params,
        ).mappings()
        segment_rows = self.session.execute(
            text(
                f"""
                select roi_segment, count(*)::integer as count
                from mv_doctor_roi
                {where}
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
            dict(quality or {}),
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

    def search_doctors(
        self,
        *,
        country: str | None,
        search: str,
        limit: int = 5,
    ) -> list[dict[str, Any]]:
        normalized = search.strip()
        if not normalized:
            return []
        rows = self.session.execute(
            text(
                """
                select *
                from mv_doctor_roi
                where (
                    cast(:country as text) is null
                    or lower(country_code) = lower(cast(:country as text))
                    or lower(country_name) = lower(cast(:country as text))
                )
                and (
                    lower(pcode_normalized) = lower(cast(:search as text))
                    or lower(coalesce(doctor_name, '')) = lower(cast(:search as text))
                    or lower(coalesce(doctor_name, ''))
                        like '%' || lower(cast(:search as text)) || '%'
                    or (
                        doctor_name is not null
                        and btrim(doctor_name) <> ''
                        and lower(cast(:search as text)) like '%' || lower(doctor_name) || '%'
                    )
                )
                order by
                    case
                        when lower(pcode_normalized) = lower(cast(:search as text)) then 0
                        else 1
                    end,
                    case
                        when lower(coalesce(doctor_name, '')) = lower(cast(:search as text))
                        then 0
                        else 1
                    end,
                    has_rcpa desc,
                    engagement_count desc,
                    cipla_prescription_qty desc,
                    doctor_name nulls last,
                    pcode_normalized
                limit :limit
                """
            ),
            {"country": country, "search": normalized, "limit": max(1, min(limit, 10))},
        ).mappings()
        return [dict(row) for row in rows]

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


def _doctor_order_by(sort: str, direction: str) -> str:
    direction_sql = "asc" if direction.lower() == "asc" else "desc"
    columns = {
        "darkHorse": (
            "dark_horse_flag desc, cipla_prescription_qty desc, total_roi_spend_usd asc, "
            "doctor_name nulls last, pcode_normalized"
        ),
        "doctorName": f"doctor_name {direction_sql} nulls last, pcode_normalized",
        "roiSegment": f"roi_segment {direction_sql}, doctor_name nulls last, pcode_normalized",
        "quadrantLabel": (
            f"quadrant_label {direction_sql}, doctor_name nulls last, pcode_normalized"
        ),
        "ciplaPrescriptionQty": (
            f"cipla_prescription_qty {direction_sql}, doctor_name nulls last, "
            "pcode_normalized"
        ),
        "totalRoiSpendUsd": (
            f"total_roi_spend_usd {direction_sql}, doctor_name nulls last, "
            "pcode_normalized"
        ),
        "rcpaLastMonth": (
            f"rcpa_last_month {direction_sql} nulls last, doctor_name nulls last, "
            "pcode_normalized"
        ),
        "spendPerCiplaPrescriptionUsd": (
            f"spend_per_cipla_prescription_usd {direction_sql} nulls last, "
            "doctor_name nulls last, pcode_normalized"
        ),
        "lastEngagementDate": (
            f"last_engagement_date {direction_sql} nulls last, doctor_name nulls last, "
            "pcode_normalized"
        ),
        "engagementCount": (
            f"engagement_count {direction_sql}, doctor_name nulls last, pcode_normalized"
        ),
    }
    return columns.get(sort, columns["darkHorse"])
