from __future__ import annotations

from decimal import Decimal

from pydantic import Field

from backend.app.schemas.meta import ApiModel, ResponseMeta


class TerritoryOpportunityRow(ApiModel):
    country_code: str
    country_name: str
    territory_name: str
    patch_name: str | None = None
    first_month: str | None = None
    last_month: str | None = None
    doctor_count: int = 0
    engaged_doctor_count: int = 0
    cipla_prescription_qty: Decimal = Decimal("0")
    competitor_prescription_qty: Decimal = Decimal("0")
    total_prescription_qty: Decimal = Decimal("0")
    cipla_share_qty: Decimal | None = None
    prescriptions_per_doctor: Decimal | None = None
    engagement_count: int = 0
    sponsorship_count: int = 0
    paid_engagement_count: int = 0
    no_fee_engagement_count: int = 0
    engagements_per_doctor: Decimal | None = None
    contracted_amount_usd: Decimal = Decimal("0")
    fmv_amount_usd: Decimal = Decimal("0")
    contract_saving_usd: Decimal = Decimal("0")
    known_investment_usd: Decimal = Decimal("0")
    manual_mapping_count: int = 0
    unknown_mapping_count: int = 0
    missing_amount_count: int = 0
    opportunity_label: str = "insufficient_data"
    evidence_confidence: str = "low"
    source_caveats: list[str] = Field(default_factory=list)


class TerritoryOpportunityResponse(ApiModel):
    meta: ResponseMeta
    page: int
    page_size: int
    total: int
    rows: list[TerritoryOpportunityRow] = Field(default_factory=list)
    label_counts: dict[str, int] = Field(default_factory=dict)
