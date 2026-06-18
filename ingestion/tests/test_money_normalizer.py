from decimal import Decimal

from ingestion.normalizers.money import fx_for_country


def test_lkr_uses_official_company_rate() -> None:
    fx = fx_for_country("Sri Lanka")

    assert fx.currency_code == "LKR"
    assert fx.rate_status == "official"
    assert fx.rate_source == "company"
    assert fx.rate_to_usd == Decimal("1") / Decimal("310")
    assert fx.to_usd(Decimal("310")) == Decimal("1.0000")


def test_non_lkr_preserves_local_amount_without_fake_usd() -> None:
    fx = fx_for_country("Nepal")

    assert fx.currency_code == "NPR"
    assert fx.rate_status == "missing"
    assert fx.to_usd(Decimal("1000")) is None
