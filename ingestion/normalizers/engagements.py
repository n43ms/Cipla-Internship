from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class EngagementClassification:
    engagement_class: str
    reason: str
    confidence: float


def classify_engagement(*labels: object) -> EngagementClassification:
    text = _label_text(*labels)
    if "no fee" in text or "no-fee" in text:
        return EngagementClassification(
            engagement_class="no_fee",
            reason="No Fee Agreement is engagement evidence, not sponsorship by default.",
            confidence=1.0,
        )
    if "speaker" in text or "honorarium" in text:
        return EngagementClassification(
            engagement_class="paid_speaker",
            reason="Speaker or honorarium label maps to paid engagement evidence.",
            confidence=0.95,
        )
    if "consult" in text:
        return EngagementClassification(
            engagement_class="paid_consultancy",
            reason="Consultancy label maps to paid engagement evidence.",
            confidence=0.95,
        )
    if "advisory" in text or "advisory board" in text:
        return EngagementClassification(
            engagement_class="paid_advisory",
            reason="Advisory board label maps to paid engagement evidence.",
            confidence=0.95,
        )
    if "conference" in text:
        return EngagementClassification(
            engagement_class="conference",
            reason="Conference label maps to sponsorship classification when eligible.",
            confidence=0.9,
        )
    return EngagementClassification(
        engagement_class="unclassified",
        reason="No observed engagement/service label matched deterministic rules.",
        confidence=0.3,
    )


def _label_text(*labels: object) -> str:
    return " ".join(str(label or "").strip().casefold() for label in labels if label is not None)
