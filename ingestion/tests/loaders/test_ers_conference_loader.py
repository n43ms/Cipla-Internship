from pathlib import Path

from openpyxl import Workbook

from ingestion.file_registry import SourceFile, calculate_file_hash
from ingestion.loaders.ers_conference import load_ers_conference
from ingestion.profiler import profile_source_file


def test_ers_loader_maps_conference_rows_to_doctor_engagement_facts(tmp_path: Path) -> None:
    path = tmp_path / "ERS.xlsx"
    workbook = Workbook()
    sheet = workbook.active
    sheet.title = "Sheet1"
    sheet.append(
        [
            "Event Code",
            "BU",
            "Month",
            "Therapy",
            "Therapy Detailed",
            "Type of Event",
            "Name of the Event",
            "Doctor Name",
            "HCP Speciality",
            "Count",
            "Honorarium",
            "USD",
        ]
    )
    sheet.append(
        [
            "ERS-001",
            "Nepal",
            "May 2026",
            "Respiratory",
            "Asthma",
            "International Conference",
            "ERS Congress",
            "Dr Example",
            "Pulmonology",
            1,
            None,
            250,
        ]
    )
    sheet.append(
        [
            "ERS-002",
            "Nepal",
            "May 2026",
            "Respiratory",
            "Asthma",
            "International Conference",
            "ERS Congress",
            None,
            "Pulmonology",
            1,
            None,
            100,
        ]
    )
    workbook.save(path)

    profile = profile_source_file(
        SourceFile(
            path=path,
            original_filename=path.name,
            file_hash=calculate_file_hash(path),
            file_type="xlsx",
            source_type="ers_conference",
        )
    )
    result = load_ers_conference(profile)

    assert result.rows_loaded == 1
    assert result.rows_skipped == 1
    record = result.records[0]
    assert record["intervention_id"] == "ERS-001"
    assert record["country"] == "Nepal"
    assert record["doctor_name"] == "Dr Example"
    assert record["pcode_normalized"] is None
    assert record["is_sponsorship"] is True
    assert record["sponsorship_class"] == "international_conference"
    assert record["contracted_amount_usd"] == 250
    assert any(issue.error_code == "ers_missing_pcode" for issue in result.issues)
    assert any(issue.error_code == "ers_missing_doctor_name" for issue in result.issues)
    assert not any(issue.severity == "error" for issue in result.issues)
