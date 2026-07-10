from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal

from ingestion.models import to_decimal


@dataclass(frozen=True)
class NormalizedExpenses:
    btu_expense_local: Decimal | None
    btc_expense_local: Decimal | None
    total_expense_local: Decimal | None
    reconciliation_status: str


def normalize_expenses(
    *,
    btu_expense: object = None,
    btc_expense: object = None,
    total_expense: object = None,
) -> NormalizedExpenses:
    btu = to_decimal(btu_expense)
    btc = to_decimal(btc_expense)
    total = to_decimal(total_expense)
    if total is None and (btu is not None or btc is not None):
        total = (btu or Decimal("0")) + (btc or Decimal("0"))
    status = "not_available"
    if total is not None:
        status = "total_only"
    if total is not None and (btu is not None or btc is not None):
        status = "reconciled" if (btu or Decimal("0")) + (btc or Decimal("0")) == total else "mismatch"
    return NormalizedExpenses(
        btu_expense_local=btu,
        btc_expense_local=btc,
        total_expense_local=total,
        reconciliation_status=status,
    )
