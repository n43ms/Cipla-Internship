from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal
from typing import Any


@dataclass(frozen=True)
class TerritoryObservation:
    country: str
    territory_name: str
    patch_name: str | None
    period: str | None
    doctor_count: int
    prescription_qty: Decimal
    engagement_count: int
    spend_usd: Decimal
    source: str


def rcpa_territory_observations(records: list[dict[str, Any]]) -> list[TerritoryObservation]:
    aggregate: dict[tuple[str, str, str | None, str | None], dict[str, Any]] = {}
    for record in records:
        country = _text(record.get("country"))
        territory = _text(record.get("territory_name")) or _text(record.get("patch_name"))
        pcode = _text(record.get("pcode_normalized"))
        if not country or not territory or not pcode:
            continue
        patch = _text(record.get("patch_name"))
        period = _period(record.get("month_start_date"))
        key = (country, territory, patch, period)
        bucket = aggregate.setdefault(
            key,
            {
                "doctor_pcodes": set(),
                "prescription_qty": Decimal("0"),
            },
        )
        bucket["doctor_pcodes"].add(pcode)
        bucket["prescription_qty"] += _decimal(record.get("total_prescription_qty"))

    return [
        TerritoryObservation(
            country=country,
            territory_name=territory,
            patch_name=patch,
            period=period,
            doctor_count=len(values["doctor_pcodes"]),
            prescription_qty=values["prescription_qty"],
            engagement_count=0,
            spend_usd=Decimal("0"),
            source="rcpa",
        )
        for (country, territory, patch, period), values in aggregate.items()
    ]


def engagement_territory_observations(records: list[dict[str, Any]]) -> list[TerritoryObservation]:
    aggregate: dict[tuple[str, str, str | None, str | None], dict[str, Any]] = {}
    for record in records:
        country = _text(record.get("country"))
        territory = (
            _text(record.get("fs_hq"))
            or _text(record.get("territory_code"))
            or _text(record.get("region"))
        )
        pcode = _text(record.get("pcode_normalized")) or _text(record.get("doctor_name"))
        if not country or not territory or not pcode:
            continue
        period = _period(record.get("month_start_date"))
        key = (country, territory, None, period)
        bucket = aggregate.setdefault(
            key,
            {
                "doctor_pcodes": set(),
                "engagement_count": 0,
                "spend_usd": Decimal("0"),
            },
        )
        bucket["doctor_pcodes"].add(pcode)
        bucket["engagement_count"] += 1
        bucket["spend_usd"] += (
            _decimal(record.get("contracted_amount_usd"))
            + _decimal(record.get("total_roi_spend_usd"))
            + _decimal(record.get("actual_total_expense_usd"))
        )

    return [
        TerritoryObservation(
            country=country,
            territory_name=territory,
            patch_name=patch,
            period=period,
            doctor_count=len(values["doctor_pcodes"]),
            prescription_qty=Decimal("0"),
            engagement_count=int(values["engagement_count"]),
            spend_usd=values["spend_usd"],
            source="engagement",
        )
        for (country, territory, patch, period), values in aggregate.items()
    ]


def classify_territory_opportunity(
    *,
    doctor_count: int,
    prescription_qty: Decimal,
    engagement_count: int,
    sponsorship_count: int = 0,
    paid_engagement_count: int = 0,
    spend_usd: Decimal = Decimal("0"),
) -> str:
    if doctor_count <= 0:
        return "insufficient_data"
    prescriptions_per_doctor = prescription_qty / Decimal(doctor_count)
    engagements_per_doctor = Decimal(engagement_count) / Decimal(doctor_count)
    if prescriptions_per_doctor >= Decimal("50") and engagement_count == 0:
        return "underserved"
    if spend_usd > 0 and prescriptions_per_doctor < Decimal("10"):
        return "overserved"
    if engagements_per_doctor > Decimal("2") and prescriptions_per_doctor < Decimal("20"):
        return "overserved"
    return "balanced"


def _period(value: object) -> str | None:
    if value is None:
        return None
    text = str(value)
    return text[:7] if len(text) >= 7 else text


def _text(value: object) -> str | None:
    if value is None:
        return None
    text = str(value).strip()
    return text or None


def _decimal(value: object) -> Decimal:
    if isinstance(value, Decimal):
        return value
    if value is None:
        return Decimal("0")
    try:
        return Decimal(str(value).replace(",", "").strip() or "0")
    except Exception:
        return Decimal("0")
