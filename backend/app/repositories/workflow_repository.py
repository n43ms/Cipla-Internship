from __future__ import annotations

from typing import Any

from sqlalchemy import text
from sqlalchemy.orm import Session

from backend.app.repositories.base import pagination


class WorkflowRepository:
    def __init__(self, session: Session) -> None:
        self.session = session

    def rows(
        self,
        country: str | None = None,
        month: str | None = None,
        intervention_type: str | None = None,
        include_out_of_scope: bool = False,
    ) -> list[dict[str, Any]]:
        result = self.session.execute(
            text(
                """
                select *
                from mv_workflow_governance
                where (cast(:country as text) is null or lower(country_code) = lower(cast(:country as text)) or lower(country_name) = lower(cast(:country as text)))
                  and (cast(:month as text) is null or to_char(month_start_date, 'YYYY-MM') = cast(:month as text))
                  and (cast(:intervention_type as text) is null or lower(intervention_type) = lower(cast(:intervention_type as text)))
                  and (cast(:include_out_of_scope as boolean) or is_primary_phase4_scope)
                """
            ),
            {
                "country": country,
                "month": month,
                "intervention_type": intervention_type,
                "include_out_of_scope": include_out_of_scope,
            },
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
        include_out_of_scope: bool = False,
        sort: str = "reqId",
        sort_direction: str = "asc",
    ) -> tuple[int, list[dict[str, Any]]]:
        limit, offset = pagination(page, page_size)
        order_by = _workflow_order_by(sort, sort_direction)
        params = {
            "country": country,
            "month": month,
            "intervention_type": intervention_type,
            "workflow_status": workflow_status,
            "limit": limit,
            "offset": offset,
            "include_out_of_scope": include_out_of_scope,
        }
        where = """
            (cast(:country as text) is null or lower(country_code) = lower(cast(:country as text)) or lower(country_name) = lower(cast(:country as text)))
            and (cast(:month as text) is null or to_char(month_start_date, 'YYYY-MM') = cast(:month as text))
            and (cast(:intervention_type as text) is null or lower(intervention_type) = lower(cast(:intervention_type as text)))
            and (cast(:include_out_of_scope as boolean) or is_primary_phase4_scope)
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
                order by {order_by}
                limit :limit offset :offset
                """
            ),
            params,
        ).mappings()
        return int(total), [dict(row) for row in rows]


def _workflow_order_by(sort: str, direction: str) -> str:
    direction_sql = "asc" if direction.lower() == "asc" else "desc"
    nulls = "nulls first" if direction_sql == "asc" else "nulls last"
    columns = {
        "reqId": f"req_id {direction_sql} {nulls}, source_row_number",
        "repName": f"rep_name {direction_sql} {nulls}, req_id, source_row_number",
        "interventionType": f"intervention_type {direction_sql} {nulls}, req_id, source_row_number",
        "requestApprovalStatus": f"request_approval_status {direction_sql} {nulls}, req_id, source_row_number",
        "requestConfirmationStatus": f"request_confirmation_status {direction_sql} {nulls}, req_id, source_row_number",
        "postConfirmationStatus": f"post_confirmation_status {direction_sql} {nulls}, post_approval_status {direction_sql} {nulls}, req_id",
        "expenseConfirmedDate": f"expense_confirmed_date {direction_sql} {nulls}, expense_submitted_date {direction_sql} {nulls}, req_id",
        "scopeStatus": f"scope_status {direction_sql} {nulls}, country_name, month_start_date desc, req_id",
        "currentOwnerStage": f"current_owner_stage {direction_sql} {nulls}, req_id, source_row_number",
    }
    return columns.get(sort, columns["reqId"])
