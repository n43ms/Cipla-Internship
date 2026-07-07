from pathlib import Path

from typer.testing import CliRunner

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
