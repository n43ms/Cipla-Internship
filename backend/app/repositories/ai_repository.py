from __future__ import annotations

import json
from typing import Any

from sqlalchemy import text
from sqlalchemy.orm import Session


class AiRepository:
    def __init__(self, session: Session) -> None:
        self.session = session

    def lookup_country_id(self, country: str | None) -> str | None:
        if not country:
            return None
        row = self.session.execute(
            text(
                """
                select id::text
                from countries
                where lower(code) = lower(:country) or lower(name) = lower(:country)
                limit 1
                """
            ),
            {"country": country},
        ).scalar()
        return str(row) if row else None

    def lookup_calendar_month_id(self, month: str | None) -> str | None:
        if not month:
            return None
        row = self.session.execute(
            text(
                """
                select id::text
                from calendar_months
                where to_char(month_start_date, 'YYYY-MM') = :month or month_label = :month
                limit 1
                """
            ),
            {"month": month},
        ).scalar()
        return str(row) if row else None

    def log_query(
        self,
        *,
        country: str | None,
        month: str | None,
        question_redacted: str,
        context_summary: dict[str, Any],
        answer: str,
        provider: str,
        model: str | None,
        latency_ms: int,
        error_code: str | None,
        error_message: str | None,
    ) -> None:
        self.session.execute(
            text(
                """
                insert into ai_query_logs (
                    country_id,
                    calendar_month_id,
                    question_redacted,
                    context_summary_json,
                    answer,
                    provider,
                    model,
                    latency_ms,
                    error_code,
                    error_message
                )
                values (
                    cast(:country_id as uuid),
                    cast(:calendar_month_id as uuid),
                    :question_redacted,
                    cast(:context_summary_json as json),
                    :answer,
                    :provider,
                    :model,
                    :latency_ms,
                    :error_code,
                    :error_message
                )
                """
            ),
            {
                "country_id": self.lookup_country_id(country),
                "calendar_month_id": self.lookup_calendar_month_id(month),
                "question_redacted": question_redacted,
                "context_summary_json": json.dumps(context_summary, default=str),
                "answer": answer,
                "provider": provider,
                "model": model,
                "latency_ms": latency_ms,
                "error_code": error_code,
                "error_message": error_message,
            },
        )
        self.session.commit()
