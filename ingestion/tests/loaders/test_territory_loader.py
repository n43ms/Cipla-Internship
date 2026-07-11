from datetime import date
from decimal import Decimal

from ingestion.normalizers.territory import (
    classify_territory_opportunity,
    engagement_territory_observations,
    rcpa_territory_observations,
)


def test_rcpa_territory_observations_capture_country_patch_period_doctors_and_rx() -> None:
    observations = rcpa_territory_observations(
        [
            {
                "country": "Sri Lanka",
                "territory_name": "Colombo",
                "patch_name": "Patch A",
                "month_start_date": date(2026, 6, 1),
                "pcode_normalized": "P001",
                "total_prescription_qty": Decimal("40"),
            },
            {
                "country": "Sri Lanka",
                "territory_name": "Colombo",
                "patch_name": "Patch A",
                "month_start_date": date(2026, 6, 1),
                "pcode_normalized": "P002",
                "total_prescription_qty": Decimal("80"),
            },
        ]
    )

    assert observations == [
        observations[0],
    ]
    assert observations[0].country == "Sri Lanka"
    assert observations[0].territory_name == "Colombo"
    assert observations[0].patch_name == "Patch A"
    assert observations[0].period == "2026-06"
    assert observations[0].doctor_count == 2
    assert observations[0].prescription_qty == Decimal("120")


def test_engagement_territory_observations_capture_engagement_count_and_spend() -> None:
    observations = engagement_territory_observations(
        [
            {
                "country": "Sri Lanka",
                "fs_hq": "Colombo",
                "month_start_date": date(2026, 7, 1),
                "pcode_normalized": "P001",
                "contracted_amount_usd": Decimal("100"),
                "total_roi_spend_usd": Decimal("25"),
            },
            {
                "country": "Sri Lanka",
                "fs_hq": "Colombo",
                "month_start_date": date(2026, 7, 1),
                "pcode_normalized": "P002",
                "actual_total_expense_usd": Decimal("30"),
            },
        ]
    )

    assert observations[0].territory_name == "Colombo"
    assert observations[0].period == "2026-07"
    assert observations[0].doctor_count == 2
    assert observations[0].engagement_count == 2
    assert observations[0].spend_usd == Decimal("155")


def test_territory_labels_are_deterministic() -> None:
    assert classify_territory_opportunity(
        doctor_count=2,
        prescription_qty=Decimal("140"),
        engagement_count=0,
    ) == "underserved"
    assert classify_territory_opportunity(
        doctor_count=5,
        prescription_qty=Decimal("20"),
        engagement_count=6,
        spend_usd=Decimal("1000"),
    ) == "overserved"
    assert classify_territory_opportunity(
        doctor_count=2,
        prescription_qty=Decimal("70"),
        engagement_count=1,
        paid_engagement_count=1,
        sponsorship_count=0,
    ) == "balanced"
