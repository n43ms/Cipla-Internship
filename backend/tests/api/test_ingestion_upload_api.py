from io import BytesIO
from pathlib import Path

from fastapi.testclient import TestClient
from openpyxl import Workbook

from backend.app.config import get_settings
from backend.app.main import create_app
from ingestion.orchestrator import IngestionSummary


def _xlsx_bytes(headers: list[str]) -> bytes:
    workbook = Workbook()
    sheet = workbook.active
    sheet.title = "Working"
    sheet.append(headers)
    sheet.append(["Sri Lanka", "REQ-1", "Event", 100])
    output = BytesIO()
    workbook.save(output)
    return output.getvalue()


def test_upload_batch_accepts_recognized_excel_file(monkeypatch, tmp_path: Path) -> None:
    monkeypatch.setenv("UPLOAD_DATA_DIR", str(tmp_path))
    get_settings.cache_clear()
    app = create_app()
    content = _xlsx_bytes(
        ["DIVISION", "REQ_ID", "INTERVENTION NAME", "TOTAL ACTUAL EXPENSES FOR INTERVENTION"]
    )

    with TestClient(app) as client:
        response = client.post(
            "/api/ingestion/upload-batch",
            files={"files": ("consolidated.xlsx", content, "application/vnd.ms-excel")},
        )

    assert response.status_code == 200
    payload = response.json()
    assert payload["acceptedCount"] == 1
    assert payload["quarantinedCount"] == 0
    assert payload["files"][0]["sourceType"] == "consolidation"
    assert payload["manifestPath"]
    status_response = client.get(f"/api/ingestion/upload-batches/{payload['batchId']}")
    assert status_response.status_code == 200
    status_payload = status_response.json()
    assert status_payload["refreshState"] == "accepted_for_ingestion"
    assert status_payload["acceptedCount"] == 1
    get_settings.cache_clear()


def test_upload_batch_quarantines_duplicate_files(monkeypatch, tmp_path: Path) -> None:
    monkeypatch.setenv("UPLOAD_DATA_DIR", str(tmp_path))
    get_settings.cache_clear()
    app = create_app()
    content = _xlsx_bytes(
        ["DIVISION", "REQ_ID", "INTERVENTION NAME", "TOTAL ACTUAL EXPENSES FOR INTERVENTION"]
    )

    with TestClient(app) as client:
        response = client.post(
            "/api/ingestion/upload-batch",
            files=[
                ("files", ("consolidated-a.xlsx", content, "application/vnd.ms-excel")),
                ("files", ("consolidated-b.xlsx", content, "application/vnd.ms-excel")),
            ],
        )

    assert response.status_code == 200
    payload = response.json()
    assert payload["acceptedCount"] == 1
    assert payload["quarantinedCount"] == 1
    assert "Duplicate" in payload["files"][1]["reasons"][0]
    get_settings.cache_clear()


def test_accepted_upload_batch_runs_ingestion_and_updates_refresh_status(
    monkeypatch, tmp_path: Path
) -> None:
    monkeypatch.setenv("UPLOAD_DATA_DIR", str(tmp_path))
    get_settings.cache_clear()
    app = create_app()
    content = _xlsx_bytes(
        ["DIVISION", "REQ_ID", "INTERVENTION NAME", "TOTAL ACTUAL EXPENSES FOR INTERVENTION"]
    )
    calls: list[Path] = []

    def fake_ingest_manifest_batch(manifest_path: Path) -> IngestionSummary:
        calls.append(manifest_path)
        return IngestionSummary(
            profiles=[],
            load_results=[],
            dry_run=False,
            ingestion_run_id="00000000-0000-0000-0000-000000000123",
        )

    monkeypatch.setattr(
        "backend.app.services.ingestion_upload_service.ingest_manifest_batch",
        fake_ingest_manifest_batch,
    )

    with TestClient(app) as client:
        upload_response = client.post(
            "/api/ingestion/upload-batch",
            files={"files": ("consolidated.xlsx", content, "application/vnd.ms-excel")},
        )
        upload_payload = upload_response.json()
        ingest_response = client.post(
            f"/api/ingestion/upload-batches/{upload_payload['batchId']}/ingest"
        )
        status_response = client.get(
            f"/api/ingestion/upload-batches/{upload_payload['batchId']}"
        )

    assert upload_response.status_code == 200
    assert ingest_response.status_code == 200
    assert status_response.status_code == 200
    assert calls == [Path(upload_payload["manifestPath"])]
    payload = ingest_response.json()
    assert payload["refreshState"] == "views_refreshed"
    assert payload["ingestionRunId"] == "00000000-0000-0000-0000-000000000123"
    assert payload["message"] == "Supabase facts were written and materialized views were refreshed."
    assert status_response.json()["refreshState"] == "views_refreshed"
    get_settings.cache_clear()
