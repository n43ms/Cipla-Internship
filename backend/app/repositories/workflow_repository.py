from __future__ import annotations

from typing import Any

from sqlalchemy import text
from sqlalchemy.orm import Session

from backend.app.repositories.base import pagination


class WorkflowRepository:
    def __init__(self, session: Session) -> None:
        self.session = session

    def rows(self, country: str | None = None, month: str | None = None, intervention_type: str | None = None) -> list[dict[str, Any]]:
        result = self.session.execute(
            text(
                """
                select *
                from mv_workflow_governance
                where (cast(:country as text) is null or lower(country_code) = lower(cast(:country as text)) or lower(country_name) = lower(cast(:country as text)))
                  and (cast(:month as text) is null or to_char(month_start_date, 'YYYY-MM') = cast(:month as text))
                  and (cast(:intervention_type as text) is null or lower(intervention_type) = lower(cast(:intervention_type as text)))
                """
            ),
            {"country": country, "month": month, "intervention_type": intervention_type},
        ).mappings()
        return [dict(row) for row in result]

    def request_rows(
        self,
        country: str | None,
        month: str | None,
        intervention_type: str | None,
        workflow_status: str | None,
        page: int,
        page_size: int,
    ) -> tuple[int, list[dict[str, Any]]]:
        limit, offset = pagination(page, page_size)
        params = {
            "country": country,
            "month": month,
            "intervention_type": intervention_type,
            "workflow_status": workflow_status,
            "limit": limit,
            "offset": offset,
        }
        where = """
            (cast(:country as text) is null or lower(country_code) = lower(cast(:country as text)) or lower(country_name) = lower(cast(:country as text)))
            and (cast(:month as text) is null or to_char(month_start_date, 'YYYY-MM') = cast(:month as text))
            and (cast(:intervention_type as text) is null or lower(intervention_type) = lower(cast(:intervention_type as text)))
            and (
                cast(:workflow_status as text) is null
                or request_approval_status = cast(:workflow_status as text)
                or request_confirmation_status = cast(:workflow_status as text)
                or post_approval_status = cast(:workflow_status as text)
                or post_confirmation_status = cast(:workflow_status as text)
            )
        """
        total = self.session.execute(text(f"select count(*) from mv_workflow_governance where {where}"), params).scalar_one()
        rows = self.session.execute(
            text(
                f"""
                select *
                from mv_workflow_governance
                where {where}
                order by month_start_date desc, country_name, source_row_number
                limit :limit offset :offset
                """
            ),
            params,
        ).mappings()
        return int(total), [dict(row) for row in rows]
