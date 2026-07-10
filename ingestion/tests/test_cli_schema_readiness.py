from pathlib import Path

import pytest
from typer.testing import CliRunner

from ingestion.config import get_settings
from ingestion.main import app
from ingestion.tests.fixtures.build_fixtures import build


def test_compare_cli_writes_markdown_and_json_outputs(tmp_path: Path) -> None:
    build()
    runner = CliRunner()
    output_dir = tmp_path / "reports"

    result = runner.invoke(
        app,
        [
            "compare",
            "--raw",
            "ingestion/tests/fixtures/xlsx/schema_drift_raw.xlsx",
            "--cleaned",
            "ingestion/tests/fixtures/xlsx/schema_drift_cleaned.xlsx",
            "--output-dir",
            str(output_dir),
        ],
    )

    assert result.exit_code == 0
    assert "raw_only=" in result.output
    assert "cleaned_only=" in result.output
    assert (output_dir / "workbook-comparison-report.md").exists()
    assert (output_dir / "workbook-comparison-report.json").exists()
    markdown = (output_dir / "workbook-comparison-report.md").read_text(encoding="utf-8")
    assert "## Raw-Only Columns" in markdown
    assert "Doctor Sponsorship Remark" in markdown


def test_profile_cli_writes_markdown_and_json_outputs(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    build()
    reports_dir = tmp_path / "reports"
    monkeypatch.setenv("REPORTS_DIR", str(reports_dir))
    get_settings.cache_clear()
    runner = CliRunner()

    result = runner.invoke(
        app,
        [
            "profile",
            "--data-dir",
            "ingestion/tests/fixtures/xlsx",
        ],
    )

    get_settings.cache_clear()
    assert result.exit_code == 0
    assert "Reports:" in result.output
    assert (reports_dir / "workbook-profile-report.md").exists()
    assert (reports_dir / "workbook-profile-report.json").exists()
