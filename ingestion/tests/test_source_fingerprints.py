from pathlib import Path

from openpyxl import Workbook

from ingestion.source_fingerprints import fingerprint_path


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


def test_fingerprints_received_consolidated_xlsx(tmp_path: Path) -> None:
    path = tmp_path / "Consolidate report All Bu's Nov'25 - 9 Jul'26.xlsx"
    _write_xlsx(
        path,
        "Working",
        ["DIVISION", "REQ_ID", "INTERVENTION NAME", "TOTAL ACTUAL EXPENSES FOR INTERVENTION"],
    )

    fingerprint = fingerprint_path(path)

    assert fingerprint.file_format == "xlsx"
    assert fingerprint.inferred_source_type == "consolidation"
    assert fingerprint.confidence >= 0.9


def test_fingerprints_doctor_wise_crm_html_xls(tmp_path: Path) -> None:
    path = tmp_path / "Sri Lanka Doctor Raw Report.xls"
    _write_html_xls(
        path,
        ["Division name", "Intervention No.", "DR code", "FMV amount", "Contracted Amount"],
    )

    fingerprint = fingerprint_path(path)

    assert fingerprint.file_format == "crm_html_xls"
    assert fingerprint.inferred_source_type == "doctor_contract"


def test_fingerprints_cleaned_presentable_xlsx(tmp_path: Path) -> None:
    path = tmp_path / "Cleaned Presentable Version - Point 2.xlsx"
    _write_xlsx(path, "Summary", ["Division", "Intervention Name", "CON_AMOUNT", "TYPE"])

    assert fingerprint_path(path).inferred_source_type == "cleaned_presentable"


def test_fingerprints_ers_msl_monthly_and_historical_workbooks(tmp_path: Path) -> None:
    ers = tmp_path / "ERS.xlsx"
    msl = tmp_path / "MSL.xlsx"
    monthly = tmp_path / "RCPA Report All Bu's Apr'26 - 03 Jul'26.xlsx"
    historical = tmp_path / "Nepal & Myanmar RCPA Report Apr'25-mar'26.xlsb"
    _write_xlsx(ers, "ERS", ["Conference", "Country", "Doctor Name"])
    _write_xlsx(msl, "MSL", ["Pcode", "Doctor Name", "BU", "Location", "Territory Id"])
    _write_xlsx(monthly, "Malaysia", ["BU", "Month", "Pcode", "Brand", "Quantity"])
    _write_xlsx(
        historical.with_suffix(".xlsx"),
        "RCPA",
        ["BU", "Month", "Pcode", "Brand", "Quantity"],
    )
    historical.write_bytes(historical.with_suffix(".xlsx").read_bytes())

    assert fingerprint_path(ers).inferred_source_type == "ers_conference"
    assert fingerprint_path(msl).inferred_source_type == "msl_doctor_master"
    assert fingerprint_path(monthly).inferred_source_type == "rcpa"
    assert fingerprint_path(historical).inferred_source_type == "rcpa"
