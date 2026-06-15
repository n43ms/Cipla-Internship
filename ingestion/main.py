import typer

app = typer.Typer(help="Profile, ingest, reconcile, and report on Cipla source workbooks.")


@app.command()
def profile() -> None:
    """Profile local source workbooks. Implemented in Phase 3."""
    typer.echo("Workbook profiling is not implemented yet.")


@app.command()
def ingest(source: str = typer.Option("all", help="Source family to ingest.")) -> None:
    """Ingest local source workbooks. Implemented in Phase 3."""
    typer.echo(f"Ingestion for source '{source}' is not implemented yet.")


@app.command()
def report() -> None:
    """Generate ingestion report. Implemented in Phase 3."""
    typer.echo("Ingestion reporting is not implemented yet.")


if __name__ == "__main__":
    app()
