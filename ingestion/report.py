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
    source_rows = _source_row_summary(summary)
    fx_rows = _fx_summary(summary)
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
        "## Source Type Row Summary",
        "",
        "| Source Type | Files | Rows Seen | Rows Loaded | Rows Skipped |",
        "|---|---:|---:|---:|---:|",
    ]
    for source_type, stats in sorted(source_rows.items()):
        lines.append(
            f"| {source_type} | {stats['files']} | {stats['rows_seen']} | "
            f"{stats['rows_loaded']} | {stats['rows_skipped']} |"
        )
    lines.extend(
        [
            "",
            "## FX Status Summary",
            "",
            "| Currency | FX Status | Rows |",
            "|---|---|---:|",
        ]
    )
    if fx_rows:
        for (currency, status), count in sorted(fx_rows.items()):
            lines.append(f"| {currency} | {status} | {count} |")
    else:
        lines.append("| none | none | 0 |")
    lines.extend(
        [
            "",
            "## Files",
            "",
            "| File | Source | Canonical Sheets | Rows Loaded | Issues |",
            "|---|---|---|---:|---:|",
        ]
    )
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


def _source_row_summary(summary: IngestionSummary) -> dict[str, dict[str, int]]:
    stats: dict[str, dict[str, int]] = {}
    for profile, result in zip(summary.profiles, summary.load_results, strict=False):
        source_stats = stats.setdefault(
            profile.source_type,
            {"files": 0, "rows_seen": 0, "rows_loaded": 0, "rows_skipped": 0},
        )
        source_stats["files"] += 1
        source_stats["rows_seen"] += result.rows_seen
        source_stats["rows_loaded"] += result.rows_loaded
        source_stats["rows_skipped"] += result.rows_skipped
    return stats


def _fx_summary(summary: IngestionSummary) -> dict[tuple[str, str], int]:
    stats: dict[tuple[str, str], int] = {}
    for result in summary.load_results:
        for record in result.records:
            currency = record.get("currency_code")
            status = record.get("fx_rate_status")
            if currency and status:
                key = (str(currency), str(status))
                stats[key] = stats.get(key, 0) + 1
    return stats
