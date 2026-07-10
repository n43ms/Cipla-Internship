from io import BytesIO
from pathlib import Path

from fastapi.testclient import TestClient
from openpyxl import Workbook

from backend.app.config import get_settings
from backend.app.main import create_app


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
