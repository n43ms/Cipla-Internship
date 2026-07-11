from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal

from ingestion.models import to_decimal
from ingestion.normalizers.money import FxLookup, fx_for_country


@dataclass(frozen=True)
class ContractEconomics:
    fmv_amount_local: Decimal | None
    contracted_amount_local: Decimal | None
    contract_saving_local: Decimal | None
    fmv_amount_usd: Decimal | None
    contracted_amount_usd: Decimal | None
    contract_saving_usd: Decimal | None
    currency_code: str
    fx_rate_status: str


def normalize_contract_economics(
    *,
    country: str | None,
    fmv_amount: object,
    contracted_amount: object,
    fx: FxLookup | None = None,
) -> ContractEconomics:
    lookup = fx or fx_for_country(country)
    fmv = to_decimal(fmv_amount)
    contracted = to_decimal(contracted_amount)
    saving = None if fmv is None or contracted is None else fmv - contracted
    return ContractEconomics(
        fmv_amount_local=fmv,
        contracted_amount_local=contracted,
        contract_saving_local=saving,
        fmv_amount_usd=lookup.to_usd(fmv),
        contracted_amount_usd=lookup.to_usd(contracted),
        contract_saving_usd=lookup.to_usd(saving),
        currency_code=lookup.currency_code,
        fx_rate_status=lookup.rate_status,
    )
