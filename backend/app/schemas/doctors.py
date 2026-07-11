from __future__ import annotations

from decimal import Decimal

from pydantic import Field

from backend.app.schemas.meta import ApiModel, ResponseMeta


class DoctorRoiRow(ApiModel):
    country_code: str
    country_name: str
    pcode_normalized: str
    doctor_name: str | None = None
    speciality: str | None = None
    doctor_class: str | None = None
    territory_name: str | None = None
    territory_id: str | None = None
    has_doctor_master: bool = False
    active_status: str | None = None
    engagement_count: int = 0
    sponsorship_count: int = 0
    no_fee_engagement_count: int = 0
    paid_engagement_count: int = 0
    first_engagement_date: str | None = None
    last_engagement_date: str | None = None
    direct_hcp_btu_spend_usd: Decimal = Decimal("0")
    overhead_btc_spend_usd: Decimal = Decimal("0")
    total_roi_spend_usd: Decimal = Decimal("0")
    contracted_engagement_amount_usd: Decimal = Decimal("0")
    fmv_engagement_amount_usd: Decimal = Decimal("0")
    contract_saving_usd: Decimal = Decimal("0")
    sponsorship_engagement_amount_missing_count: int = 0
    cipla_prescription_qty: Decimal = Decimal("0")
    competitor_prescription_qty: Decimal = Decimal("0")
    total_prescription_qty: Decimal = Decimal("0")
    cipla_share_qty: Decimal | None = None
    spend_per_cipla_prescription_usd: Decimal | None = None
    roi_segment: str
    quadrant_x: Decimal = Decimal("0")
    quadrant_y: Decimal = Decimal("0")
    quadrant_label: str
    dark_horse_flag: bool
    dark_horse_unengaged_flag: bool = False
    high_value_engaged_flag: bool = False
    has_rcpa: bool
    has_missing_fx: bool = False
    has_provisional_fx: bool = False
    rcpa_first_month: str | None = None
    rcpa_last_month: str | None = None
    rcpa_month_count: int = 0


class DoctorRoiResponse(ApiModel):
    meta: ResponseMeta
    page: int
    page_size: int
    total: int
    sort: str = "darkHorse"
    sort_direction: str = "desc"
    dark_horse_count: int = 0
    no_rcpa_count: int = 0
    missing_fx_count: int = 0
    provisional_fx_count: int = 0
    brand_filter_mode: str | None = None
    period_filter_mode: str = "engagement_period"
    rows: list[DoctorRoiRow] = Field(default_factory=list)
    quadrant_counts: dict[str, int] = Field(default_factory=dict)
    segment_counts: dict[str, int] = Field(default_factory=dict)


class DoctorEngagementRow(ApiModel):
    request_id: str | None = None
    intervention_name: str | None = None
    intervention_type: str | None = None
    intervention_subtype: str | None = None
    month: str | None = None
    actual_intervention_date: str | None = None
    expected_intervention_date: str | None = None
    total_roi_spend_usd: Decimal | None = None
    contracted_amount_usd: Decimal | None = None
    fmv_amount_usd: Decimal | None = None
    contract_saving_usd: Decimal | None = None
    fx_rate_status: str | None = None
    evidence_source: str = "execution_request"


class DoctorPrescriptionTrendRow(ApiModel):
    month: str
    cipla_prescription_qty: Decimal = Decimal("0")
    competitor_prescription_qty: Decimal = Decimal("0")
    total_prescription_qty: Decimal = Decimal("0")


class DoctorBrandMixRow(ApiModel):
    brand_group: str
    own_or_competitor: str
    prescription_qty: Decimal = Decimal("0")
    prescription_value_local: Decimal = Decimal("0")


class SponsorshipOutcomeSummary(ApiModel):
    sponsorship_count: int = 0
    paid_engagement_count: int = 0
    no_fee_engagement_count: int = 0
    paid_service_count: int = 0
    contracted_amount_usd: Decimal = Decimal("0")
    fmv_amount_usd: Decimal = Decimal("0")
    contract_saving_usd: Decimal = Decimal("0")
    doctor_attributable_expense_local: Decimal = Decimal("0")
    known_engagement_investment_usd: Decimal = Decimal("0")
    pre_window_cipla_rx_qty: Decimal = Decimal("0")
    post_window_cipla_rx_qty: Decimal = Decimal("0")
    associated_rx_movement_qty: Decimal = Decimal("0")
    pre_window_month_count: int = 0
    post_window_month_count: int = 0
    evidence_confidence: str = "low"
    evidence_caveats: list[str] = Field(default_factory=list)


class DoctorDetailResponse(ApiModel):
    meta: ResponseMeta
    profile: DoctorRoiRow
    sponsorship_outcome: SponsorshipOutcomeSummary | None = None
    engagement_history: list[DoctorEngagementRow] = Field(default_factory=list)
    prescription_trend: list[DoctorPrescriptionTrendRow] = Field(default_factory=list)
    brand_mix: list[DoctorBrandMixRow] = Field(default_factory=list)
