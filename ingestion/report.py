from __future__ import annotations

import json
from datetime import date, datetime
from pathlib import Path

from ingestion.constants import PHASE4_EXECUTION_MONTHS, PHASE4_PRIMARY_COUNTRIES
from ingestion.models import LoadResult, WorkbookProfile
from ingestion.orchestrator import IngestionSummary
from ingestion.workbook_compare import WorkbookComparison


def write_profile_report(profiles: list[WorkbookProfile], output_path: Path) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(profile_report_markdown(profiles), encoding="utf-8")


def write_workbook_comparison_report(
    comparison: WorkbookComparison,
    output_dir: Path,
) -> tuple[Path, Path]:
    output_dir.mkdir(parents=True, exist_ok=True)
    markdown_path = output_dir / "workbook-comparison-report.md"
    json_path = output_dir / "workbook-comparison-report.json"
    markdown_path.write_text(workbook_comparison_markdown(comparison), encoding="utf-8")
    json_path.write_text(json.dumps(comparison.to_json(), indent=2), encoding="utf-8")
    return markdown_path, json_path


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
        lines.extend(["", "### Schema Drift", ""])
        for sheet in profile.sheets:
            lines.extend(
                [
                    f"#### {sheet.sheet_name}",
                    "",
                    f"- Mapped canonical fields: `{len(sheet.mapped_columns)}`",
                    f"- Unknown columns: `{len(sheet.unknown_columns)}`",
                    f"- Missing required fields: `{len(sheet.missing_required_columns)}`",
                    f"- Empty columns: `{len(sheet.empty_columns)}`",
                    "",
                ]
            )
            if sheet.mapped_columns:
                lines.extend(["Mapped fields:", ""])
                for canonical, source_column in sorted(sheet.mapped_columns.items()):
                    lines.append(f"- `{canonical}` <- `{source_column}`")
                lines.append("")
            if sheet.unknown_columns:
                lines.extend(["Unknown columns:", ""])
                for column in sheet.unknown_columns:
                    lines.append(f"- `{column}`")
                lines.append("")
            if sheet.missing_required_columns:
                lines.extend(["Missing required fields:", ""])
                for column in sheet.missing_required_columns:
                    lines.append(f"- `{column}`")
                lines.append("")
            if sheet.empty_columns:
                lines.extend(["Empty columns:", ""])
                for column in sheet.empty_columns:
                    lines.append(f"- `{column}`")
                lines.append("")
            if sheet.sample_values:
                lines.extend(["Sample values:", "", "| Column | Values |", "|---|---|"])
                for column, values in sorted(sheet.sample_values.items()):
                    lines.append(f"| `{column}` | {'; '.join(values)} |")
                lines.append("")
        lines.append("")
    return "\n".join(lines)


def workbook_comparison_markdown(comparison: WorkbookComparison) -> str:
    lines = [
        "# Workbook Comparison Report",
        "",
        f"- Raw workbook: `{comparison.raw_filename}`",
        f"- Cleaned workbook: `{comparison.cleaned_filename}`",
        f"- Raw sheet: `{comparison.raw_sheet}`",
        f"- Cleaned sheet: `{comparison.cleaned_sheet}`",
        "",
        "## Column Summary",
        "",
        f"- Shared columns: `{len(comparison.shared_columns)}`",
        f"- Raw-only columns: `{len(comparison.raw_only_columns)}`",
        f"- Cleaned-only columns: `{len(comparison.cleaned_only_columns)}`",
        f"- Rename candidates: `{len(comparison.rename_candidates)}`",
        f"- Action-required columns: `{len(comparison.action_required_columns)}`",
        "",
    ]
    _append_column_list(lines, "Shared Columns", comparison.shared_columns)
    _append_column_list(lines, "Raw-Only Columns", comparison.raw_only_columns)
    _append_column_list(lines, "Cleaned-Only Columns", comparison.cleaned_only_columns)
    if comparison.normalized_header_matches:
        lines.extend(
            ["## Normalized Header Matches", "", "| Normalized | Raw | Cleaned |", "|---|---|---|"]
        )
        for row in comparison.normalized_header_matches:
            normalized = row["normalized_header"]
            raw_column = row["raw_column"]
            cleaned_column = row["cleaned_column"]
            lines.append(f"| `{normalized}` | `{raw_column}` | `{cleaned_column}` |")
        lines.append("")
    if comparison.rename_candidates:
        lines.extend(
            ["## Rename Candidates", "", "| Raw | Cleaned | Similarity |", "|---|---|---:|"]
        )
        for candidate in comparison.rename_candidates:
            lines.append(
                f"| `{candidate.raw_column}` | `{candidate.cleaned_column}` | "
                f"{candidate.similarity:.0%} |"
            )
        lines.append("")
    if comparison.mapped_canonical_fields:
        lines.extend(
            [
                "## Mapped Canonical Fields",
                "",
                "| Field | Raw Column | Cleaned Column |",
                "|---|---|---|",
            ]
        )
        for field, columns in comparison.mapped_canonical_fields.items():
            lines.append(
                f"| `{field}` | `{columns.get('raw_column') or ''}` | "
                f"`{columns.get('cleaned_column') or ''}` |"
            )
        lines.append("")
    _append_column_list(lines, "Action Required Columns", comparison.action_required_columns)
    return "\n".join(lines) + "\n"


def _append_column_list(lines: list[str], title: str, columns: list[str]) -> None:
    lines.extend([f"## {title}", ""])
    if not columns:
        lines.extend(["None.", ""])
        return
    for column in columns:
        lines.append(f"- `{column}`")
    lines.append("")


def ingestion_report_markdown(summary: IngestionSummary) -> str:
    source_rows = _source_row_summary(summary)
    fx_rows = _fx_summary(summary)
    rcpa_storage_rows = _rcpa_storage_summary(summary)
    scope_rows = _phase4_scope_summary(summary)
    duplicate_rows = _planner_duplicate_summary(summary)
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
        "- Phase 4 production scope: "
        f"`{', '.join(PHASE4_PRIMARY_COUNTRIES)}` for "
        f"`{', '.join(PHASE4_EXECUTION_MONTHS)}`",
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
    if rcpa_storage_rows:
        lines.extend(
            [
                "",
                "## RCPA Free-Tier Storage Summary",
                "",
                "| File | Online Rows | Detail Rows | Detail Extract |",
                "|---|---:|---:|---|",
            ]
        )
        for row in rcpa_storage_rows:
            lines.append(
                f"| {row['file']} | {row['online_rows']} | {row['detail_rows']} | "
                f"{row['detail_extract']} |"
            )
    lines.extend(
        [
            "",
            "## Phase 4 Scope Coverage",
            "",
            "Out-of-scope source rows are preserved in canonical tables but excluded "
            "from default Phase 4 KPI math.",
            "",
            "| Source Type | Primary Scope Rows | Out-of-Scope Rows |",
            "|---|---:|---:|",
        ]
    )
    for source_type, stats in sorted(scope_rows.items()):
        lines.append(f"| {source_type} | {stats['primary']} | {stats['out_of_scope']} |")
    if duplicate_rows:
        lines.extend(
            [
                "",
                "## Planner Repeated Natural Grains",
                "",
                "These rows share source file, country, month, event type, and normalized "
                "event name. They are preserved at source-row grain and must be reviewed "
                "as repeated planned instances versus accidental duplicates before deduping.",
                "",
                "| File | Country | Month | Event Type | Event | Planned Instances | Source Rows |",
                "|---|---|---|---|---|---:|---|",
            ]
        )
        for row in duplicate_rows:
            lines.append(
                f"| {row['file']} | {row['country']} | {row['month']} | {row['event_type']} | "
                f"{row['event_name']} | {row['count']} | {row['source_rows']} |"
            )
    lines.extend(
        [
            "",
            "## Files",
            "",
            "| File | Source | Hash | Canonical Sheets | Rows Seen | Rows Loaded | "
            "Rows Skipped | Issues |",
            "|---|---|---|---|---:|---:|---:|---:|",
        ]
    )
    for profile, result in zip(summary.profiles, summary.load_results, strict=False):
        issue_count = len(result.issues) if result else 0
        rows_seen = result.rows_seen if result else 0
        rows_loaded = result.rows_loaded if result else 0
        rows_skipped = result.rows_skipped if result else 0
        lines.append(
            f"| {profile.original_filename} | {profile.source_type} | `{profile.file_hash}` | "
            f"{', '.join(profile.canonical_sheets)} | {rows_seen} | {rows_loaded} | "
            f"{rows_skipped} | {issue_count} |"
        )
    lines.append("")
    for result in summary.load_results:
        _append_issues(lines, result)
    return "\n".join(lines) + "\n"


def _append_issues(lines: list[str], result: LoadResult) -> None:
    if not result.issues:
        return
    lines.extend(
        [
            f"## {result.source_type} Issues",
            "",
            "| Severity | Code | Message | Sheet | Row |",
            "|---|---|---|---|---:|",
        ]
    )
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


def _rcpa_storage_summary(summary: IngestionSummary) -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    for profile, result in zip(summary.profiles, summary.load_results, strict=False):
        if result.source_type != "rcpa":
            continue
        rows.append(
            {
                "file": profile.original_filename,
                "online_rows": result.summaries.get("rcpa_online_record_count", result.rows_loaded),
                "detail_rows": result.summaries.get("rcpa_detail_record_count", 0),
                "detail_extract": result.summaries.get("rcpa_detail_export_path", "dry-run"),
            }
        )
    return rows


def _phase4_scope_summary(summary: IngestionSummary) -> dict[str, dict[str, int]]:
    stats: dict[str, dict[str, int]] = {}
    for result in summary.load_results:
        source_stats = stats.setdefault(result.source_type, {"primary": 0, "out_of_scope": 0})
        for record in result.records:
            if _record_in_phase4_scope(record):
                source_stats["primary"] += 1
            else:
                source_stats["out_of_scope"] += 1
    return stats


def _planner_duplicate_summary(summary: IngestionSummary) -> list[dict[str, object]]:
    grouped: dict[tuple[str, str, str, str, str], dict[str, object]] = {}
    for profile, result in zip(summary.profiles, summary.load_results, strict=False):
        if result.source_type != "planner":
            continue
        for record in result.records:
            key = (
                profile.original_filename,
                str(record.get("country") or ""),
                _month_key(record.get("month_start_date")),
                str(record.get("event_type") or ""),
                str(record.get("event_name_normalized") or record.get("event_name") or ""),
            )
            row = grouped.setdefault(
                key,
                {
                    "file": profile.original_filename,
                    "country": key[1],
                    "month": key[2],
                    "event_type": key[3],
                    "event_name": record.get("event_name") or key[4],
                    "source_rows": [],
                },
            )
            row["source_rows"].append(record.get("source_row_number"))
    duplicates: list[dict[str, object]] = []
    for row in grouped.values():
        source_rows = [str(value) for value in row["source_rows"] if value is not None]
        if len(source_rows) <= 1:
            continue
        duplicates.append(
            {
                **row,
                "count": len(source_rows),
                "source_rows": ", ".join(source_rows),
            }
        )
    return sorted(
        duplicates,
        key=lambda row: (
            str(row["file"]),
            str(row["country"]),
            str(row["month"]),
            str(row["event_name"]),
        ),
    )


def _record_in_phase4_scope(record: dict[str, object]) -> bool:
    country = str(record.get("country") or record.get("country_name") or "").strip()
    month_value = (
        record.get("month_start_date")
        or record.get("month")
        or record.get("month_label")
        or record.get("calendar_month")
    )
    month = _month_key(month_value)
    return country in PHASE4_PRIMARY_COUNTRIES and month in PHASE4_EXECUTION_MONTHS


def _month_key(value: object) -> str:
    if isinstance(value, datetime):
        return value.strftime("%Y-%m")
    if isinstance(value, date):
        return value.strftime("%Y-%m")
    text = str(value or "").strip()
    return text[:7] if len(text) >= 7 else text
