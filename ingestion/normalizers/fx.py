from __future__ import annotations

from decimal import Decimal

from ingestion.normalizers.money import OFFICIAL_COMPANY_RATES_TO_USD, fx_for_country


def official_rate_to_usd_for_country(country: str | None) -> Decimal | None:
    lookup = fx_for_country(country)
    return lookup.rate_to_usd if lookup.rate_status == "official" else None


def official_company_rates_to_usd() -> dict[str, Decimal]:
    return dict(OFFICIAL_COMPANY_RATES_TO_USD)
