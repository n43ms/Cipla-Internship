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
    ) -> tuple[int, list[dict[str, Any]], dict[str, int]]:
        limit, offset = pagination(page, page_size)
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
                order by
                    case opportunity_label
                        when 'underserved' then 0
                        when 'overserved' then 1
                        when 'self_serving' then 2
                        when 'balanced' then 3
                        else 4
                    end,
                    total_prescription_qty desc nulls last,
                    known_investment_usd desc nulls last,
                    territory_name
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
