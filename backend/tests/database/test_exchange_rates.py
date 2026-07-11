from decimal import Decimal
from pathlib import Path

from ingestion.normalizers.money import fx_for_country


def test_lkr_uses_official_company_rate_of_368_90_lkr_per_usd() -> None:
    fx = fx_for_country("Sri Lanka")

    assert fx.currency_code == "LKR"
    assert fx.rate_status == "official"
    assert fx.rate_source == "company"
    assert fx.rate_to_usd == Decimal("1") / Decimal("368.90")
    assert fx.to_usd(Decimal("368.90")) == Decimal("1.00")


def test_non_lkr_known_currencies_use_company_rates_only() -> None:
    fx = fx_for_country("Nepal")

    assert fx.currency_code == "NPR"
    assert fx.rate_status == "official"
    assert fx.rate_source == "company"
    assert fx.rate_to_usd == Decimal("1") / Decimal("89")


def test_exchange_rate_seed_documents_only_company_official_rates() -> None:
    sql = Path("database/seeds/exchange_rates_static.sql").read_text(encoding="utf-8")

    assert "('LKR', 1.0 / 368.90" in sql
    assert "('NPR', 1.0 / 89.0" in sql
    assert "'company', 'official'" in sql
    assert "public_market_rate" not in sql
