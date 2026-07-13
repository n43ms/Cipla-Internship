from __future__ import annotations

from typing import Any

from sqlalchemy import text
from sqlalchemy.orm import Session

from backend.app.repositories.base import pagination


class TerritoryRepository:
    def __init__(self, session: Session) -> None:
        self.session = session

    def opportunity_rows(
        self,
        *,
        country: str | None,
        opportunity_label: str | None,
        page: int,
        page_size: int,
        sort_by: str,
        sort_dir: str,
    ) -> tuple[int, list[dict[str, Any]], dict[str, int]]:
        limit, offset = pagination(page, page_size)
        order_clause = _territory_order_clause(sort_by, sort_dir)
        params = {
            "country": country,
            "opportunity_label": opportunity_label,
            "limit": limit,
            "offset": offset,
        }
        where = """
            where (
                cast(:country as text) is null
                or lower(country_code) = lower(cast(:country as text))
                or lower(country_name) = lower(cast(:country as text))
            )
            and (
                cast(:opportunity_label as text) is null
                or opportunity_label = cast(:opportunity_label as text)
            )
        """
        total = int(
            self.session.execute(
                text(f"select count(*) from mv_territory_opportunity {where}"),
                params,
            ).scalar_one()
        )
        rows = self.session.execute(
            text(
                f"""
                select *
                from mv_territory_opportunity
                {where}
                {order_clause}
                limit :limit offset :offset
                """
            ),
            params,
        ).mappings()
        label_rows = self.session.execute(
            text(
                f"""
                select opportunity_label, count(*)::integer as count
                from mv_territory_opportunity
                {where}
                group by opportunity_label
                """
            ),
            params,
        ).mappings()
        return (
            total,
            [dict(row) for row in rows],
            {str(row["opportunity_label"]): int(row["count"]) for row in label_rows},
        )

    def territory_doctors(
        self,
        *,
        country: str,
        territory_name: str,
        patch_name: str | None = None,
    ) -> list[dict[str, Any]]:
        result = self.session.execute(
            text(
                """
                select
                    rdms.pcode_normalized,
                    coalesce(
                        max(nullif(d.latest_doctor_name, '')),
                        max(nullif(rdms.doctor_name, '')),
                        rdms.pcode_normalized
                    ) as doctor_name
                from rcpa_doctor_month_summary rdms
                join countries c on c.id = rdms.country_id
                left join doctors d
                  on d.country_id = rdms.country_id
                 and d.pcode_normalized = rdms.pcode_normalized
                where (
                    lower(c.code) = lower(cast(:country as text))
                    or lower(c.name) = lower(cast(:country as text))
                )
                  and lower(
                    coalesce(nullif(rdms.territory_name, ''), nullif(rdms.patch_name, ''), 'Unknown')
                  ) = lower(cast(:territory_name as text))
                  and (
                    (
                        cast(:patch_name as text) is null
                        and nullif(rdms.patch_name, '') is null
                    )
                    or nullif(rdms.patch_name, '') = cast(:patch_name as text)
                  )
                  and rdms.pcode_normalized is not null
                group by rdms.pcode_normalized
                order by doctor_name nulls last, rdms.pcode_normalized
                """
            ),
            {
                "country": country,
                "territory_name": territory_name,
                "patch_name": patch_name,
            },
        ).mappings()
        return [dict(row) for row in result]


def _territory_order_clause(sort_by: str, sort_dir: str) -> str:
    direction = "desc" if sort_dir == "desc" else "asc"
    sortable = {
        "territoryName": "lower(territory_name)",
        "opportunityLabel": """
            case lower(coalesce(opportunity_label, ''))
                when 'underserved' then 0
                when 'overserved' then 1
                when 'balanced' then 2
                when 'insufficient_data' then 3
                else 4
            end
        """,
        "doctorCount": "doctor_count",
        "totalPrescriptionQty": "total_prescription_qty",
    }
    primary = sortable.get(sort_by, "total_prescription_qty")
    return f"""
        order by
            {primary} {direction} nulls last,
            total_prescription_qty desc nulls last,
            territory_name asc
    """
