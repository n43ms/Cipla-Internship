from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from decimal import Decimal

from ingestion.models import to_usd
from ingestion.normalizers.currencies import currency_for_country

OFFICIAL_COMPANY_FX_RATE_DATE = date(2026, 7, 10)
OFFICIAL_COMPANY_RATES_TO_USD: dict[str, Decimal] = {
    "LKR": Decimal("1") / Decimal("368.90"),
    "NPR": Decimal("1") / Decimal("89"),
    "OMR": Decimal("1") / Decimal("0.46"),
    "AED": Decimal("1"),
    "MMK": Decimal("1") / Decimal("4300"),
    "MYR": Decimal("1") / Decimal("4.39"),
}


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
    if currency_code in OFFICIAL_COMPANY_RATES_TO_USD:
        return FxLookup(
            currency_code=currency_code,
            rate_to_usd=OFFICIAL_COMPANY_RATES_TO_USD[currency_code],
            rate_status="official",
            rate_source="company",
            rate_date=OFFICIAL_COMPANY_FX_RATE_DATE,
        )
    return FxLookup(
        currency_code=currency_code,
        rate_to_usd=None,
        rate_status="missing",
        rate_source="pending_company_rate",
        rate_date=None,
    )
