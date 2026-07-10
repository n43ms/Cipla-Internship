from __future__ import annotations

from datetime import date, datetime
from typing import Any

from sqlalchemy.orm import Session

from backend.app.repositories.doctor_repository import DoctorRepository
from backend.app.schemas.doctors import (
    DoctorBrandMixRow,
    DoctorDetailResponse,
    DoctorEngagementRow,
    DoctorPrescriptionTrendRow,
    DoctorRoiResponse,
    DoctorRoiRow,
    SponsorshipOutcomeSummary,
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
        roi_segment: str | None,
        quadrant: str | None,
        month_start: str | None,
        month_end: str | None,
        brand: str | None,
        speciality: str | None,
        doctor_class: str | None,
        include_out_of_scope: bool,
        page: int,
        page_size: int,
        sort: str = "darkHorse",
        sort_direction: str = "desc",
    ) -> DoctorRoiResponse:
        validate_country_month_filters(self.session, country=country, month=month_start)
        validate_country_month_filters(self.session, country=None, month=month_end)
        total, rows, quadrant_counts, segment_counts, quality_counts = self.repository.roi_rows(
            country,
            roi_segment,
            quadrant,
            month_start,
            month_end,
            brand,
            speciality,
            doctor_class,
            include_out_of_scope,
            page,
            page_size,
            sort,
            sort_direction,
        )
        mapped = [_doctor_row(row) for row in rows]
        flags = []
        if int(quality_counts.get("no_rcpa_count") or 0):
            flags.append("no_rcpa")
        if int(quality_counts.get("missing_fx_count") or 0):
            flags.append("missing_fx")
        if int(quality_counts.get("provisional_fx_count") or 0):
            flags.append("provisional_fx")
        limitations = [
            "Doctor spend is allocated evenly across parsed actual-attendance Pcodes per request.",
            (
                "RCPA is treated as historical prescription baseline; engagement month filters do "
                "not imply same-period prescription lift."
            ),
        ]
        if not include_out_of_scope and not country:
            limitations.append(
                "Doctor ROI defaults to Nepal and Sri Lanka primary markets; select a country "
                "or include out-of-scope rows to inspect all loaded markets."
            )
        if brand:
            limitations.append(
                "Brand filter identifies doctors with that brand in the RCPA baseline; displayed "
                "ROI metrics remain all-brand doctor totals."
            )
        if month_start or month_end:
            limitations.append(
                "Month range filters apply to engagement evidence; unengaged RCPA doctors remain "
                "visible as opportunity candidates."
            )
        return DoctorRoiResponse(
            meta=build_meta(
                self.session,
                filters_applied=_filters(
                    country=country,
                    roiSegment=roi_segment,
                    quadrant=quadrant,
                    monthStart=month_start,
                    monthEnd=month_end,
                    brand=brand,
                    speciality=speciality,
                    doctorClass=doctor_class,
                    includeOutOfScope=include_out_of_scope,
                    page=page,
                    pageSize=page_size,
                    sort=sort,
                    sortDirection=sort_direction,
                    brandFilterMode="baseline_inclusion" if brand else None,
                    periodFilterMode="engagement_period",
                ),
                flags=flags,
                limitations=limitations,
            ),
            page=page,
            page_size=page_size,
            total=total,
            sort=sort,
            sort_direction=sort_direction,
            dark_horse_count=int(quality_counts.get("dark_horse_count") or 0),
            no_rcpa_count=int(quality_counts.get("no_rcpa_count") or 0),
            missing_fx_count=int(quality_counts.get("missing_fx_count") or 0),
            provisional_fx_count=int(quality_counts.get("provisional_fx_count") or 0),
            brand_filter_mode="baseline_inclusion" if brand else None,
            period_filter_mode="engagement_period",
            rows=mapped,
            quadrant_counts=quadrant_counts,
            segment_counts=segment_counts,
        )

    def detail(self, country_code: str, pcode: str) -> DoctorDetailResponse:
        profile = self.repository.doctor_profile(country_code, pcode)
        if not profile:
            raise AppError(
                "not_found", "Doctor not found for the selected country and Pcode.", status_code=404
            )
        mapped_profile = _doctor_row(profile)
        flags = []
        limitations = ["Doctor profile is country-scoped by Pcode."]
        if not mapped_profile.has_rcpa:
            flags.append("no_rcpa")
            limitations.append("No RCPA coverage is available for this doctor.")
        if mapped_profile.sponsorship_engagement_amount_missing_count:
            flags.append("sponsorship_engagement_amount_missing")
            limitations.append(
                "Prior sponsorship or engagement evidence exists, but at least one amount is "
                "unavailable and is not counted as zero spend."
            )
        outcome = self.repository.sponsorship_outcome(country_code, pcode)
        if outcome and outcome.get("evidence_confidence") == "low":
            flags.append("low_sponsorship_outcome_confidence")
            limitations.append(
                "Sponsorship and engagement outcome evidence has insufficient pre/post RCPA "
                "windows."
            )
        if outcome and outcome.get("evidence_caveats"):
            limitations.extend(_outcome_caveats(outcome.get("evidence_caveats")))
        return DoctorDetailResponse(
            meta=build_meta(
                self.session,
                filters_applied={"countryCode": country_code, "pcode": pcode},
                flags=flags,
                limitations=limitations,
            ),
            profile=mapped_profile,
            sponsorship_outcome=(
                SponsorshipOutcomeSummary(**_sponsorship_outcome_row(outcome)) if outcome else None
            ),
            engagement_history=[
                DoctorEngagementRow(**_doctor_engagement_row(row))
                for row in self.repository.engagement_history(country_code, pcode)
            ],
            prescription_trend=[
                DoctorPrescriptionTrendRow(**_prescription_trend_row(row))
                for row in self.repository.prescription_trend(country_code, pcode)
            ],
            brand_mix=[
                DoctorBrandMixRow(**row) for row in self.repository.brand_mix(country_code, pcode)
            ],
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
        sponsorship_count=int(row.get("sponsorship_count") or 0),
        no_fee_engagement_count=int(row.get("no_fee_engagement_count") or 0),
        paid_engagement_count=int(row.get("paid_engagement_count") or 0),
        first_engagement_date=str(row.get("first_engagement_date"))
        if row.get("first_engagement_date")
        else None,
        last_engagement_date=str(row.get("last_engagement_date"))
        if row.get("last_engagement_date")
        else None,
        direct_hcp_btu_spend_usd=row.get("direct_hcp_btu_spend_usd") or 0,
        overhead_btc_spend_usd=row.get("overhead_btc_spend_usd") or 0,
        total_roi_spend_usd=row.get("total_roi_spend_usd") or 0,
        contracted_engagement_amount_usd=row.get("contracted_engagement_amount_usd") or 0,
        fmv_engagement_amount_usd=row.get("fmv_engagement_amount_usd") or 0,
        contract_saving_usd=row.get("contract_saving_usd") or 0,
        sponsorship_engagement_amount_missing_count=int(
            row.get("sponsorship_engagement_amount_missing_count") or 0
        ),
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
        dark_horse_unengaged_flag=bool(row.get("dark_horse_unengaged_flag")),
        high_value_engaged_flag=bool(row.get("high_value_engaged_flag")),
        has_rcpa=bool(row.get("has_rcpa")),
        has_missing_fx=bool(row.get("has_missing_fx")),
        has_provisional_fx=bool(row.get("has_provisional_fx")),
        rcpa_first_month=str(row.get("rcpa_first_month")) if row.get("rcpa_first_month") else None,
        rcpa_last_month=str(row.get("rcpa_last_month")) if row.get("rcpa_last_month") else None,
        rcpa_month_count=int(row.get("rcpa_month_count") or 0),
    )


def _filters(**values: object) -> dict[str, object]:
    return {key: value for key, value in values.items() if value not in (None, "")}


def _doctor_engagement_row(row: dict[str, Any]) -> dict[str, Any]:
    mapped = dict(row)
    for field in ("month", "actual_intervention_date", "expected_intervention_date"):
        mapped[field] = _iso_date(mapped.get(field))
    return mapped


def _prescription_trend_row(row: dict[str, Any]) -> dict[str, Any]:
    mapped = dict(row)
    mapped["month"] = _iso_date(mapped.get("month")) or ""
    return mapped


def _iso_date(value: object) -> str | None:
    if value is None:
        return None
    if isinstance(value, datetime):
        return value.date().isoformat()
    if isinstance(value, date):
        return value.isoformat()
    return str(value)


def _sponsorship_outcome_row(row: dict[str, object]) -> dict[str, object]:
    return {
        "sponsorship_count": int(row.get("sponsorship_count") or 0),
        "paid_engagement_count": int(row.get("paid_engagement_count") or 0),
        "no_fee_engagement_count": int(row.get("no_fee_engagement_count") or 0),
        "paid_service_count": int(row.get("paid_service_count") or 0),
        "contracted_amount_usd": row.get("contracted_amount_usd") or 0,
        "fmv_amount_usd": row.get("fmv_amount_usd") or 0,
        "contract_saving_usd": row.get("contract_saving_usd") or 0,
        "doctor_attributable_expense_local": row.get("doctor_attributable_expense_local") or 0,
        "known_engagement_investment_usd": row.get("known_engagement_investment_usd") or 0,
        "pre_window_cipla_rx_qty": row.get("pre_window_cipla_rx_qty") or 0,
        "post_window_cipla_rx_qty": row.get("post_window_cipla_rx_qty") or 0,
        "associated_rx_movement_qty": row.get("associated_rx_movement_qty") or 0,
        "pre_window_month_count": int(row.get("pre_window_month_count") or 0),
        "post_window_month_count": int(row.get("post_window_month_count") or 0),
        "evidence_confidence": str(row.get("evidence_confidence") or "low"),
        "evidence_caveats": list(row.get("evidence_caveats") or []),
    }


def _outcome_caveats(values: object) -> list[str]:
    caveats = [str(value) for value in (values or [])]
    messages = {
        "amount_unavailable_not_counted_as_zero": (
            "Some sponsorship or engagement evidence has unavailable amount and is not counted "
            "as zero."
        ),
        "insufficient_pre_window_rcpa": (
            "Pre-engagement RCPA coverage is insufficient for a stable comparison."
        ),
        "insufficient_post_window_rcpa": (
            "Post-engagement RCPA coverage is insufficient for a stable comparison."
        ),
        "manual_rcpa_mapping_period": (
            "Some RCPA evidence comes from manual P-code mapping periods."
        ),
        "unknown_rcpa_mapping_period": "Some RCPA evidence has unknown P-code mapping provenance.",
        "missing_fx": (
            "Some engagement economics cannot be normalized to USD because FX is missing."
        ),
        "provisional_fx": "Some engagement economics use provisional FX.",
    }
    return [messages.get(caveat, caveat) for caveat in caveats]
