from ingestion.loaders.request_doctors import split_request_doctors


def test_request_doctor_splitter_preserves_raw_and_normalized_positions() -> None:
    records = split_request_doctors(
        request_key="REQ-1",
        attendance_type="actual",
        doctors_raw="Dr A; Dr B",
        pcodes_raw="100.0; 00200",
    )

    assert len(records) == 2
    assert records[0]["pcode_normalized"] == "100"
    assert records[1]["pcode_normalized"] == "00200"
    assert records[1]["source_position"] == 2


def test_request_doctor_splitter_preserves_duplicate_and_non_numeric_pcodes() -> None:
    records = split_request_doctors(
        request_key="REQ-2",
        attendance_type="actual",
        doctors_raw="Dr A; Dr B; Dr C",
        pcodes_raw="1001; ABC-12; 1001",
    )

    assert [record["source_position"] for record in records] == [1, 2, 3]
    assert records[0]["pcode_normalized"] == "1001"
    assert records[0]["parse_status"] == "parsed"
    assert records[1]["pcode_raw"] == "ABC-12"
    assert records[1]["pcode_normalized"] == "ABC-12"
    assert records[1]["parse_status"] == "parsed"
    assert records[2]["pcode_normalized"] == "1001"


def test_request_doctor_splitter_marks_missing_pcode_when_source_has_no_pcodes() -> None:
    records = split_request_doctors(
        request_key="REQ-3",
        attendance_type="expected",
        doctors_raw="Dr Missing",
        pcodes_raw=None,
    )

    assert len(records) == 1
    assert records[0]["source_position"] == 1
    assert records[0]["doctor_name_raw"] == "Dr Missing"
    assert records[0]["pcode_normalized"] is None
    assert records[0]["parse_status"] == "missing_pcode"
