from decimal import Decimal

from ingestion.normalizers.contract_economics import normalize_contract_economics


def test_contract_economics_calculates_local_and_usd_saving() -> None:
    economics = normalize_contract_economics(
        country="Sri Lanka",
        fmv_amount=3689,
        contracted_amount=1844.5,
    )

    assert economics.currency_code == "LKR"
    assert economics.fx_rate_status == "official"
    assert economics.contract_saving_local == Decimal("1844.5")
    assert economics.fmv_amount_usd == Decimal("10.00")
    assert economics.contracted_amount_usd == Decimal("5.00")
    assert economics.contract_saving_usd == Decimal("5.00")


def test_contract_economics_does_not_zero_missing_contracted_value() -> None:
    economics = normalize_contract_economics(
        country="Nepal",
        fmv_amount=890,
        contracted_amount=None,
    )

    assert economics.fmv_amount_usd == Decimal("10.00")
    assert economics.contracted_amount_local is None
    assert economics.contract_saving_local is None
    assert economics.contract_saving_usd is None
