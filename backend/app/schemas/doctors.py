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
    active_status: str | None = None
    engagement_count: int = 0
    last_engagement_date: str | None = None
    direct_hcp_btu_spend_usd: Decimal = Decimal("0")
    overhead_btc_spend_usd: Decimal = Decimal("0")
    total_roi_spend_usd: Decimal = Decimal("0")
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
    has_rcpa: bool
    has_missing_fx: bool = False
    has_provisional_fx: bool = False


class DoctorRoiResponse(ApiModel):
    meta: ResponseMeta
    page: int
    page_size: int
    total: int
    rows: list[DoctorRoiRow] = Field(default_factory=list)
    quadrant_counts: dict[str, int] = Field(default_factory=dict)
    segment_counts: dict[str, int] = Field(default_factory=dict)


class DoctorEngagementRow(ApiModel):
    request_id: str | None = None
    intervention_name: str | None = None
    intervention_type: str | None = None
    month: str | None = None
    actual_intervention_date: str | None = None
    total_roi_spend_usd: Decimal | None = None
    fx_rate_status: str | None = None


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


class DoctorDetailResponse(ApiModel):
    meta: ResponseMeta
    profile: DoctorRoiRow
    engagement_history: list[DoctorEngagementRow] = Field(default_factory=list)
    prescription_trend: list[DoctorPrescriptionTrendRow] = Field(default_factory=list)
    brand_mix: list[DoctorBrandMixRow] = Field(default_factory=list)
