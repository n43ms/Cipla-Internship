from datetime import date

from ingestion.normalizers.rcpa_provenance import rcpa_mapping_provenance


def test_rcpa_mapping_before_cutoff_is_manual_legacy() -> None:
    provenance = rcpa_mapping_provenance(
        month_start_date=date(2025, 10, 1),
        pcode_present=True,
    )

    assert provenance.mapping_provenance == "manual_legacy"
    assert "2025-11-01" in provenance.mapping_note


def test_rcpa_mapping_after_cutoff_is_system_supplied_when_pcode_exists() -> None:
    provenance = rcpa_mapping_provenance(
        month_start_date=date(2025, 11, 1),
        pcode_present=True,
    )

    assert provenance.mapping_provenance == "system_supplied"


def test_source_mapping_method_overrides_cutoff_when_present() -> None:
    provenance = rcpa_mapping_provenance(
        month_start_date=date(2025, 10, 1),
        pcode_present=True,
        source_mapping_method="system",
    )

    assert provenance.mapping_provenance == "system_supplied"


def test_missing_pcode_mapping_provenance_is_unknown() -> None:
    provenance = rcpa_mapping_provenance(
        month_start_date=date(2026, 1, 1),
        pcode_present=False,
    )

    assert provenance.mapping_provenance == "unknown"
