from pathlib import Path

from typer.testing import CliRunner

from ingestion.main import app
from ingestion.tests.fixtures.build_fixtures import build


def test_profile_and_dry_run_ingest_cli_contracts() -> None:
    build()
    runner = CliRunner()
    data_dir = Path("ingestion/tests/fixtures/xlsx")

    profile_result = runner.invoke(app, ["profile", "--data-dir", str(data_dir)])
    ingest_result = runner.invoke(app, ["ingest", "--data-dir", str(data_dir), "--dry-run"])

    assert profile_result.exit_code == 0
    assert ingest_result.exit_code == 0
    assert "dry_run=True" in ingest_result.output
    report = Path("data/reports/ingestion-report.md").read_text(encoding="utf-8")
    assert "## Source Type Row Summary" in report
    assert "## FX Status Summary" in report
    assert "| LKR | official |" in report
