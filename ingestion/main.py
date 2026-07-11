import json
from pathlib import Path

import typer
from sqlalchemy import text

from ingestion.config import get_settings
from ingestion.database import session_scope
from ingestion.orchestrator import (
    ingest_manifest_batch,
    ingest_workbooks,
    profile_manifest_batch,
    profile_workbooks,
)
from ingestion.profiler import profile_path
from ingestion.reconciliation.event_matcher import EventMatcher
from ingestion.report import (
    write_ingestion_report,
    write_profile_reports,
    write_workbook_comparison_report,
)
from ingestion.repositories.event_match_repository import EventMatchRepository
from ingestion.workbook_compare import compare_workbook_profiles

app = typer.Typer(help="Profile, ingest, reconcile, and report on Cipla source workbooks.")
DATA_DIR_OPTION = typer.Option(None, help="Directory containing raw local workbooks.")
PROFILE_SOURCE_OPTION = typer.Option("all", help="Source family to profile.")
INGEST_SOURCE_OPTION = typer.Option("all", help="Source family to ingest.")
DRY_RUN_OPTION = typer.Option(False, help="Parse and validate without database writes.")
COMPARE_RAW_OPTION = typer.Option(..., "--raw", help="Raw recurring workbook path.")
COMPARE_CLEANED_OPTION = typer.Option(
    ..., "--cleaned", help="Cleaned or presentable workbook path."
)
COMPARE_OUTPUT_DIR_OPTION = typer.Option(
    None, help="Directory for comparison markdown/json reports."
)
MANIFEST_OPTION = typer.Option(..., "--manifest", help="Source manifest JSON path.")


@app.command()
def profile(
    data_dir: Path | None = DATA_DIR_OPTION,
    source: str = PROFILE_SOURCE_OPTION,
) -> None:
    """Profile local source workbooks without writing business facts."""
    profiles = profile_workbooks(data_dir, source=source)
    settings = get_settings()
    markdown_path, json_path = write_profile_reports(profiles, settings.reports_dir)
    typer.echo(f"Profiled {len(profiles)} workbook(s). Reports: {markdown_path}, {json_path}")


@app.command("batch-profile")
def batch_profile(manifest: Path = MANIFEST_OPTION) -> None:
    """Validate and profile a labeled manual upload batch."""
    summary = profile_manifest_batch(manifest)
    settings = get_settings()
    output_path = settings.reports_dir / "batch-profile-report.json"
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(summary.to_json(), indent=2), encoding="utf-8")
    typer.echo(
        f"Validated {len(summary.validation.files)} manifest file(s); "
        f"accepted={summary.accepted_count}, quarantined={summary.quarantined_count}."
    )
    typer.echo(f"Report: {output_path}")


@app.command("batch-ingest")
def batch_ingest(
    manifest: Path = MANIFEST_OPTION,
    dry_run: bool = DRY_RUN_OPTION,
) -> None:
    """Ingest a labeled batch manifest through the same path used by dashboard uploads."""
    summary = ingest_manifest_batch(manifest, dry_run=dry_run)
    markdown_path, json_path = write_ingestion_report(summary, get_settings().reports_dir)
    typer.echo(
        f"Ingested manifest batch rows_loaded={summary.rows_loaded}; "
        f"warnings={summary.warning_count}, errors={summary.error_count}, dry_run={dry_run}."
    )
    typer.echo(f"Reports: {markdown_path}, {json_path}")


@app.command("compare")
def compare_workbooks(
    raw: Path = COMPARE_RAW_OPTION,
    cleaned: Path = COMPARE_CLEANED_OPTION,
    output_dir: Path | None = COMPARE_OUTPUT_DIR_OPTION,
) -> None:
    """Compare a raw workbook profile against a cleaned workbook profile."""
    raw_profile = profile_path(raw)
    cleaned_profile = profile_path(cleaned)
    comparison = compare_workbook_profiles(raw_profile, cleaned_profile)
    settings = get_settings()
    markdown_path, json_path = write_workbook_comparison_report(
        comparison,
        output_dir or settings.reports_dir,
    )
    typer.echo(
        f"Compared raw={raw.name} cleaned={cleaned.name}; "
        f"raw_only={len(comparison.raw_only_columns)}, "
        f"cleaned_only={len(comparison.cleaned_only_columns)}."
    )
    typer.echo(f"Reports: {markdown_path}, {json_path}")


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
    typer.echo("No local ingestion report exists yet.")
    typer.echo("Run `python -m ingestion.main ingest --dry-run` first.")


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
        "mv_budget_utilization",
        "mv_doctor_roi",
        "mv_data_quality",
        "mv_sponsorship_outcomes",
        "mv_territory_opportunity",
    ]
    with session_scope() as session:
        for view_name in view_names:
            session.execute(text(f"refresh materialized view {view_name}"))
    typer.echo(f"Refreshed {len(view_names)} materialized view(s).")


if __name__ == "__main__":
    app()
