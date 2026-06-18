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
    ) -> WorkflowSummary:
        validate_country_month_filters(self.session, country=country, month=month)
        filters = _filters(country=country, month=month, interventionType=intervention_type)
        rows = self.repository.rows(country, month, intervention_type)
        total = len(rows) or 1
        pending_reports = sum(int(row.get("pending_report_count") or 0) for row in rows)
        pending_requests = sum(int(row.get("pending_request_count") or 0) for row in rows)
        limitations = [
            "Post-event proof completion is inferred from report approval/confirmation "
            "and expense dates; proof files are not available in the supplied workbook."
        ] if rows else ["No workflow rows match the selected filters."]
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
        )

    def requests(
        self,
        country: str | None,
        month: str | None,
        intervention_type: str | None,
        workflow_status: str | None,
        page: int,
        page_size: int,
    ) -> WorkflowRequestsResponse:
        validate_country_month_filters(self.session, country=country, month=month)
        validate_workflow_status(workflow_status)
        filters = _filters(
            country=country,
            month=month,
            interventionType=intervention_type,
            workflowStatus=workflow_status,
            page=page,
            pageSize=page_size,
        )
        total, rows = self.repository.request_rows(
            country,
            month,
            intervention_type,
            workflow_status,
            page,
            page_size,
        )
        return WorkflowRequestsResponse(
            meta=build_meta(self.session, filters_applied=filters),
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
                )
                for row in rows
            ],
        )


def _counts(rows: list[dict], field: str) -> dict[str, int]:
    return dict(Counter(str(row.get(field) or "unknown") for row in rows))


def _filters(**values: object) -> dict[str, object]:
    return {key: value for key, value in values.items() if value not in (None, "")}
