from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

from sqlalchemy import text

from ingestion.config import get_settings
from ingestion.database import session_scope
from ingestion.file_registry import SourceFile, discover_source_files
from ingestion.loaders import (
    load_consolidation,
    load_doctor_wise_intervention,
    load_ers_conference,
    load_execution_snapshot,
    load_msl_doctor_master,
    load_planner,
    load_rcpa,
)
from ingestion.models import BatchValidationResult, LoadResult, WorkbookProfile
from ingestion.normalizers.intervention_reconciliation import reconcile_doctor_interventions
from ingestion.processed_exports import export_rcpa_detail_records
from ingestion.profiler import profile_source_file
from ingestion.reconciliation.event_matcher import EventMatcher
from ingestion.reconciliation.sri_lanka_may_derivation import derive_sri_lanka_may_snapshots
from ingestion.repositories.audit_repository import AuditRepository
from ingestion.repositories.canonical_repository import CanonicalRepository
from ingestion.repositories.event_match_repository import EventMatchRepository
from ingestion.repositories.rcpa_repository import RcpaRepository
from ingestion.source_manifest import load_source_manifest, validate_source_manifest

LOADERS = {
    "planner": load_planner,
    "execution_snapshot": load_execution_snapshot,
    "consolidation": load_consolidation,
    "doctor_contract": load_doctor_wise_intervention,
    "ers_conference": load_ers_conference,
    "msl_doctor_master": load_msl_doctor_master,
    "rcpa": load_rcpa,
}


@dataclass(frozen=True)
class IngestionSummary:
    profiles: list[WorkbookProfile]
    load_results: list[LoadResult]
    dry_run: bool
    ingestion_run_id: str | None = None

    @property
    def rows_seen(self) -> int:
        return sum(result.rows_seen for result in self.load_results)

    @property
    def rows_loaded(self) -> int:
        return sum(result.rows_loaded for result in self.load_results)

    @property
    def rows_skipped(self) -> int:
        return sum(result.rows_skipped for result in self.load_results)

    @property
    def warning_count(self) -> int:
        return sum(
            1
            for result in self.load_results
            for issue in result.issues
            if issue.severity == "warning"
        )

    @property
    def error_count(self) -> int:
        return sum(
            1
            for result in self.load_results
            for issue in result.issues
            if issue.severity == "error"
        )

    def to_json(self) -> dict[str, Any]:
        return {
            "dry_run": self.dry_run,
            "ingestion_run_id": self.ingestion_run_id,
            "file_count": len(self.profiles),
            "rows_seen": self.rows_seen,
            "rows_loaded": self.rows_loaded,
            "rows_skipped": self.rows_skipped,
            "warning_count": self.warning_count,
            "error_count": self.error_count,
            "files": [
                {
                    "filename": profile.original_filename,
                    "source_type": profile.source_type,
                    "file_hash": profile.file_hash,
                    "file_type": profile.file_type,
                    "country_scope": profile.country_scope,
                    "canonical_sheets": profile.canonical_sheets,
                    "rows_seen_profiled": profile.total_rows_seen,
                    "rows_loaded": result.rows_loaded if result else 0,
                    "rows_skipped": result.rows_skipped if result else 0,
                    "issue_count": len(result.issues) if result else 0,
                    "summaries": _reportable_summaries(result.summaries) if result else {},
                }
                for profile, result in zip(self.profiles, self.load_results, strict=False)
            ],
        }


@dataclass(frozen=True)
class BatchProfileSummary:
    validation: BatchValidationResult
    profiles: list[WorkbookProfile]

    @property
    def accepted_count(self) -> int:
        return len(self.validation.accepted_files)

    @property
    def quarantined_count(self) -> int:
        return len(self.validation.quarantined_files)

    def to_json(self) -> dict[str, Any]:
        return {
            "manifest": str(self.validation.manifest.path),
            "received_package_path": str(self.validation.manifest.received_package_path),
            "accepted_count": self.accepted_count,
            "quarantined_count": self.quarantined_count,
            "files": [
                {
                    "label": file_result.entry.label,
                    "path": str(file_result.entry.path),
                    "declared_source_type": file_result.entry.source_type,
                    "fingerprint_source_type": (
                        file_result.fingerprint.inferred_source_type
                        if file_result.fingerprint
                        else None
                    ),
                    "file_hash": file_result.file_hash,
                    "accepted": file_result.accepted,
                    "issues": [issue.error_code for issue in file_result.issues],
                }
                for file_result in self.validation.files
            ],
            "profiles": [profile.to_json() for profile in self.profiles],
        }


def profile_workbooks(
    data_dir: Path | None = None,
    *,
    source: str = "all",
) -> list[WorkbookProfile]:
    settings = get_settings()
    root = data_dir or settings.data_dir
    source_files = _filter_sources(
        discover_source_files(root, require_gitignored_path=data_dir is None),
        source,
    )
    return [profile_source_file(source_file) for source_file in source_files]


def profile_manifest_batch(manifest_path: Path) -> BatchProfileSummary:
    manifest = load_source_manifest(manifest_path)
    validation = validate_source_manifest(manifest)
    profiles = []
    for file_result in validation.accepted_files:
        if not file_result.file_hash:
            continue
        profiles.append(
            profile_source_file(
                SourceFile(
                    path=file_result.entry.path,
                    original_filename=file_result.entry.path.name,
                    file_hash=file_result.file_hash,
                    file_type=file_result.entry.path.suffix.lower().lstrip("."),
                    source_type=file_result.entry.source_type,
                    country_scope=", ".join(file_result.entry.country_scope) or None,
                    period_start=file_result.entry.period_start,
                    period_end=file_result.entry.period_end,
                )
            )
        )
    return BatchProfileSummary(validation=validation, profiles=profiles)


def load_profiles(profiles: list[WorkbookProfile], *, source: str = "all") -> list[LoadResult]:
    results: list[LoadResult] = []
    for profile in profiles:
        if source != "all" and profile.source_type != source:
            continue
        loader = LOADERS.get(profile.source_type)
        if not loader:
            continue
        result = loader(profile)
        result.summaries["_profile_path"] = str(profile.path)
        results.append(result)
    _annotate_doctor_reconciliation_quality(results)
    return results


def _annotate_doctor_reconciliation_quality(results: list[LoadResult]) -> None:
    request_records = [
        record
        for result in results
        if result.source_type == "consolidation"
        for record in result.records
    ]
    if not request_records:
        return
    for result in results:
        if result.source_type != "doctor_contract":
            continue
        matches = reconcile_doctor_interventions(result.records, request_records)
        result.summaries["unjoined_row_count"] = sum(
            1 for match in matches if match.match_method == "unmatched"
        )
        result.summaries["weak_join_count"] = sum(
            1 for match in matches if 0 < match.confidence < 1
        )


def ingest_workbooks(
    data_dir: Path | None = None,
    *,
    source: str = "all",
    dry_run: bool = False,
) -> IngestionSummary:
    settings = get_settings()
    root = data_dir or settings.data_dir
    source_files = _filter_sources(
        discover_source_files(root, require_gitignored_path=data_dir is None),
        source,
    )
    profiles = [profile_source_file(source_file) for source_file in source_files]
    load_results = load_profiles(profiles, source=source)
    summary = IngestionSummary(profiles=profiles, load_results=load_results, dry_run=dry_run)
    if dry_run:
        return summary
    run_id = _persist(source_files, profiles, load_results, summary)
    return IngestionSummary(
        profiles=profiles,
        load_results=load_results,
        dry_run=dry_run,
        ingestion_run_id=run_id,
    )


def ingest_manifest_batch(manifest_path: Path, *, dry_run: bool = False) -> IngestionSummary:
    batch = profile_manifest_batch(manifest_path)
    profiles = batch.profiles
    load_results = load_profiles(profiles)
    source_files = [
        SourceFile(
            path=file_result.entry.path,
            original_filename=file_result.entry.path.name,
            file_hash=str(file_result.file_hash),
            file_type=file_result.entry.path.suffix.lower().lstrip("."),
            source_type=file_result.entry.source_type,
            country_scope=", ".join(file_result.entry.country_scope) or None,
            period_start=file_result.entry.period_start,
            period_end=file_result.entry.period_end,
        )
        for file_result in batch.validation.accepted_files
        if file_result.file_hash
    ]
    summary = IngestionSummary(profiles=profiles, load_results=load_results, dry_run=dry_run)
    if dry_run:
        return summary
    run_id = _persist(
        source_files,
        profiles,
        load_results,
        summary,
        triggered_by="dashboard_upload",
    )
    refresh_dashboard_views()
    return IngestionSummary(
        profiles=profiles,
        load_results=load_results,
        dry_run=False,
        ingestion_run_id=run_id,
    )


def refresh_dashboard_views() -> None:
    with session_scope() as session:
        session.execute(text("select refresh_dashboard_materialized_views()"))


def _persist(
    source_files: list[SourceFile],
    profiles: list[WorkbookProfile],
    load_results: list[LoadResult],
    summary: IngestionSummary,
    *,
    triggered_by: str = "local_cli",
) -> str:
    settings = get_settings()
    source_by_hash = {source_file.file_hash: source_file for source_file in source_files}
    result_by_type_and_path = {
        (result.source_type, str(result.summaries.get("_profile_path"))): result
        for result in load_results
    }
    with session_scope() as session:
        audit = AuditRepository(session)
        canonical = CanonicalRepository(session)
        rcpa = RcpaRepository(session)
        run_id = audit.create_run(triggered_by=triggered_by)
        for profile in profiles:
            source_file = source_by_hash[profile.file_hash]
            source_file_id = audit.upsert_source_file(source_file, profile)
            result = result_by_type_and_path.get((profile.source_type, str(profile.path)))
            if result is None:
                audit.upsert_run_file(
                    ingestion_run_id=run_id,
                    source_file_id=source_file_id,
                    profile=profile,
                    status="profiled",
                    rows_seen=profile.total_rows_seen,
                    rows_loaded=0,
                    rows_skipped=0,
                    warnings=len(profile.warnings),
                    errors=0,
                )
                continue
            warnings = sum(1 for issue in result.issues if issue.severity == "warning")
            errors = sum(1 for issue in result.issues if issue.severity == "error")
            audit.upsert_run_file(
                ingestion_run_id=run_id,
                source_file_id=source_file_id,
                profile=profile,
                status="loaded" if not errors else "failed",
                rows_seen=result.rows_seen,
                rows_loaded=result.rows_loaded,
                rows_skipped=result.rows_skipped,
                warnings=warnings,
                errors=errors,
            )
            audit.insert_validation_issues(
                ingestion_run_id=run_id,
                source_file_id=source_file_id,
                issues=result.issues,
            )
            if result.source_type == "planner":
                canonical.insert_plan_events(
                    ingestion_run_id=run_id, source_file_id=source_file_id, records=result.records
                )
                audit.update_source_file_period_from_canonical(source_file_id)
            elif result.source_type == "execution_snapshot":
                canonical.insert_execution_snapshots(
                    ingestion_run_id=run_id, source_file_id=source_file_id, records=result.records
                )
                audit.update_source_file_period_from_canonical(source_file_id)
            elif result.source_type == "consolidation":
                request_ids = canonical.insert_execution_requests(
                    ingestion_run_id=run_id, source_file_id=source_file_id, records=result.records
                )
                canonical.insert_request_doctors(
                    request_ids,
                    result.summaries.get("request_doctors", []),
                )
                derived_snapshots = derive_sri_lanka_may_snapshots(result.records)
                if derived_snapshots:
                    canonical.insert_execution_snapshots(
                        ingestion_run_id=run_id,
                        source_file_id=source_file_id,
                        records=derived_snapshots,
                    )
                audit.update_source_file_period_from_canonical(source_file_id)
            elif result.source_type in {"doctor_contract", "ers_conference"}:
                canonical.insert_doctor_engagement_facts(
                    ingestion_run_id=run_id,
                    source_file_id=source_file_id,
                    records=result.records,
                )
                audit.update_source_file_period_from_canonical(source_file_id)
            elif result.source_type == "msl_doctor_master":
                enrichment_summary = canonical.insert_msl_doctor_master_records(
                    ingestion_run_id=run_id,
                    source_file_id=source_file_id,
                    records=result.records,
                )
                result.summaries.update(enrichment_summary)
            elif result.source_type == "rcpa":
                detail_export_path = export_rcpa_detail_records(
                    profile=profile,
                    records=result.summaries.get("rcpa_detail_records", []),
                    processed_dir=settings.processed_data_dir,
                )
                if detail_export_path is not None:
                    result.summaries["rcpa_detail_export_path"] = str(detail_export_path)
                rcpa.replace_rcpa_doctor_month_summaries(
                    ingestion_run_id=run_id, source_file_id=source_file_id, records=result.records
                )
                rcpa.replace_rcpa_doctor_brand_summaries(
                    ingestion_run_id=run_id,
                    source_file_id=source_file_id,
                    records=result.summaries.get("rcpa_doctor_brand_summary", []),
                )
                rcpa.replace_rcpa_country_brand_month_summaries(
                    ingestion_run_id=run_id,
                    source_file_id=source_file_id,
                    records=result.summaries.get("rcpa_country_brand_month_summary", []),
                )
                rcpa.upsert_doctors_from_rcpa(result.records)
                audit.update_source_file_period_from_canonical(source_file_id)
        EventMatcher(EventMatchRepository(session)).reconcile(run_id)
        status = "completed"
        if summary.error_count:
            status = "failed"
        elif summary.warning_count:
            status = "completed_with_warnings"
        audit.complete_run(
            ingestion_run_id=run_id,
            status=status,
            source_file_count=len(profiles),
            total_rows_seen=summary.rows_seen,
            total_rows_loaded=summary.rows_loaded,
            total_rows_skipped=summary.rows_skipped,
            warning_count=summary.warning_count,
            error_count=summary.error_count,
            summary_json=summary.to_json(),
        )
        return run_id


def _filter_sources(source_files: list[SourceFile], source: str) -> list[SourceFile]:
    if source == "all":
        return source_files
    return [source_file for source_file in source_files if source_file.source_type == source]


def _reportable_summaries(summaries: dict[str, Any]) -> dict[str, Any]:
    reportable: dict[str, Any] = {}
    for key, value in summaries.items():
        if key.startswith("_"):
            continue
        if isinstance(value, str | int | float | bool) or value is None:
            reportable[key] = value
    return reportable
