from pathlib import Path

from ingestion.models import SourceFile, ValidationIssue
from ingestion.profiler import profile_path
from ingestion.repositories.audit_repository import AuditRepository
from ingestion.tests.fixtures.build_fixtures import build


class FakeResult:
    def __init__(self, value: str = "00000000-0000-0000-0000-000000000001") -> None:
        self.value = value

    def scalar_one(self) -> str:
        return self.value


class FakeSession:
    def __init__(self) -> None:
        self.calls: list[tuple[str, object]] = []

    def execute(self, statement: object, params: object | None = None) -> FakeResult:
        self.calls.append((str(statement), params))
        return FakeResult()


def test_audit_repository_persists_run_file_and_validation_issue_shapes() -> None:
    build()
    profile = profile_path(Path("ingestion/tests/fixtures/xlsx/planner_nepal_tiny.xlsx"))
    session = FakeSession()
    repository = AuditRepository(session)  # type: ignore[arg-type]
    source_file = SourceFile(
        path=profile.path,
        original_filename=profile.original_filename,
        file_hash=profile.file_hash,
        file_type=profile.file_type,
        source_type=profile.source_type,
        country_scope=profile.country_scope,
    )

    run_id = repository.create_run()
    source_file_id = repository.upsert_source_file(source_file, profile)
    repository.upsert_run_file(
        ingestion_run_id=run_id,
        source_file_id=source_file_id,
        profile=profile,
        status="loaded",
        rows_seen=1,
        rows_loaded=1,
        rows_skipped=0,
        warnings=1,
        errors=0,
    )
    repository.insert_validation_issues(
        ingestion_run_id=run_id,
        source_file_id=source_file_id,
        issues=[
            ValidationIssue(
                severity="warning",
                error_code="test_warning",
                message="warning",
            )
        ],
    )

    sql = "\n".join(call[0] for call in session.calls)
    assert "insert into ingestion_runs" in sql
    assert "insert into source_files" in sql
    assert "insert into ingestion_run_files" in sql
    assert "insert into validation_errors" in sql

