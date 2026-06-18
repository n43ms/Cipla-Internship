from __future__ import annotations

from sqlalchemy.orm import Session

from backend.app.repositories.doctor_repository import DoctorRepository
from backend.app.schemas.doctors import (
    DoctorBrandMixRow,
    DoctorDetailResponse,
    DoctorEngagementRow,
    DoctorPrescriptionTrendRow,
    DoctorRoiResponse,
    DoctorRoiRow,
)
from backend.app.services.dashboard_meta import build_meta
from backend.app.services.filter_validation import validate_country_month_filters
from backend.app.utils.errors import AppError


class DoctorService:
    def __init__(self, session: Session) -> None:
        self.session = session
        self.repository = DoctorRepository(session)

    def roi(
        self,
        country: str | None,
        segment: str | None,
        quadrant: str | None,
        page: int,
        page_size: int,
    ) -> DoctorRoiResponse:
        validate_country_month_filters(self.session, country=country, month=None)
        total, rows, quadrant_counts, segment_counts = self.repository.roi_rows(country, segment, quadrant, page, page_size)
        mapped = [_doctor_row(row) for row in rows]
        flags = []
        if any(not row.has_rcpa for row in mapped):
            flags.append("no_rcpa")
        if any(row.has_missing_fx for row in mapped):
            flags.append("missing_fx")
        return DoctorRoiResponse(
            meta=build_meta(
                self.session,
                filters_applied=_filters(country=country, segment=segment, quadrant=quadrant, page=page, pageSize=page_size),
                flags=flags,
                limitations=["Doctor spend is allocated evenly across parsed actual-attendance Pcodes per request."],
            ),
            page=page,
            page_size=page_size,
            total=total,
            rows=mapped,
            quadrant_counts=quadrant_counts,
            segment_counts=segment_counts,
        )

    def detail(self, country_code: str, pcode: str) -> DoctorDetailResponse:
        profile = self.repository.doctor_profile(country_code, pcode)
        if not profile:
            raise AppError("not_found", "Doctor not found for the selected country and Pcode.", status_code=404)
        mapped_profile = _doctor_row(profile)
        flags = []
        limitations = ["Doctor profile is country-scoped by Pcode."]
        if not mapped_profile.has_rcpa:
            flags.append("no_rcpa")
            limitations.append("No RCPA coverage is available for this doctor.")
        return DoctorDetailResponse(
            meta=build_meta(self.session, filters_applied={"countryCode": country_code, "pcode": pcode}, flags=flags, limitations=limitations),
            profile=mapped_profile,
            engagement_history=[DoctorEngagementRow(**row) for row in self.repository.engagement_history(country_code, pcode)],
            prescription_trend=[DoctorPrescriptionTrendRow(**row) for row in self.repository.prescription_trend(country_code, pcode)],
            brand_mix=[DoctorBrandMixRow(**row) for row in self.repository.brand_mix(country_code, pcode)],
        )


def _doctor_row(row: dict[str, object]) -> DoctorRoiRow:
    return DoctorRoiRow(
        country_code=str(row.get("country_code") or ""),
        country_name=str(row.get("country_name") or ""),
        pcode_normalized=str(row.get("pcode_normalized") or ""),
        doctor_name=row.get("doctor_name"),
        speciality=row.get("speciality"),
        doctor_class=row.get("doctor_class"),
        active_status=row.get("active_status"),
        engagement_count=int(row.get("engagement_count") or 0),
        last_engagement_date=str(row.get("last_engagement_date")) if row.get("last_engagement_date") else None,
        direct_hcp_btu_spend_usd=row.get("direct_hcp_btu_spend_usd") or 0,
        overhead_btc_spend_usd=row.get("overhead_btc_spend_usd") or 0,
        total_roi_spend_usd=row.get("total_roi_spend_usd") or 0,
        cipla_prescription_qty=row.get("cipla_prescription_qty") or 0,
        competitor_prescription_qty=row.get("competitor_prescription_qty") or 0,
        total_prescription_qty=row.get("total_prescription_qty") or 0,
        cipla_share_qty=row.get("cipla_share_qty"),
        spend_per_cipla_prescription_usd=row.get("spend_per_cipla_prescription_usd"),
        roi_segment=str(row.get("roi_segment") or "insufficient_data"),
        quadrant_x=row.get("quadrant_x") or 0,
        quadrant_y=row.get("quadrant_y") or 0,
        quadrant_label=str(row.get("quadrant_label") or "insufficient data"),
        dark_horse_flag=bool(row.get("dark_horse_flag")),
        has_rcpa=bool(row.get("has_rcpa")),
        has_missing_fx=bool(row.get("has_missing_fx")),
        has_provisional_fx=bool(row.get("has_provisional_fx")),
    )


def _filters(**values: object) -> dict[str, object]:
    return {key: value for key, value in values.items() if value not in (None, "")}
