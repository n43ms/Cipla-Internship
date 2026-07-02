from __future__ import annotations

import re

from sqlalchemy import text
from sqlalchemy.orm import Session

from backend.app.utils.errors import AppError

MONTH_PATTERN = re.compile(r"^\d{4}-\d{2}$")
WORKFLOW_STATUSES = {
    "approved",
    "confirmed",
    "deleted",
    "draft",
    "pending",
    "pending_confirmation",
    "pending_owner",
    "rejected",
    "sent_for_correction",
    "unknown",
}


def validate_country_month_filters(
    session: Session,
    *,
    country: str | None,
    month: str | None,
) -> None:
    if country and not _country_exists(session, country):
        raise AppError("invalid_filter", f"Unknown country filter: {country}", status_code=400)
    if month:
        if not MONTH_PATTERN.match(month):
            raise AppError(
                "invalid_filter",
                "Month filter must use YYYY-MM format.",
                status_code=400,
            )
        if not _month_exists(session, month):
            raise AppError("invalid_filter", f"Unknown month filter: {month}", status_code=400)


def validate_workflow_status(workflow_status: str | None) -> None:
    if workflow_status and workflow_status not in WORKFLOW_STATUSES:
        raise AppError(
            "invalid_filter",
            f"Unknown workflow status filter: {workflow_status}",
            status_code=400,
        )


def _country_exists(session: Session, country: str) -> bool:
    return bool(
        session.execute(
            text(
                """
                select 1
                from countries
                where lower(code) = lower(:country)
                   or lower(name) = lower(:country)
                limit 1
                """
            ),
            {"country": country},
        ).first()
    )


def _month_exists(session: Session, month: str) -> bool:
    return bool(
        session.execute(
            text(
                """
                select 1
                from calendar_months
                where to_char(month_start_date, 'YYYY-MM') = :month
                limit 1
                """
            ),
            {"month": month},
        ).first()
    )
