from datetime import date
from pathlib import Path

import pytest

from ingestion.file_registry import calculate_file_hash
from ingestion.models import SheetData, SourceFile, WorkbookData
from ingestion.profiler import profile_path, profile_source_file
from ingestion.tests.fixtures.build_fixtures import build


def test_profiler_reports_mapped_and_unknown_columns() -> None:
    build()
    profile = profile_path(Path("ingestion/tests/fixtures/xlsx/schema_drift_raw.xlsx"))
    sheet = profile.sheets[0]

    assert profile.source_type == "consolidation"
    assert sheet.mapped_columns["country"] == "DIVISION"
    assert sheet.mapped_columns["month"] == "Months"
    assert sheet.mapped_columns["intervention_name"] == "INTERVENTION NAME"
    assert "Raw Only Field" in sheet.unknown_columns
    assert "Doctor Sponsorship Remark" in sheet.unknown_columns


def test_profiler_reports_missing_required_and_empty_columns() -> None:
    build()
    profile = profile_path(Path("ingestion/tests/fixtures/xlsx/schema_drift_raw.xlsx"))
    sheet = profile.sheets[0]

    assert sheet.missing_required_columns == []
    assert "Unused Empty Field" in sheet.empty_columns


def test_profiler_reports_bounded_sample_values() -> None:
    build()
    profile = profile_path(Path("ingestion/tests/fixtures/xlsx/schema_drift_raw.xlsx"))
    sheet = profile.sheets[0]

    assert sheet.sample_values["country"] == ["Sri Lanka"]
    assert sheet.sample_values["Raw Only Field"] == ["raw value", "raw value 2"]
    assert len(sheet.sample_values["Doctor Sponsorship Remark"]) == 2


def test_profiler_preserves_manifest_country_and_period_scope() -> None:
    build()
    source_path = Path("ingestion/tests/fixtures/xlsx/schema_drift_raw.xlsx")
    profile = profile_source_file(
        SourceFile(
            path=source_path,
            original_filename=source_path.name,
            file_hash=calculate_file_hash(source_path),
            file_type="xlsx",
            source_type="consolidation",
            country_scope="Sri Lanka, Nepal",
            period_start=date(2025, 11, 1),
            period_end=date(2026, 7, 9),
        )
    )

    assert profile.country_scope == "Sri Lanka, Nepal"
    assert str(profile.period_start) == "2025-11-01"
    assert str(profile.period_end) == "2026-07-09"


def test_profiler_detects_html_xls_doctor_contract_header_row(tmp_path: Path) -> None:
    path = tmp_path / "Sri Lanka Doctor Raw Report.xls"
    path.write_text(
        """
        <html><body><table>
        <tr><td>CRM Export</td></tr>
        <tr><td>Generated for test</td></tr>
        <tr><td></td></tr>
        <tr>
          <th>Division name</th><th>Intervention No.</th><th>DR code</th>
          <th>Doctor Name</th><th>FMV amount</th><th>Contracted Amount</th>
        </tr>
        <tr>
          <td>Sri Lanka</td><td>INT-1</td><td>P123</td>
          <td>Dr Example</td><td>100</td><td>80</td>
        </tr>
        </table></body></html>
        """,
        encoding="utf-8",
    )

    profile = profile_source_file(
        SourceFile(
            path=path,
            original_filename=path.name,
            file_hash=calculate_file_hash(path),
            file_type="xls",
            source_type="doctor_contract",
            country_scope="Sri Lanka",
        )
    )

    sheet = profile.sheets[0]
    assert profile.source_type == "doctor_contract"
    assert sheet.likely_header_row == 4
    assert sheet.likely_data_start_row == 5
    assert sheet.mapped_columns["doctor_code"] == "DR code"
    assert sheet.mapped_columns["fmv_amount"] == "FMV amount"
    assert sheet.row_count == 4


def test_profiler_handles_historical_rcpa_xlsb_profile_metadata(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    path = tmp_path / "Nepal & Myanmar RCPA Report Apr'25-mar'26.xlsb"
    path.write_bytes(b"synthetic xlsb placeholder")

    def fake_read_workbook(workbook_path: Path) -> WorkbookData:
        return WorkbookData(
            path=workbook_path,
            reader_engine="test_xlsb",
            sheets=[
                SheetData(
                    name="RCPA",
                    rows=[
                        ["BU", "Month", "Pcode", "Brand", "Quantity"],
                        ["Nepal", "Apr-25", "P1", "Brand A", 10],
                    ],
                )
            ],
        )

    monkeypatch.setattr("ingestion.profiler.read_workbook", fake_read_workbook)

    profile = profile_source_file(
        SourceFile(
            path=path,
            original_filename=path.name,
            file_hash=calculate_file_hash(path),
            file_type="xlsb",
            source_type="rcpa",
            country_scope="Nepal, Myanmar",
            period_start=date(2025, 4, 1),
            period_end=date(2026, 3, 31),
        )
    )

    sheet = profile.sheets[0]
    assert profile.file_type == "xlsb"
    assert profile.period_start == date(2025, 4, 1)
    assert profile.period_end == date(2026, 3, 31)
    assert sheet.row_count == 2
    assert sheet.mapped_columns["pcode"] == "Pcode"
