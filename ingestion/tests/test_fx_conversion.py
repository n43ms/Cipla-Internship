from decimal import Decimal

from ingestion.normalizers.fx import official_company_rates_to_usd, official_rate_to_usd_for_country
from ingestion.normalizers.money import fx_for_country


def test_fx_conversion_uses_only_company_supplied_rates() -> None:
    rates = official_company_rates_to_usd()

    assert rates["LKR"] == Decimal("1") / Decimal("368.90")
    assert rates["NPR"] == Decimal("1") / Decimal("89")
    assert rates["OMR"] == Decimal("1") / Decimal("0.46")
    assert rates["AED"] == Decimal("1")
    assert rates["MMK"] == Decimal("1") / Decimal("4300")
    assert rates["MYR"] == Decimal("1") / Decimal("4.39")


def test_fx_lookup_marks_company_rates_official() -> None:
    lookup = fx_for_country("Malaysia")

    assert lookup.currency_code == "MYR"
    assert lookup.rate_status == "official"
    assert lookup.rate_source == "company"
    assert lookup.to_usd(Decimal("4.39")) == Decimal("1.00")


def test_fx_lookup_flags_missing_unknown_currency_without_public_fallback() -> None:
    assert official_rate_to_usd_for_country("Unknownland") is None
    lookup = fx_for_country("Unknownland")
    assert lookup.rate_status == "missing"
    assert lookup.rate_source == "pending_company_rate"
