from ingestion.repositories.rcpa_repository import RcpaRepository


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


def test_rcpa_repository_uses_explicit_aggregate_conflict_target() -> None:
    session = FakeSession()
    repository = RcpaRepository(session)  # type: ignore[arg-type]
    repository.upsert_rcpa_aggregates(
        ingestion_run_id="run-id",
        source_file_id="source-id",
        records=[
            {
                "country": "Sri Lanka",
                "month_start_date": "2026-05-01",
                "pcode_raw": "00123",
                "pcode_normalized": "00123",
                "doctor_name": "Dr Example",
                "brand_group": "Brand",
                "sku": "Brand",
                "own_or_competitor": "own",
                "prescription_qty": 10,
                "prescription_value_local": 3100,
                "currency_code": "LKR",
                "prescription_value_usd": None,
                "row_count_aggregated": 1,
            }
        ],
    )

    sql = "\n".join(call[0] for call in session.calls)
    assert "on conflict" in sql
    assert "source_file_id, country_id, calendar_month_id, pcode_normalized" in sql
    assert "brand_group, sku, own_or_competitor, currency_code" in sql


def test_rcpa_repository_upserts_doctor_master_from_aggregates() -> None:
    session = FakeSession()
    repository = RcpaRepository(session)  # type: ignore[arg-type]
    repository.upsert_doctors_from_rcpa(
        [
            {
                "country": "Sri Lanka",
                "pcode_normalized": "00123",
                "doctor_name": "Dr Example",
            }
        ]
    )

    sql = "\n".join(call[0] for call in session.calls)
    assert "insert into doctors" in sql
    assert "on conflict (country_id, pcode_normalized)" in sql
