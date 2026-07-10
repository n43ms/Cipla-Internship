from ingestion.normalizers.engagements import classify_engagement


def test_classifies_no_fee_as_engagement_not_sponsorship() -> None:
    result = classify_engagement("No Fee Agreement")

    assert result.engagement_class == "no_fee"
    assert result.confidence == 1.0


def test_classifies_paid_service_engagements() -> None:
    assert classify_engagement("Speaker Agreement").engagement_class == "paid_speaker"
    assert classify_engagement("Consultancy Agreement").engagement_class == "paid_consultancy"
    assert classify_engagement("Advisory Board").engagement_class == "paid_advisory"
    assert classify_engagement("Paid Honorarium").engagement_class == "paid_speaker"


def test_classification_records_reason_and_confidence() -> None:
    result = classify_engagement("Unmapped Activity")

    assert result.engagement_class == "unclassified"
    assert result.reason
    assert result.confidence == 0.3
