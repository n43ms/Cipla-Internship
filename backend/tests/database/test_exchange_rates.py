from decimal import Decimal
from pathlib import Path

from ingestion.normalizers.money import fx_for_country


def test_lkr_uses_official_company_rate_of_310_lkr_per_usd() -> None:
    fx = fx_for_country("Sri Lanka")

    assert fx.currency_code == "LKR"
    assert fx.rate_status == "official"
    assert fx.rate_source == "company"
    assert fx.rate_to_usd == Decimal("1") / Decimal("310")
    assert fx.to_usd(Decimal("310")) == Decimal("1.00")


def test_non_lkr_known_currencies_are_provisional_until_company_rates_exist() -> None:
    fx = fx_for_country("Nepal")

    assert fx.currency_code == "NPR"
    assert fx.rate_status == "provisional"
    assert fx.rate_source == "public_market_rate"
    assert fx.rate_to_usd is not None


def test_exchange_rate_seed_documents_official_and_provisional_statuses() -> None:
    sql = Path("database/seeds/exchange_rates_static.sql").read_text(encoding="utf-8")

    assert "('LKR', 1.0 / 310.0" in sql
    assert "'company', 'official'" in sql
    assert "'public_market_rate', 'provisional'" in sql
