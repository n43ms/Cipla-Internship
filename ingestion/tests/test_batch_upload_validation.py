import json
from pathlib import Path

from openpyxl import Workbook

from ingestion.orchestrator import profile_manifest_batch
from ingestion.source_manifest import load_source_manifest, validate_source_manifest


def _write_consolidation(path: Path) -> None:
    workbook = Workbook()
    sheet = workbook.active
    sheet.title = "Working"
    sheet.append(
        ["DIVISION", "REQ_ID", "INTERVENTION NAME", "TOTAL ACTUAL EXPENSES FOR INTERVENTION"]
    )
    sheet.append(["Sri Lanka", "REQ-1", "Sponsorship Event", 100])
    path.parent.mkdir(parents=True, exist_ok=True)
    workbook.save(path)


def _write_manifest(path: Path, package_root: Path, files: list[dict[str, object]]) -> None:
    path.write_text(
        json.dumps(
            {
                "received_package_path": str(package_root),
                "owner": "Abhijeet Mudila/EMEU/PBP",
                "files": files,
            }
        ),
        encoding="utf-8",
    )


def test_batch_upload_validation_quarantines_duplicate_file_hashes(tmp_path: Path) -> None:
    package_root = tmp_path / "package"
    first = package_root / "raw_consolidated_a.xlsx"
    second = package_root / "raw_consolidated_b.xlsx"
    _write_consolidation(first)
    second.write_bytes(first.read_bytes())
    manifest_path = tmp_path / "manifest.json"
    _write_manifest(
        manifest_path,
        package_root,
        [
            {
                "label": "raw_consolidated_a",
                "path": str(first),
                "source_type": "consolidation",
                "raw_or_cleaned": "raw",
            },
            {
                "label": "raw_consolidated_b",
                "path": str(second),
                "source_type": "consolidation",
                "raw_or_cleaned": "raw",
            },
        ],
    )

    result = validate_source_manifest(load_source_manifest(manifest_path))

    assert result.accepted_files[0].entry.label == "raw_consolidated_a"
    assert result.quarantined_files[0].entry.label == "raw_consolidated_b"
    assert result.quarantined_files[0].issues[0].error_code == "duplicate_file_hash"


def test_batch_upload_validation_quarantines_wrong_report_type(tmp_path: Path) -> None:
    package_root = tmp_path / "package"
    workbook = package_root / "raw_consolidated.xlsx"
    _write_consolidation(workbook)
    manifest_path = tmp_path / "manifest.json"
    _write_manifest(
        manifest_path,
        package_root,
        [
            {
                "label": "declared_rcpa_but_consolidated",
                "path": str(workbook),
                "source_type": "rcpa",
                "raw_or_cleaned": "raw",
            }
        ],
    )

    result = validate_source_manifest(load_source_manifest(manifest_path))

    assert result.accepted_files == []
    assert result.quarantined_files[0].issues[0].error_code == "wrong_source_type"


def test_batch_profile_orchestrator_profiles_only_accepted_files(tmp_path: Path) -> None:
    package_root = tmp_path / "package"
    workbook = package_root / "raw_consolidated.xlsx"
    _write_consolidation(workbook)
    manifest_path = tmp_path / "manifest.json"
    _write_manifest(
        manifest_path,
        package_root,
        [
            {
                "label": "raw_consolidated",
                "path": str(workbook),
                "source_type": "consolidation",
                "raw_or_cleaned": "raw",
                "country_scope": ["Sri Lanka"],
            }
        ],
    )

    summary = profile_manifest_batch(manifest_path)

    assert summary.accepted_count == 1
    assert summary.quarantined_count == 0
    assert summary.profiles[0].source_type == "consolidation"
    assert summary.profiles[0].country_scope == "Sri Lanka"
