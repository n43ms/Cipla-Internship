from __future__ import annotations

from dataclasses import dataclass
from typing import Any

SUPPORTED_TOPIC_KEYWORDS: dict[str, tuple[str, ...]] = {
    "execution": ("execution", "planned", "matched", "action due", "action-due", "event", "hcp"),
    "workflow": ("workflow", "approval", "confirmation", "pending", "report", "bottleneck"),
    "intervention": ("intervention", "mix", "type", "program", "cme", "conference"),
    "budget": ("budget", "spend", "expense", "btu", "btc", "fx", "variance", "cost"),
    "doctor": ("doctor", "hcp", "roi", "rcpa", "prescription", "dark horse", "quadrant"),
    "quality": ("quality", "data", "validation", "coverage", "unmatched", "freshness", "missing"),
}


@dataclass(frozen=True)
class TopicDecision:
    supported: bool
    topics: list[str]
    refusal: str | None = None


def route_question(question: str) -> TopicDecision:
    normalized = question.lower()
    topics = [
        topic
        for topic, keywords in SUPPORTED_TOPIC_KEYWORDS.items()
        if any(keyword in normalized for keyword in keywords)
    ]
    if topics:
        return TopicDecision(supported=True, topics=topics)
    return TopicDecision(
        supported=False,
        topics=[],
        refusal=(
            "I can only answer questions grounded in this app's execution, workflow, "
            "intervention, budget, doctor ROI, RCPA, and data-quality metrics."
        ),
    )


def confidence_for_context(context: dict[str, Any]) -> str:
    limitations = [str(item).lower() for item in context.get("limitations", [])]
    flags = [str(item).lower() for item in context.get("dataQualityFlags", [])]
    if any("no rows" in item or "missing" in item or "unavailable" in item for item in limitations):
        return "low"
    if any("weak" in item or "missing" in item or "stale" in item for item in flags):
        return "medium"
    if limitations or flags:
        return "medium"
    return "high"


def unsupported_response(question: str, context_scope: dict[str, Any]) -> dict[str, Any]:
    decision = route_question(question)
    return {
        "answer": decision.refusal or "Unsupported question.",
        "supportingMetrics": [],
        "limitations": [
            "Unsupported question. No answer was generated because the available data "
            "cannot ground it.",
        ],
        "confidence": "low",
        "providerUsed": "deterministic",
        "modelUsed": "policy",
        "fallbackUsed": True,
        "redactionApplied": False,
        "contextScope": context_scope,
    }


def supporting_metrics_from_context(
    context: dict[str, Any],
    limit: int = 8,
) -> list[dict[str, Any]]:
    metrics: list[dict[str, Any]] = []
    for section in ("execution", "workflow", "interventions", "budget", "doctorRoi", "dataQuality"):
        payload = context.get(section)
        if not isinstance(payload, dict):
            continue
        for key, value in payload.items():
            if len(metrics) >= limit:
                return metrics
            if isinstance(value, int | float | str | bool) and key not in {"meta"}:
                metrics.append(
                    {
                        "label": _metric_label(section, key),
                        "value": value,
                        "source": section,
                    }
                )
    return metrics


def deterministic_answer(
    question: str,
    context: dict[str, Any],
    reason: str | None = None,
) -> dict[str, Any]:
    metrics = supporting_metrics_from_context(context)
    limitations = list(dict.fromkeys(str(item) for item in context.get("limitations", [])))
    if reason:
        limitations.insert(
            0,
            f"Gemini was not used: {reason}. This is a deterministic fallback answer.",
        )
    execution = context.get("execution", {}) if isinstance(context.get("execution"), dict) else {}
    workflow = context.get("workflow", {}) if isinstance(context.get("workflow"), dict) else {}
    budget = context.get("budget", {}) if isinstance(context.get("budget"), dict) else {}
    doctor = context.get("doctorRoi", {}) if isinstance(context.get("doctorRoi"), dict) else {}
    quality = context.get("dataQuality", {}) if isinstance(context.get("dataQuality"), dict) else {}
    answer = (
        "Based on the current structured dashboard data, the main risk signals are: "
        f"{execution.get('weakOrUnmatchedEvents', 0)} weak/unmatched execution records, "
        f"{workflow.get('pendingReportCount', 0)} pending reports, "
        f"{budget.get('spendWithoutPlanCount', 0)} spend-without-plan rows, "
        f"{doctor.get('darkHorseCount', 0)} dark-horse doctor opportunities, and "
        f"{quality.get('validationWarningCount', 0)} validation warnings. "
        "Use the supporting metrics and limitations below before making a final business decision."
    )
    return {
        "answer": answer,
        "supportingMetrics": metrics,
        "limitations": limitations,
        "confidence": confidence_for_context(context),
        "providerUsed": "deterministic",
        "modelUsed": "rules",
        "fallbackUsed": True,
    }


def _metric_label(section: str, key: str) -> str:
    words = "".join(
        [f" {char.lower()}" if char.isupper() else char for char in key]
    ).replace("_", " ")
    return f"{section}: {words}".strip()
