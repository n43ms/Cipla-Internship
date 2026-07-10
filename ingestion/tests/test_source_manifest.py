import json
from pathlib import Path

from openpyxl import Workbook

from ingestion.source_manifest import load_source_manifest


def _write_xlsx(path: Path, headers: list[str]) -> None:
    workbook = Workbook()
    sheet = workbook.active
    sheet.title = "Working"
    sheet.append(headers)
    sheet.append(["Sri Lanka", "REQ-1", "Event", 100])
    path.parent.mkdir(parents=True, exist_ok=True)
    workbook.save(path)


def test_source_manifest_loads_labeled_batch_with_resolved_paths(tmp_path: Path) -> None:
    package_root = tmp_path / "received"
    workbook_path = package_root / "Raw Reports -Point 1" / "consolidated.xlsx"
    _write_xlsx(
        workbook_path,
        ["DIVISION", "REQ_ID", "INTERVENTION NAME", "TOTAL ACTUAL EXPENSES FOR INTERVENTION"],
    )
    manifest_path = tmp_path / "manifest.json"
    manifest_path.write_text(
        json.dumps(
            {
                "received_package_path": "received",
                "owner": "Abhijeet Mudila/EMEU/PBP",
                "files": [
                    {
                        "label": "raw_consolidated",
                        "path": "Raw Reports -Point 1/consolidated.xlsx",
                        "source_type": "consolidation",
                        "raw_or_cleaned": "raw",
                        "country_scope": ["Sri Lanka"],
                        "period_start": "2025-11-01",
                        "period_end": "2026-07-09",
                        "export_timestamp": "2026-07-10T12:20:00+05:30",
                    }
                ],
            }
        ),
        encoding="utf-8",
    )

    manifest = load_source_manifest(manifest_path)

    assert manifest.received_package_path == package_root.resolve()
    assert manifest.owner == "Abhijeet Mudila/EMEU/PBP"
    assert manifest.files[0].label == "raw_consolidated"
    assert manifest.files[0].path == workbook_path.resolve()
    assert manifest.files[0].source_type == "consolidation"
    assert manifest.files[0].raw_or_cleaned == "raw"
    assert manifest.files[0].country_scope == ("Sri Lanka",)
    assert manifest.files[0].owner == "Abhijeet Mudila/EMEU/PBP"
    assert manifest.files[0].period_start.isoformat() == "2025-11-01"
