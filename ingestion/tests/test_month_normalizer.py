from datetime import date

from ingestion.normalizers.months import month_start


def test_month_normalizer_handles_observed_formats() -> None:
    assert month_start("Apr-24").value == date(2024, 4, 1)
    assert month_start("25-Apr").value == date(2025, 4, 1)
    assert month_start("Oct-25").value == date(2025, 10, 1)
    assert month_start("Apr'26").value == date(2026, 4, 1)
    assert month_start("May-26").value == date(2026, 5, 1)


def test_month_normalizer_accepts_excel_serials() -> None:
    result = month_start(45772)

    assert result.status == "ok_excel_serial"
    assert result.value is not None

