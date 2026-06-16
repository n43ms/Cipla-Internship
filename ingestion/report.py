from __future__ import annotations

import json
from pathlib import Path

from ingestion.models import LoadResult, WorkbookProfile
from ingestion.orchestrator import IngestionSummary


def write_profile_report(profiles: list[WorkbookProfile], output_path: Path) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(profile_report_markdown(profiles), encoding="utf-8")


def write_ingestion_report(summary: IngestionSummary, output_dir: Path) -> tuple[Path, Path]:
    output_dir.mkdir(parents=True, exist_ok=True)
    markdown_path = output_dir / "ingestion-report.md"
    json_path = output_dir / "ingestion-report.json"
    markdown_path.write_text(ingestion_report_markdown(summary), encoding="utf-8")
    json_path.write_text(json.dumps(summary.to_json(), indent=2, default=str), encoding="utf-8")
    return markdown_path, json_path


def profile_report_markdown(profiles: list[WorkbookProfile]) -> str:
    lines = ["# Workbook Profile Report", ""]
    if not profiles:
        lines.append("No supported workbooks found.")
        return "\n".join(lines) + "\n"
    for profile in profiles:
        lines.extend(
            [
                f"## {profile.original_filename}",
                "",
                f"- Source type: `{profile.source_type}`",
                f"- Country scope: `{profile.country_scope or 'unknown'}`",
                f"- File type: `{profile.file_type}`",
                f"- File hash: `{profile.file_hash}`",
                f"- Sheets detected: `{profile.detected_sheet_count}`",
                f"- Canonical sheets: `{', '.join(profile.canonical_sheets) or 'none'}`",
                "",
                "| Sheet | Rows | Columns | Header Row | Required Coverage | Anomalies |",
                "|---|---:|---:|---:|---:|---|",
            ]
        )
        for sheet in profile.sheets:
            lines.append(
                f"| {sheet.sheet_name} | {sheet.row_count} | {sheet.column_count} | "
                f"{sheet.likely_header_row or ''} | {sheet.required_column_coverage:.0%} | "
                f"{'; '.join(sheet.anomalies) or ''} |"
            )
        lines.append("")
    return "\n".join(lines)


def ingestion_report_markdown(summary: IngestionSummary) -> str:
    lines = [
        "# Ingestion Report",
        "",
        f"- Dry run: `{summary.dry_run}`",
        f"- Files: `{len(summary.profiles)}`",
        f"- Rows seen: `{summary.rows_seen}`",
        f"- Rows loaded: `{summary.rows_loaded}`",
        f"- Rows skipped: `{summary.rows_skipped}`",
        f"- Warnings: `{summary.warning_count}`",
        f"- Errors: `{summary.error_count}`",
        "- Official Sri Lanka FX: `1 USD = 310 LKR`",
        "",
        "## Files",
        "",
        "| File | Source | Canonical Sheets | Rows Loaded | Issues |",
        "|---|---|---|---:|---:|",
    ]
    for profile, result in zip(summary.profiles, summary.load_results, strict=False):
        issue_count = len(result.issues) if result else 0
        rows_loaded = result.rows_loaded if result else 0
        lines.append(
            f"| {profile.original_filename} | {profile.source_type} | "
            f"{', '.join(profile.canonical_sheets)} | {rows_loaded} | {issue_count} |"
        )
    lines.append("")
    for result in summary.load_results:
        _append_issues(lines, result)
    return "\n".join(lines) + "\n"

def _append_issues(lines: list[str], result: LoadResult) -> None:
    if not result.issues:
        return
    lines.extend([f"## {result.source_type} Issues", "", "| Severity | Code | Message | Sheet | Row |", "|---|---|---|---|---:|"])
    for issue in result.issues:
        lines.append(
            f"| {issue.severity} | {issue.error_code} | {issue.message} | "
            f"{issue.sheet_name or ''} | {issue.row_number or ''} |"
        )
    lines.append("")
