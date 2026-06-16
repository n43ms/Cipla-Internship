from pathlib import Path

import typer

from ingestion.config import get_settings
from ingestion.orchestrator import ingest_workbooks, profile_workbooks
from ingestion.report import write_ingestion_report, write_profile_report

app = typer.Typer(help="Profile, ingest, reconcile, and report on Cipla source workbooks.")


@app.command()
def profile(
    data_dir: Path | None = typer.Option(None, help="Directory containing raw local workbooks."),
    source: str = typer.Option("all", help="Source family to profile."),
) -> None:
    """Profile local source workbooks without writing business facts."""
    profiles = profile_workbooks(data_dir, source=source)
    settings = get_settings()
    output_path = settings.reports_dir / "workbook-profile-report.md"
    write_profile_report(profiles, output_path)
    typer.echo(f"Profiled {len(profiles)} workbook(s). Report: {output_path}")


@app.command()
def ingest(
    source: str = typer.Option("all", help="Source family to ingest."),
    data_dir: Path | None = typer.Option(None, help="Directory containing raw local workbooks."),
    dry_run: bool = typer.Option(False, help="Parse and validate without database writes."),
) -> None:
    """Ingest local source workbooks into canonical records."""
    summary = ingest_workbooks(data_dir, source=source, dry_run=dry_run)
    markdown_path, json_path = write_ingestion_report(summary, get_settings().reports_dir)
    typer.echo(
        f"Ingested {summary.rows_loaded} row(s) from {len(summary.profiles)} workbook(s); "
        f"warnings={summary.warning_count}, errors={summary.error_count}, dry_run={dry_run}."
    )
    typer.echo(f"Reports: {markdown_path}, {json_path}")


@app.command()
def report() -> None:
    """Show the latest generated local ingestion report path."""
    output_path = get_settings().reports_dir / "ingestion-report.md"
    if output_path.exists():
        typer.echo(str(output_path))
        return
    typer.echo("No local ingestion report exists yet. Run `python -m ingestion.main ingest --dry-run` first.")


if __name__ == "__main__":
    app()
