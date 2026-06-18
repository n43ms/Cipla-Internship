from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from decimal import Decimal

from ingestion.models import to_usd
from ingestion.normalizers.currencies import currency_for_country

OFFICIAL_LKR_RATE_TO_USD = Decimal("1") / Decimal("310")
OFFICIAL_LKR_RATE_DATE = date(2026, 6, 16)


@dataclass(frozen=True)
class FxLookup:
    currency_code: str
    rate_to_usd: Decimal | None
    rate_status: str
    rate_source: str
    rate_date: date | None

    def to_usd(self, amount: Decimal | None) -> Decimal | None:
        return to_usd(amount, self.rate_to_usd)


def fx_for_country(country: str | None) -> FxLookup:
    currency_code = currency_for_country(country) or "UNKNOWN"
    if currency_code == "LKR":
        return FxLookup(
            currency_code=currency_code,
            rate_to_usd=OFFICIAL_LKR_RATE_TO_USD,
            rate_status="official",
            rate_source="company",
            rate_date=OFFICIAL_LKR_RATE_DATE,
        )
    return FxLookup(
        currency_code=currency_code,
        rate_to_usd=None,
        rate_status="missing",
        rate_source="pending_company_rate",
        rate_date=None,
    )
