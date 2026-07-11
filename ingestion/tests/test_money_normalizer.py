from decimal import Decimal

from ingestion.normalizers.money import fx_for_country


def test_lkr_uses_official_company_rate() -> None:
    fx = fx_for_country("Sri Lanka")

    assert fx.currency_code == "LKR"
    assert fx.rate_status == "official"
    assert fx.rate_source == "company"
    assert fx.rate_to_usd == Decimal("1") / Decimal("368.90")
    assert fx.to_usd(Decimal("368.90")) == Decimal("1.0000")


def test_non_lkr_uses_company_official_rate_without_public_fallback() -> None:
    fx = fx_for_country("Nepal")

    assert fx.currency_code == "NPR"
    assert fx.rate_status == "official"
    assert fx.rate_source == "company"
    assert fx.to_usd(Decimal("89")) == Decimal("1.0000")
