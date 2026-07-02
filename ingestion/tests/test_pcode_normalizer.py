from ingestion.normalizers.pcodes import normalize_pcode


def test_pcode_normalizer_preserves_text_and_numeric_ids() -> None:
    assert normalize_pcode("00123").value == "00123"
    assert normalize_pcode("929400.0").value == "929400"
    assert normalize_pcode(929400.0).value == "929400"


def test_pcode_normalizer_rejects_blank_and_zero_like_values() -> None:
    assert normalize_pcode("").value is None
    assert normalize_pcode("nan").value is None
    assert normalize_pcode("0.0").value is None

