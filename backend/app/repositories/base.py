from __future__ import annotations

from typing import Any

from sqlalchemy import text
from sqlalchemy.orm import Session


class DashboardRepository:
    def __init__(self, session: Session) -> None:
        self.session = session

    def latest_ingestion(self) -> dict[str, Any] | None:
        row = self.session.execute(
            text(
                """
                select id, status
                from ingestion_runs
                order by started_at desc
                limit 1
                """
            )
        ).mappings().first()
        return dict(row) if row else None

    def filters(self, country: str | None, month: str | None) -> dict[str, Any]:
        filters: dict[str, Any] = {}
        if country:
            filters["country"] = country
        if month:
            filters["month"] = month
        return filters


def pagination(page: int, page_size: int) -> tuple[int, int]:
    safe_page = max(page, 1)
    safe_size = min(max(page_size, 1), 100)
    return safe_size, (safe_page - 1) * safe_size
