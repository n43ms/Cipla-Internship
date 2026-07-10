from backend.app.services.ai.redaction import redact_payload, redact_text


def test_redacts_pcodes_amounts_names_and_source_snippets() -> None:
    text = (
        "Dr Arjun Perera has Pcode 123456, Contract ID C-001, and LKR 310000 spend. "
        "source row: full workbook payload should not be sent."
    )

    redacted, changed = redact_text(text)

    assert changed is True
    assert "123456" not in redacted
    assert "C-001" not in redacted
    assert "310000" not in redacted
    assert "Arjun Perera" not in redacted
    assert "full workbook payload" not in redacted
    assert "[PCODE]" in redacted
    assert "[CONTRACT_ID]" in redacted
    assert "[AMOUNT]" in redacted
    assert "[NAME]" in redacted
    assert "[SOURCE_EXCERPT]" in redacted


def test_redacts_nested_context_payload() -> None:
    payload = {"rows": [{"doctor": "Doctor Meera Shah", "value": "USD 20000", "pcode": "98765"}]}

    redacted, changed = redact_payload(payload)

    assert changed is True
    assert redacted["rows"][0]["doctor"] == "Doctor [NAME]"
    assert redacted["rows"][0]["value"] == "[AMOUNT]"
    assert redacted["rows"][0]["pcode"] == "[PCODE]"
