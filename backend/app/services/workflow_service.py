from __future__ import annotations

from collections import Counter

from sqlalchemy.orm import Session

from backend.app.repositories.workflow_repository import WorkflowRepository
from backend.app.schemas.workflow import (
    WorkflowRequestRow,
    WorkflowRequestsResponse,
    WorkflowSummary,
)
from backend.app.services.dashboard_meta import build_meta
from backend.app.services.filter_validation import (
    validate_country_month_filters,
    validate_workflow_status,
)


class WorkflowService:
    def __init__(self, session: Session) -> None:
        self.session = session
        self.repository = WorkflowRepository(session)

    def summary(
        self,
        country: str | None = None,
        month: str | None = None,
        intervention_type: str | None = None,
        include_out_of_scope: bool = False,
    ) -> WorkflowSummary:
        validate_country_month_filters(self.session, country=country, month=month)
        filters = _filters(
            country=country,
            month=month,
            interventionType=intervention_type,
            includeOutOfScope=include_out_of_scope,
        )
        rows = self.repository.rows(country, month, intervention_type, include_out_of_scope)
        total = len(rows) or 1
        pending_reports = sum(int(row.get("pending_report_count") or 0) for row in rows)
        pending_requests = sum(int(row.get("pending_request_count") or 0) for row in rows)
        limitations = [
            "Post-event proof completion is inferred from report approval/confirmation "
            "and expense dates; proof files are not available in the supplied workbook."
        ] if rows else ["No workflow rows match the selected filters."]
        if not include_out_of_scope:
            limitations.append(
                "Workflow governance defaults to Phase 4 production scope: Nepal and Sri Lanka, Apr-May 2026."
            )
        scope_statuses = list(dict.fromkeys(str(row.get("scope_status")) for row in rows if row.get("scope_status")))
        scope_reasons = list(dict.fromkeys(str(row.get("scope_reason")) for row in rows if row.get("scope_reason")))
        return WorkflowSummary(
            meta=build_meta(
                self.session,
                filters_applied=filters,
                flags=["pending_workflow"] if pending_requests or pending_reports else [],
                limitations=limitations,
            ),
            request_approval_counts=_counts(rows, "request_approval_status"),
            request_confirmation_counts=_counts(rows, "request_confirmation_status"),
            post_approval_counts=_counts(rows, "post_approval_status"),
            post_confirmation_counts=_counts(rows, "post_confirmation_status"),
            owner_stage_counts=_counts(rows, "current_owner_stage"),
            pending_request_count=pending_requests,
            pending_report_count=pending_reports,
            reports_sent_for_correction=sum(
                int(row.get("reports_sent_for_correction") or 0)
                for row in rows
            ),
            reports_approved=sum(int(row.get("reports_approved") or 0) for row in rows),
            expense_submitted_coverage=sum(
                int(row.get("expense_submitted_flag") or 0)
                for row in rows
            )
            / total,
            expense_confirmed_coverage=sum(
                int(row.get("expense_confirmed_flag") or 0)
                for row in rows
            )
            / total,
            primary_scope=all(bool(row.get("is_primary_phase4_scope")) for row in rows) if rows else True,
            scope_statuses=scope_statuses,
            scope_reasons=scope_reasons,
        )

    def requests(
        self,
        country: str | None,
        month: str | None,
        intervention_type: str | None,
        workflow_status: str | None,
        workflow_search: str | None,
        page: int,
        page_size: int,
        include_out_of_scope: bool = False,
        sort: str = "reqId",
        sort_direction: str = "asc",
    ) -> WorkflowRequestsResponse:
        validate_country_month_filters(self.session, country=country, month=month)
        validate_workflow_status(workflow_status)
        filters = _filters(
            country=country,
            month=month,
            interventionType=intervention_type,
            workflowStatus=workflow_status,
            workflowSearch=workflow_search,
            page=page,
            pageSize=page_size,
            includeOutOfScope=include_out_of_scope,
            sort=sort,
            sortDirection=sort_direction,
        )
        total, rows = self.repository.request_rows(
            country,
            month,
            intervention_type,
            workflow_status,
            workflow_search,
            page,
            page_size,
            include_out_of_scope,
            sort,
            sort_direction,
        )
        return WorkflowRequestsResponse(
            meta=build_meta(
                self.session,
                filters_applied=filters,
                limitations=(
                    []
                    if include_out_of_scope
                    else ["Workflow requests are scoped to Nepal/Sri Lanka Apr-May 2026 by default."]
                ),
            ),
            page=page,
            page_size=page_size,
            total=total,
            rows=[
                WorkflowRequestRow(
                    req_id=row.get("req_id") or row.get("request_uid"),
                    country=str(row.get("country_name") or row.get("country_code") or ""),
                    month=str(row.get("month_label") or row.get("month_start_date") or ""),
                    rep_name=row.get("rep_name"),
                    intervention_type=row.get("intervention_type"),
                    request_approval_status=str(row.get("request_approval_status") or "unknown"),
                    request_confirmation_status=str(
                        row.get("request_confirmation_status") or "unknown"
                    ),
                    post_approval_status=str(row.get("post_approval_status") or "unknown"),
                    post_confirmation_status=str(row.get("post_confirmation_status") or "unknown"),
                    current_owner_stage=row.get("current_owner_stage"),
                    expense_submitted_date=row.get("expense_submitted_date"),
                    expense_confirmed_date=row.get("expense_confirmed_date"),
                    is_primary_phase4_scope=bool(row.get("is_primary_phase4_scope")),
                    scope_status=row.get("scope_status"),
                    scope_reason=row.get("scope_reason"),
                )
                for row in rows
            ],
        )


def _counts(rows: list[dict], field: str) -> dict[str, int]:
    return dict(Counter(str(row.get(field) or "unknown") for row in rows))


def _filters(**values: object) -> dict[str, object]:
    return {key: value for key, value in values.items() if value not in (None, "")}
