from pathlib import Path

import typer
from sqlalchemy import text

from ingestion.config import get_settings
from ingestion.database import session_scope
from ingestion.orchestrator import ingest_workbooks, profile_workbooks
from ingestion.reconciliation.event_matcher import EventMatcher
from ingestion.report import write_ingestion_report, write_profile_report
from ingestion.repositories.event_match_repository import EventMatchRepository

app = typer.Typer(help="Profile, ingest, reconcile, and report on Cipla source workbooks.")
DATA_DIR_OPTION = typer.Option(None, help="Directory containing raw local workbooks.")
PROFILE_SOURCE_OPTION = typer.Option("all", help="Source family to profile.")
INGEST_SOURCE_OPTION = typer.Option("all", help="Source family to ingest.")
DRY_RUN_OPTION = typer.Option(False, help="Parse and validate without database writes.")


@app.command()
def profile(
    data_dir: Path | None = DATA_DIR_OPTION,
    source: str = PROFILE_SOURCE_OPTION,
) -> None:
    """Profile local source workbooks without writing business facts."""
    profiles = profile_workbooks(data_dir, source=source)
    settings = get_settings()
    output_path = settings.reports_dir / "workbook-profile-report.md"
    write_profile_report(profiles, output_path)
    typer.echo(f"Profiled {len(profiles)} workbook(s). Report: {output_path}")


@app.command()
def ingest(
    source: str = INGEST_SOURCE_OPTION,
    data_dir: Path | None = DATA_DIR_OPTION,
    dry_run: bool = DRY_RUN_OPTION,
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


@app.command()
def reconcile() -> None:
    """Rebuild deterministic event match records from canonical tables."""
    with session_scope() as session:
        count = EventMatcher(EventMatchRepository(session)).reconcile()
    typer.echo(f"Reconciled {count} event match row(s).")


@app.command("refresh-views")
def refresh_views() -> None:
    """Refresh dashboard materialized views after ingestion or reconciliation."""
    view_names = [
        "mv_execution_kpis",
        "mv_unmatched_events",
        "mv_execution_event_matrix",
        "mv_workflow_governance",
        "mv_intervention_mix",
    ]
    with session_scope() as session:
        for view_name in view_names:
            session.execute(text(f"refresh materialized view {view_name}"))
    typer.echo(f"Refreshed {len(view_names)} materialized view(s).")


if __name__ == "__main__":
    app()
