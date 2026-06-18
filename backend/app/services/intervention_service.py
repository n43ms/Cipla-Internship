from __future__ import annotations

from sqlalchemy.orm import Session

from backend.app.repositories.intervention_repository import InterventionRepository
from backend.app.schemas.interventions import InterventionMixResponse, InterventionMixRow
from backend.app.services.dashboard_meta import build_meta
from backend.app.services.filter_validation import validate_country_month_filters


class InterventionService:
    def __init__(self, session: Session) -> None:
        self.session = session
        self.repository = InterventionRepository(session)

    def mix(self, country: str | None = None, month: str | None = None) -> InterventionMixResponse:
        validate_country_month_filters(self.session, country=country, month=month)
        filters = _filters(country=country, month=month)
        rows = self.repository.mix(country, month)
        has_missing_fx = any(
            str(row.get("fx_rate_status") or "missing") == "missing"
            for row in rows
        )
        limitations = [] if rows else ["No intervention mix rows match the selected filters."]
        flags = []
        if has_missing_fx:
            flags.append("missing_fx")
            limitations.append(
                "Some intervention spend rows use local currency only because no "
                "company FX rate is seeded for that currency."
            )
        return InterventionMixResponse(
            meta=build_meta(
                self.session,
                filters_applied=filters,
                flags=flags,
                limitations=limitations,
            ),
            rows=[
                InterventionMixRow(
                    intervention_type=str(row.get("intervention_type") or "Unknown"),
                    intervention_sub_type=row.get("intervention_sub_type"),
                    request_count=int(row.get("request_count") or 0),
                    executed_count=int(row.get("executed_count") or 0),
                    approved_count=int(row.get("approved_count") or 0),
                    report_pending_count=int(row.get("report_pending_count") or 0),
                    confirmed_contracted_amount=row.get("confirmed_contracted_amount"),
                    direct_hcp_btu_spend=row.get("direct_hcp_btu_spend"),
                    overhead_btc_spend=row.get("overhead_btc_spend"),
                    total_actual_spend=row.get("total_actual_spend"),
                    fx_rate_status=str(row.get("fx_rate_status") or "missing"),
                )
                for row in rows
            ],
        )


def _filters(**values: object) -> dict[str, object]:
    return {key: value for key, value in values.items() if value not in (None, "")}
