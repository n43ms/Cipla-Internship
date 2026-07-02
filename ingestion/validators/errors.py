from __future__ import annotations

from ingestion.models import ValidationIssue


class IssueCollector:
    def __init__(self) -> None:
        self.issues: list[ValidationIssue] = []

    def add(
        self,
        severity: str,
        error_code: str,
        message: str,
        *,
        entity_type: str | None = None,
        field_name: str | None = None,
        sheet_name: str | None = None,
        row_number: int | None = None,
        raw_value: object | None = None,
    ) -> None:
        self.issues.append(
            ValidationIssue(
                severity=severity,
                error_code=error_code,
                message=message,
                entity_type=entity_type,
                field_name=field_name,
                sheet_name=sheet_name,
                row_number=row_number,
                raw_value=None if raw_value is None else str(raw_value),
            )
        )

    @property
    def warning_count(self) -> int:
        return sum(1 for issue in self.issues if issue.severity == "warning")

    @property
    def error_count(self) -> int:
        return sum(1 for issue in self.issues if issue.severity == "error")

