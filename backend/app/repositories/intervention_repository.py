from __future__ import annotations

from typing import Any

from sqlalchemy import text
from sqlalchemy.orm import Session


class InterventionRepository:
    def __init__(self, session: Session) -> None:
        self.session = session

    def mix(self, country: str | None = None, month: str | None = None) -> list[dict[str, Any]]:
        rows = self.session.execute(
            text(
                """
                select
                    intervention_type,
                    intervention_sub_type,
                    coalesce(sum(request_count), 0)::integer as request_count,
                    coalesce(sum(executed_count), 0)::integer as executed_count,
                    coalesce(sum(approved_count), 0)::integer as approved_count,
                    coalesce(sum(report_pending_count), 0)::integer as report_pending_count,
                    sum(confirmed_contracted_amount) as confirmed_contracted_amount,
                    sum(direct_hcp_btu_spend) as direct_hcp_btu_spend,
                    sum(overhead_btc_spend) as overhead_btc_spend,
                    sum(total_actual_spend) as total_actual_spend,
                    case
                        when count(*) filter (where fx_rate_status = 'missing') > 0 then 'missing'
                        when count(*) filter (where fx_rate_status = 'provisional') > 0 then 'provisional'
                        else 'official'
                    end as fx_rate_status
                from mv_intervention_mix
                where (cast(:country as text) is null or lower(country_code) = lower(cast(:country as text)) or lower(country_name) = lower(cast(:country as text)))
                  and (cast(:month as text) is null or to_char(month_start_date, 'YYYY-MM') = cast(:month as text))
                group by intervention_type, intervention_sub_type
                order by sum(request_count) desc, intervention_type, intervention_sub_type
                """
            ),
            {"country": country, "month": month},
        ).mappings()
        return [dict(row) for row in rows]
