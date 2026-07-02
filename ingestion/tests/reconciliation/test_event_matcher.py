from ingestion.reconciliation.event_matcher import EventMatcher


class FakeRepository:
    def __init__(self) -> None:
        self.rows = []

    def latest_ingestion_run_id(self) -> str:
        return "run-1"

    def delete_matches_for_run(self, ingestion_run_id: str) -> None:
        assert ingestion_run_id == "run-1"

    def event_scopes(self) -> list[dict]:
        return [{"country_id": "country-1", "calendar_month_id": "month-1"}]

    def plan_events(self, country_id: str, calendar_month_id: str) -> list[dict]:
        return [
            {"id": "plan-1", "event_name": "Diabetes CME - Apr", "event_type": "CME"},
            {"id": "plan-ignored", "event_name": "Grand Total", "event_type": None},
        ]

    def execution_snapshots(self, country_id: str, calendar_month_id: str) -> list[dict]:
        return [{"id": "snapshot-1", "event_name": "Diabetes CME", "event_type": "CME"}]

    def execution_requests(self, country_id: str, calendar_month_id: str) -> list[dict]:
        return [{"id": "request-1", "event_name": "Unplanned Pharmacy Program", "event_type": "PBP"}]

    def match_row(self, **kwargs):
        return kwargs

    def insert_matches(self, rows: list[dict]) -> None:
        self.rows = rows


def test_event_matcher_creates_matched_and_unmatched_records() -> None:
    repository = FakeRepository()
    count = EventMatcher(repository).reconcile()

    assert count == 3
    assert repository.rows[0]["match_status"] == "matched"
    assert repository.rows[0]["plan_event_id"] == "plan-1"
    assert repository.rows[0]["execution_snapshot_id"] == "snapshot-1"
    assert repository.rows[1]["match_status"] == "ignored"
    assert repository.rows[2]["match_status"] == "unmatched_request"
