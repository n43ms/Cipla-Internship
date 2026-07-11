from pathlib import Path

from ingestion.orchestrator import IngestionSummary, load_profiles
from ingestion.profiler import profile_path
from ingestion.report import ingestion_report_markdown
from ingestion.tests.fixtures.build_fixtures import build


def test_ingestion_report_includes_doctor_engagement_quality_summary() -> None:
    build()
    profiles = [
        profile_path(Path("ingestion/tests/fixtures/xlsx/consolidated_intervention_observed.xlsx")),
        profile_path(Path("ingestion/tests/fixtures/xls/doctor_wise_intervention_observed.xls")),
    ]
    results = load_profiles(profiles)

    markdown = ingestion_report_markdown(
        IngestionSummary(profiles=profiles, load_results=results, dry_run=True)
    )

    assert "## Doctor Engagement Data Quality" in markdown
    assert "doctor_wise_intervention_observed.xls" in markdown
    assert "| doctor_wise_intervention_observed.xls | 0 | 0 | 0 | 1 | 0 |" in markdown
    assert "## FMV vs Contracted Economics" in markdown
    assert "Contract saving is negotiation efficiency, not prescription ROI." in markdown
