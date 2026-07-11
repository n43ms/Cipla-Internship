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


def test_rcpa_repository_writes_doctor_month_summary() -> None:
    session = FakeSession()
    repository = RcpaRepository(session)  # type: ignore[arg-type]
    repository.replace_rcpa_doctor_month_summaries(
        ingestion_run_id="run-id",
        source_file_id="source-id",
        records=[
            {
                "country": "Sri Lanka",
                "month_start_date": "2026-05-01",
                "pcode_raw": "00123",
                "pcode_normalized": "00123",
                "doctor_name": "Dr Example",
                "speciality": "Cardiology",
                "doctor_class": "A",
                "patch_name": "Colombo 1",
                "active_status": "Active",
                "own_prescription_qty": 10,
                "own_prescription_value_local": 3100,
                "competitor_prescription_qty": 2,
                "competitor_prescription_value_local": 600,
                "total_prescription_qty": 12,
                "total_prescription_value_local": 3700,
                "currency_code": "LKR",
                "row_count_aggregated": 3,
            }
        ],
    )

    sql = "\n".join(call[0] for call in session.calls)
    assert "delete from rcpa_doctor_month_summary" in sql
    assert "insert into rcpa_doctor_month_summary" in sql
    assert "on conflict" in sql
    assert "source_file_id, country_id, calendar_month_id, pcode_normalized, currency_code" in sql


def test_rcpa_repository_writes_brand_summary_tables() -> None:
    session = FakeSession()
    repository = RcpaRepository(session)  # type: ignore[arg-type]
    repository.replace_rcpa_doctor_brand_summaries(
        ingestion_run_id="run-id",
        source_file_id="source-id",
        records=[
            {
                "country": "Sri Lanka",
                "first_month_start_date": "2026-04-01",
                "last_month_start_date": "2026-05-01",
                "pcode_normalized": "00123",
                "doctor_name": "Dr Example",
                "brand_group": "Brand",
                "own_or_competitor": "own",
                "prescription_qty": 10,
                "prescription_value_local": 3100,
                "currency_code": "LKR",
                "row_count_aggregated": 1,
            }
        ],
    )
    repository.replace_rcpa_country_brand_month_summaries(
        ingestion_run_id="run-id",
        source_file_id="source-id",
        records=[
            {
                "country": "Sri Lanka",
                "month_start_date": "2026-05-01",
                "brand_group": "Brand",
                "own_or_competitor": "own",
                "prescription_qty": 10,
                "prescription_value_local": 3100,
                "currency_code": "LKR",
                "row_count_aggregated": 1,
            }
        ],
    )

    sql = "\n".join(call[0] for call in session.calls)
    assert "delete from rcpa_doctor_brand_summary" in sql
    assert "insert into rcpa_doctor_brand_summary" in sql
    assert "source_file_id,\n                country_id,\n                pcode_normalized" in sql
    assert "prescription_qty = excluded.prescription_qty" in sql
    assert "first_calendar_month_id" not in sql
    assert "last_calendar_month_id" not in sql
    assert "doctor_name, brand_group" not in sql
    assert "delete from rcpa_country_brand_month_summary" in sql
    assert "insert into rcpa_country_brand_month_summary" in sql


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
