from pathlib import Path

from ingestion.loaders.monthly_rcpa import load_monthly_rcpa
from ingestion.profiler import profile_path
from ingestion.tests.fixtures.build_fixtures import build


def test_monthly_rcpa_detects_covered_month_range() -> None:
    build()
    result = load_monthly_rcpa(
        profile_path(Path("ingestion/tests/fixtures/xlsx/monthly_rcpa_observed.xlsx"))
    )

    assert str(result.summaries["covered_month_start"]) == "2025-11-01"
    assert str(result.summaries["covered_month_end"]) == "2026-07-01"


def test_monthly_rcpa_rerun_payload_has_stable_replacement_grain() -> None:
    build()
    result = load_monthly_rcpa(
        profile_path(Path("ingestion/tests/fixtures/xlsx/monthly_rcpa_observed.xlsx"))
    )

    grains = {
        (
            row["country"],
            row["month_start_date"],
            row["pcode_normalized"],
            row["currency_code"],
        )
        for row in result.records
    }
    assert len(grains) == len(result.records)


def test_monthly_rcpa_marks_missing_pcode_rows_as_skipped_warnings() -> None:
    build()
    profile = profile_path(Path("ingestion/tests/fixtures/xlsx/monthly_rcpa_observed.xlsx"))
    result = load_monthly_rcpa(profile)

    assert result.rows_skipped == 0
    assert result.summaries["missing_pcode_count"] == 0
    assert result.summaries["rcpa_load_mode"] == "monthly_cumulative"
    assert result.summaries["inserted_or_replaced_summary_rows"] == result.rows_loaded
    assert result.summaries["duplicate_source_rows_collapsed"] == 0
