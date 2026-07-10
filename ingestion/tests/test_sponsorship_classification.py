from ingestion.normalizers.sponsorship import classify_sponsorship


def test_classifies_national_and_international_conference_as_sponsorship() -> None:
    national = classify_sponsorship("National Conference", "Speaker")
    international = classify_sponsorship("International Conference", "ERS")

    assert national.is_sponsorship is True
    assert national.sponsorship_class == "national_conference"
    assert international.is_sponsorship is True
    assert international.sponsorship_class == "international_conference"


def test_classifies_ers_as_international_evidence_not_separate_root() -> None:
    result = classify_sponsorship("ERS Conference")

    assert result.is_sponsorship is True
    assert result.sponsorship_class == "international_conference"
    assert "not a separate root" in result.reason


def test_does_not_classify_no_fee_as_sponsorship() -> None:
    result = classify_sponsorship("No Fee Agreement")

    assert result.is_sponsorship is False
    assert result.sponsorship_class is None
