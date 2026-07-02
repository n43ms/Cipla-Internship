from __future__ import annotations

import pytest

from backend.app.services.filter_validation import (
    validate_country_month_filters,
    validate_workflow_status,
)
from backend.app.utils.errors import AppError


class _Result:
    def __init__(self, exists: bool) -> None:
        self.exists = exists

    def first(self) -> tuple[int] | None:
        return (1,) if self.exists else None


class _Session:
    def __init__(self, *, countries: set[str], months: set[str]) -> None:
        self.countries = {value.casefold() for value in countries}
        self.months = months

    def execute(self, _statement: object, params: dict[str, str]) -> _Result:
        if "country" in params:
            return _Result(params["country"].casefold() in self.countries)
        return _Result(params["month"] in self.months)


def test_validate_country_month_filters_accepts_known_scope() -> None:
    session = _Session(countries={"LK", "Sri Lanka"}, months={"2026-05"})

    validate_country_month_filters(session, country="Sri Lanka", month="2026-05")  # type: ignore[arg-type]


def test_validate_country_month_filters_rejects_unknown_country() -> None:
    session = _Session(countries={"LK"}, months={"2026-05"})

    with pytest.raises(AppError) as exc_info:
        validate_country_month_filters(session, country="Atlantis", month="2026-05")  # type: ignore[arg-type]

    assert exc_info.value.code == "invalid_filter"


def test_validate_country_month_filters_rejects_bad_month_format() -> None:
    session = _Session(countries={"LK"}, months={"2026-05"})

    with pytest.raises(AppError):
        validate_country_month_filters(session, country="LK", month="May 2026")  # type: ignore[arg-type]


def test_validate_workflow_status_rejects_unknown_status() -> None:
    with pytest.raises(AppError):
        validate_workflow_status("blocked_somewhere")
