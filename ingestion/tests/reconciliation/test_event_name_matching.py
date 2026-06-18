from decimal import Decimal

from ingestion.normalizers.events import normalize_event_name
from ingestion.reconciliation.event_matcher import match_event_names


def test_event_name_normalization_removes_suffixes_punctuation_and_harmless_labels() -> None:
    assert normalize_event_name("Diabetes CME - Apr 2026 (New)") == "diabetes cme"
    assert normalize_event_name("  Cardio---Workshop, May ") == "cardio workshop"


def test_event_name_matching_uses_conservative_thresholds() -> None:
    exact = match_event_names("Diabetes CME", "diabetes cme")
    normalized = match_event_names("Diabetes CME - Apr", "Diabetes CME")
    weak = match_event_names("Cardio workshop", "Cardiology workshop")
    unmatched = match_event_names("Diabetes CME", "Pharmacy Benefit Program")

    assert exact.match_status == "matched"
    assert exact.match_method == "exact"
    assert normalized.match_status == "matched"
    assert normalized.match_method == "normalized"
    assert weak.match_status in {"matched", "weak_match"}
    assert unmatched.match_status == "unmatched"
    assert unmatched.confidence < Decimal("0.7200")


def test_event_name_matching_marks_obvious_non_business_rows_ignored() -> None:
    ignored = match_event_names("Grand Total", "Diabetes CME")

    assert ignored.match_status == "ignored"
    assert ignored.match_method == "ignored"
