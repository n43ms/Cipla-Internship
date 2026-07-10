from pathlib import Path

from openpyxl import Workbook

from ingestion.profiler import profile_path
from ingestion.tests.fixtures.build_fixtures import build
from ingestion.workbook_compare import compare_workbook_profiles


def _write_xlsx(path: Path, sheet_name: str, headers: list[str]) -> None:
    workbook = Workbook()
    sheet = workbook.active
    sheet.title = sheet_name
    sheet.append(headers)
    sheet.append(["value"] * len(headers))
    path.parent.mkdir(parents=True, exist_ok=True)
    workbook.save(path)


def _write_html_xls(path: Path, headers: list[str]) -> None:
    header_cells = "".join(f"<th>{header}</th>" for header in headers)
    value_cells = "".join("<td>value</td>" for _ in headers)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        f"<html><body><table><tr>{header_cells}</tr><tr>{value_cells}</tr></table></body></html>",
        encoding="utf-8",
    )


def test_compare_reports_shared_raw_only_cleaned_only_and_normalized_matches() -> None:
    build()
    raw_profile = profile_path(Path("ingestion/tests/fixtures/xlsx/schema_drift_raw.xlsx"))
    cleaned_profile = profile_path(Path("ingestion/tests/fixtures/xlsx/schema_drift_cleaned.xlsx"))

    comparison = compare_workbook_profiles(raw_profile, cleaned_profile)

    assert "DIVISION" in comparison.shared_columns
    assert "Raw Only Field" in comparison.raw_only_columns
    assert "Cleaned Only Field" in comparison.cleaned_only_columns
    assert {
        "normalized_header": "division",
        "raw_column": "DIVISION",
        "cleaned_column": "Division",
    } in comparison.normalized_header_matches


def test_compare_reports_rename_candidates_and_action_required_columns() -> None:
    build()
    raw_profile = profile_path(Path("ingestion/tests/fixtures/xlsx/schema_drift_raw.xlsx"))
    cleaned_profile = profile_path(Path("ingestion/tests/fixtures/xlsx/schema_drift_cleaned.xlsx"))

    comparison = compare_workbook_profiles(raw_profile, cleaned_profile)

    assert any(
        candidate.raw_column == "Doctor Sponsorship Remark"
        and candidate.cleaned_column == "Doctor Sponsorship Notes"
        for candidate in comparison.rename_candidates
    )
    assert "Raw Only Field" in comparison.action_required_columns
    assert "Cleaned Only Field" in comparison.action_required_columns
    assert comparison.mapped_canonical_fields["req_id"]["raw_column"] == "REQ_ID"
    assert comparison.mapped_canonical_fields["req_id"]["cleaned_column"] == "Request ID"


def test_compare_received_consolidated_raw_vs_cleaned_shapes(tmp_path: Path) -> None:
    raw = tmp_path / "Consolidate report All Bu's Nov'25 - 9 Jul'26.xlsx"
    cleaned = tmp_path / "Cleaned Presentable Consolidated.xlsx"
    _write_xlsx(
        raw,
        "Working",
        ["DIVISION", "REQ_ID", "INTERVENTION NAME", "Association Contract ID"],
    )
    _write_xlsx(
        cleaned,
        "Working",
        ["Division", "Request ID", "Intervention Name", "CON_AMOUNT"],
    )

    comparison = compare_workbook_profiles(profile_path(raw), profile_path(cleaned))

    assert "Association Contract ID" in comparison.raw_only_columns
    assert "CON_AMOUNT" in comparison.cleaned_only_columns
    assert comparison.mapped_canonical_fields["req_id"]["raw_column"] == "REQ_ID"


def test_compare_received_doctor_raw_html_xls_vs_cleaned_shape(tmp_path: Path) -> None:
    raw = tmp_path / "Sri Lanka Doctor Raw Report.xls"
    cleaned = tmp_path / "Cleaned Presentable Doctor Report.xlsx"
    _write_html_xls(
        raw,
        ["Division name", "Intervention No.", "DR code", "Doctor Name", "FMV amount"],
    )
    _write_xlsx(
        cleaned,
        "Doctor",
        ["Division", "Intervention ID", "Pcode", "Doctor Name", "FMVROLE"],
    )

    comparison = compare_workbook_profiles(profile_path(raw), profile_path(cleaned))

    assert "FMV amount" in comparison.raw_only_columns
    assert "FMVROLE" in comparison.cleaned_only_columns
    assert comparison.mapped_canonical_fields["doctor_name"]["raw_column"] == "Doctor Name"
