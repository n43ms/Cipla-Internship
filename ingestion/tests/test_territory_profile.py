from pathlib import Path

from ingestion.profiler import profile_path
from ingestion.tests.fixtures.build_fixtures import build


def test_rcpa_profile_maps_location_and_patch_fields() -> None:
    build()

    profile = profile_path(Path("ingestion/tests/fixtures/xlsx/monthly_rcpa_observed.xlsx"))
    sheet = profile.sheets[0]

    assert profile.source_type == "rcpa"
    assert sheet.mapped_columns["territory_name"] == "Location"
    assert sheet.mapped_columns["patch_name"] == "PATCHNAME"
    assert "territory_name" in sheet.sample_values


def test_msl_profile_detects_doctor_master_territory_fields() -> None:
    build()

    profile = profile_path(Path("ingestion/tests/fixtures/xlsx/msl_doctor_master_observed.xlsx"))
    sheet = profile.sheets[0]

    assert profile.source_type == "msl_doctor_master"
    assert sheet.mapped_columns["territory_name"] == "Location"
    assert sheet.mapped_columns["patch_name"] == "Patchsname"
    assert sheet.mapped_columns["legacy_code"] == "Legacy Code"
