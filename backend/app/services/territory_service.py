from __future__ import annotations

from datetime import date, datetime
from typing import Any

from sqlalchemy.orm import Session

from backend.app.repositories.territory_repository import TerritoryRepository
from backend.app.schemas.territory import (
    TerritoryDoctorRow,
    TerritoryDoctorsResponse,
    TerritoryOpportunityResponse,
    TerritoryOpportunityRow,
)
from backend.app.services.dashboard_meta import build_meta
from backend.app.services.filter_validation import validate_country_month_filters


class TerritoryService:
    def __init__(self, session: Session) -> None:
        self.session = session
        self.repository = TerritoryRepository(session)

    def opportunities(
        self,
        *,
        country: str | None,
        opportunity_label: str | None,
        page: int,
        page_size: int,
        sort_by: str,
        sort_dir: str,
    ) -> TerritoryOpportunityResponse:
        validate_country_month_filters(self.session, country=country, month=None)
        total, rows, label_counts = self.repository.opportunity_rows(
            country=country,
            opportunity_label=opportunity_label,
            page=page,
            page_size=page_size,
            sort_by=sort_by,
            sort_dir=sort_dir,
        )
        flags: list[str] = []
        limitations = [
            (
                "Territory opportunity labels are deterministic planning signals, "
                "not causal performance claims."
            ),
            (
                "Territory uses RCPA Location/PATCHNAME and engagement FS HQ/territory "
                "fields when available."
            ),
        ]
        if not rows:
            flags.append("territory_data_unavailable")
            limitations.append("No source-backed territory rows match the selected filters.")
        if any(int(row.get("manual_mapping_count") or 0) for row in rows):
            flags.append("manual_rcpa_mapping")
            limitations.append(
                "Some territory RCPA evidence comes from manual P-code mapping periods."
            )
        if any(int(row.get("unknown_mapping_count") or 0) for row in rows):
            flags.append("unknown_rcpa_mapping")
            limitations.append(
                "Some territory RCPA evidence has unknown P-code mapping provenance."
            )
        if any(int(row.get("missing_amount_count") or 0) for row in rows):
            flags.append("missing_engagement_amount")
            limitations.append(
                "Some territory engagement evidence has unavailable amount and is not counted "
                "as zero."
            )
        return TerritoryOpportunityResponse(
            meta=build_meta(
                self.session,
                filters_applied={
                    key: value
                    for key, value in {
                        "country": country,
                        "opportunityLabel": opportunity_label,
                        "page": page,
                        "pageSize": page_size,
                        "sortBy": sort_by,
                        "sortDir": sort_dir,
                    }.items()
                    if value not in (None, "")
                },
                flags=flags,
                limitations=limitations,
            ),
            page=page,
            page_size=page_size,
            total=total,
            rows=[TerritoryOpportunityRow(**_territory_row(row)) for row in rows],
            label_counts=label_counts,
        )

    def doctors(
        self,
        *,
        country: str,
        territory_name: str,
        patch_name: str | None,
    ) -> TerritoryDoctorsResponse:
        validate_country_month_filters(self.session, country=country, month=None)
        rows = self.repository.territory_doctors(
            country=country,
            territory_name=territory_name,
            patch_name=patch_name,
        )
        return TerritoryDoctorsResponse(
            meta=build_meta(
                self.session,
                filters_applied={
                    key: value
                    for key, value in {
                        "country": country,
                        "territoryName": territory_name,
                        "patchName": patch_name,
                    }.items()
                    if value not in (None, "")
                },
                limitations=[] if rows else ["No RCPA doctors match the selected territory."],
            ),
            country=country,
            territory_name=territory_name,
            patch_name=patch_name,
            total=len(rows),
            rows=[TerritoryDoctorRow(**row) for row in rows],
        )


def _territory_row(row: dict[str, Any]) -> dict[str, Any]:
    mapped = dict(row)
    mapped["first_month"] = _iso_date(mapped.get("first_month"))
    mapped["last_month"] = _iso_date(mapped.get("last_month"))
    return mapped


def _iso_date(value: object) -> str | None:
    if value is None:
        return None
    if isinstance(value, datetime):
        return value.date().isoformat()
    if isinstance(value, date):
        return value.isoformat()
    return str(value)
