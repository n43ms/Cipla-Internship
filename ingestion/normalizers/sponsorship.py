from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class SponsorshipClassification:
    is_sponsorship: bool
    sponsorship_class: str | None
    reason: str
    confidence: float


def classify_sponsorship(*labels: object) -> SponsorshipClassification:
    text = _label_text(*labels)
    if "international conference" in text or "cipla international conference" in text:
        return SponsorshipClassification(
            is_sponsorship=True,
            sponsorship_class="international_conference",
            reason="Observed label maps International Conference to sponsorship.",
            confidence=1.0,
        )
    if "national conference" in text:
        return SponsorshipClassification(
            is_sponsorship=True,
            sponsorship_class="national_conference",
            reason="Observed label maps National Conference to sponsorship.",
            confidence=1.0,
        )
    if "ers" in text and "conference" in text:
        return SponsorshipClassification(
            is_sponsorship=True,
            sponsorship_class="international_conference",
            reason="ERS is treated as international-conference evidence, not a separate root.",
            confidence=0.9,
        )
    return SponsorshipClassification(
        is_sponsorship=False,
        sponsorship_class=None,
        reason="No National or International Conference sponsorship label was observed.",
        confidence=0.8,
    )


def _label_text(*labels: object) -> str:
    return " ".join(str(label or "").strip().casefold() for label in labels if label is not None)
