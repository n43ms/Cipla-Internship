from __future__ import annotations

from typing import Any

from sqlalchemy import text
from sqlalchemy.orm import Session

from backend.app.repositories.base import pagination


class ExecutionRepository:
    def __init__(self, session: Session) -> None:
        self.session = session

    def summary(
        self,
        country: str | None = None,
        month: str | None = None,
    ) -> dict[str, Any] | None:
        row = self.session.execute(
            text(
                """
                with filtered as (
                    select *
                    from mv_execution_kpis
                    where (
                        cast(:country as text) is null
                        or lower(country_code) = lower(cast(:country as text))
                        or lower(country_name) = lower(cast(:country as text))
                      )
                      and (
                        cast(:month as text) is null
                        or to_char(month_start_date, 'YYYY-MM') = cast(:month as text)
                      )
                )
                select
                    count(*)::integer as scope_count,
                    coalesce(sum(planned_events), 0)::integer as planned_events,
                    coalesce(sum(matched_events), 0)::integer as matched_events,
                    coalesce(sum(weak_or_unmatched_events), 0)::integer as weak_or_unmatched_events,
                    coalesce(sum(executed_events), 0)::integer as executed_events,
                    coalesce(sum(action_due_events), 0)::integer as action_due_events,
                    coalesce(sum(planned_hcps), 0)::integer as planned_hcps,
                    coalesce(sum(engaged_hcps), 0)::integer as engaged_hcps,
                    case when coalesce(sum(planned_hcps), 0) > 0
                        then round(
                            coalesce(sum(engaged_hcps), 0)::numeric
                            / nullif(sum(planned_hcps), 0),
                            4
                        )
                        else 0 end as hcp_execution_rate,
                    case when coalesce(sum(planned_events), 0) > 0
                        then round(
                            coalesce(sum(executed_events), 0)::numeric
                            / nullif(sum(planned_events), 0),
                            4
                        )
                        else 0 end as event_execution_rate,
                    case when coalesce(sum(planned_events), 0) > 0
                        then round(
                            coalesce(sum(matched_events), 0)::numeric
                            / nullif(sum(planned_events), 0),
                            4
                        )
                        else 0 end as match_coverage,
                    max(refreshed_at) as refreshed_at
                from filtered
                """
            ),
            {"country": country, "month": month},
        ).mappings().first()
        if not row or int(row.get("scope_count") or 0) == 0:
            return None
        source_counts = self.session.execute(
            text(
                """
                with filtered as (
                    select snapshot_source_counts
                    from mv_execution_kpis
                    where (
                        cast(:country as text) is null
                        or lower(country_code) = lower(cast(:country as text))
                        or lower(country_name) = lower(cast(:country as text))
                      )
                      and (
                        cast(:month as text) is null
                        or to_char(month_start_date, 'YYYY-MM') = cast(:month as text)
                      )
                )
                select key, sum(value::integer)::integer as source_count
                from filtered, lateral jsonb_each_text(snapshot_source_counts)
                group by key
                """
            ),
            {"country": country, "month": month},
        ).mappings()
        result = dict(row)
        result["snapshot_source_counts"] = {
            str(item["key"]): int(item["source_count"] or 0)
            for item in source_counts
        }
        return result

    def filter_options(self) -> dict[str, Any]:
        countries = self.session.execute(
            text(
                """
                select distinct country_code as code, country_name as name
                from mv_execution_event_matrix
                order by country_name
                """
            )
        ).mappings()
        months = self.session.execute(
            text(
                """
                select distinct to_char(month_start_date, 'YYYY-MM') as value, month_label as label
                from mv_execution_event_matrix
                order by value desc
                """
            )
        ).mappings()
        recommended_month = self.session.execute(
            text(
                """
                select to_char(month_start_date, 'YYYY-MM') as value, month_label as label
                from mv_execution_kpis
                group by month_start_date, month_label
                having sum(planned_events) > 0
                   and (sum(executed_events) > 0 or sum(action_due_events) > 0)
                order by month_start_date desc
                limit 1
                """
            )
        ).mappings().first()
        return {
            "countries": [dict(row) for row in countries],
            "months": [dict(row) for row in months],
            "recommended_month": dict(recommended_month) if recommended_month else None,
        }

    def event_rows(
        self,
        country: str | None,
        month: str | None,
        page: int,
        page_size: int,
    ) -> tuple[int, list[dict[str, Any]]]:
        limit, offset = pagination(page, page_size)
        params = {"country": country, "month": month, "limit": limit, "offset": offset}
        total = self.session.execute(
            text(
                """
                select count(*)
                from mv_execution_event_matrix
                where (
                    cast(:country as text) is null
                    or lower(country_code) = lower(cast(:country as text))
                    or lower(country_name) = lower(cast(:country as text))
                  )
                  and (
                    cast(:month as text) is null
                    or to_char(month_start_date, 'YYYY-MM') = cast(:month as text)
                  )
                """
            ),
            params,
        ).scalar_one()
        rows = self.session.execute(
            text(
                """
                select *
                from mv_execution_event_matrix
                where (
                    cast(:country as text) is null
                    or lower(country_code) = lower(cast(:country as text))
                    or lower(country_name) = lower(cast(:country as text))
                  )
                  and (
                    cast(:month as text) is null
                    or to_char(month_start_date, 'YYYY-MM') = cast(:month as text)
                  )
                order by
                    month_start_date desc,
                    country_name,
                    match_status,
                    confidence desc,
                    event_name
                limit :limit offset :offset
                """
            ),
            params,
        ).mappings()
        return int(total), [dict(row) for row in rows]
