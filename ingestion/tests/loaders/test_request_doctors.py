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

