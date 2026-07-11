from pathlib import Path

from openpyxl import Workbook

from ingestion.file_registry import SourceFile, calculate_file_hash
from ingestion.loaders.consolidation import load_consolidation
from ingestion.profiler import profile_path, profile_source_file
from ingestion.tests.fixtures.build_fixtures import build


def test_consolidation_loader_extracts_working_sheet_request() -> None:
    build()
    result = load_consolidation(
        profile_path(Path("ingestion/tests/fixtures/xlsx/consolidation_tiny.xlsx"))
    )

    assert result.rows_loaded == 1
    record = result.records[0]
    assert record["req_id"] == "REQ-1"
    assert record["currency_code"] == "LKR"
    assert record["fx_rate_status"] == "official"
    assert str(record["fx_rate_to_usd"]).startswith("0.002710")
    assert record["confirmed_contracted_amount_usd"].to_eng_string() == "84.03"
    assert record["direct_hcp_spend_local"] == record["actual_btu_expense_local"]
    assert record["overhead_spend_local"] == record["actual_btc_expense_local"]
    assert record["total_roi_spend_local"] == record["actual_total_expense_local"]
    assert record["city"] == "Colombo"


def test_consolidation_loader_derives_month_from_intervention_date_when_month_missing(
    tmp_path: Path,
) -> None:
    path = tmp_path / "Consolidated Intervention Report - Myanmar.xlsx"
    workbook = Workbook()
    sheet = workbook.active
    sheet.title = "Working"
    sheet.append(
        [
            "DIVISION",
            "Intervention No",
            "Intervention Start Date",
            "INTERVENTION DATE",
            "INTERVENTION NAME",
            "INTERVENTION TYPE",
            "TOTAL ACTUAL EXPENSES FOR INTERVENTION",
        ]
    )
    sheet.append(
        [
            "Myanmar",
            "160",
            "2025-11-24",
            "2025-11-24",
            "International conference",
            "International Conference",
            1100000,
        ]
    )
    workbook.save(path)

    profile = profile_source_file(
        SourceFile(
            path=path,
            original_filename=path.name,
            file_hash=calculate_file_hash(path),
            file_type="xlsx",
            source_type="consolidation",
        )
    )
    result = load_consolidation(profile)

    assert result.rows_loaded == 1
    record = result.records[0]
    assert record["req_id"] == "160"
    assert record["country"] == "Myanmar"
    assert record["month_start_date"].isoformat() == "2025-11-01"
    assert record["actual_total_expense_local"] == 1100000
