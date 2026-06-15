from pathlib import Path


def write_placeholder_report(output_path: Path) -> None:
    """Write a minimal report until Phase 3 implements ingestion reporting."""
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text("# Ingestion Report\n\nNot implemented yet.\n", encoding="utf-8")
