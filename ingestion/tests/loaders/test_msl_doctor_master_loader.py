from pathlib import Path

from openpyxl import Workbook

from ingestion.file_registry import SourceFile, calculate_file_hash
from ingestion.loaders.msl_doctor_master import load_msl_doctor_master
from ingestion.profiler import profile_source_file


def test_msl_loader_maps_doctor_master_rows(tmp_path: Path) -> None:
    path = tmp_path / "MSL.xlsx"
    workbook = Workbook()
    sheet = workbook.active
    sheet.title = "Sheet1"
    sheet.append(
        [
            "BU",
            "Pcode",
            "Doctor Name",
            "DrSname",
            "Location",
            "Territory Id",
            "Patchsname",
            "Legacy Code",
            "Speciality",
            "Class",
        ]
    )
    sheet.append(
        [
            "Nepal",
            12345,
            "Dr Example",
            "Example",
            "Kathmandu",
            "T-001",
            "Central",
            "L-001",
            "Pulmonology",
            "A",
        ]
    )
    sheet.append(
        [
            "Nepal",
            None,
            "Dr Missing Pcode",
            "Missing",
            "Kathmandu",
            "T-001",
            "Central",
            "L-002",
            "Pulmonology",
            "B",
        ]
    )
    workbook.save(path)

    profile = profile_source_file(
        SourceFile(
            path=path,
            original_filename=path.name,
            file_hash=calculate_file_hash(path),
            file_type="xlsx",
            source_type="msl_doctor_master",
        )
    )
    result = load_msl_doctor_master(profile)

    assert result.rows_seen == 2
    assert result.rows_loaded == 1
    assert result.rows_skipped == 1
    record = result.records[0]
    assert record["country"] == "Nepal"
    assert record["pcode_normalized"] == "12345"
    assert record["doctor_name"] == "Dr Example"
    assert record["doctor_name_normalized"] == "dr example"
    assert record["territory_name"] == "Kathmandu"
    assert record["territory_id"] == "T-001"
    assert record["speciality"] == "Pulmonology"
    assert record["doctor_class"] == "A"
    assert result.summaries["doctor_master_mapping_count"] == 1
    assert result.summaries["missing_pcode_count"] == 1
    assert any(issue.error_code == "msl_master_row_skipped" for issue in result.issues)
