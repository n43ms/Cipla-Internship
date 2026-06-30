# ruff: noqa: E501
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
        "dashboardPointers": [],
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


def dashboard_pointers_for_topics(
    topics: list[str],
    context: dict[str, Any],
) -> list[dict[str, Any]]:
    selected = topics or _topics_from_context(context)
    pointers: list[dict[str, Any]] = []
    for topic in selected:
        pointers.extend(_POINTERS_BY_TOPIC.get(topic, []))
    if not pointers:
        pointers = _GENERAL_POINTERS
    return _dedupe_pointers(pointers)


def deterministic_answer(
    question: str,
    context: dict[str, Any],
    reason: str | None = None,
) -> dict[str, Any]:
    topics = route_question(question).topics
    pointers = dashboard_pointers_for_topics(topics, context)
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
        "Use the dashboard pointers below to verify the exact cards, tables, and rows "
        "behind the answer before making a final business decision."
    )
    return {
        "answer": answer,
        "dashboardPointers": pointers,
        "limitations": limitations,
        "confidence": confidence_for_context(context),
        "providerUsed": "deterministic",
        "modelUsed": "rules",
        "fallbackUsed": True,
    }


_GENERAL_POINTERS = [
    {
        "page": "Execution",
        "section": "Top KPI cards and planned-vs-actual chart",
        "detail": "Use the execution page as the first source for planned, matched, executed, action-due, and match-coverage questions.",
        "reason": "General execution questions usually depend on the primary execution reconciliation layer.",
    },
    {
        "page": "Data Quality",
        "section": "Source files, unmatched records, and validation issues",
        "detail": "Check the data-quality page when an answer mentions weak matching, missing fields, stale ingestion, or source limitations.",
        "reason": "Most ambiguous answers need validation against ingestion and matching health.",
    },
]

_POINTERS_BY_TOPIC: dict[str, list[dict[str, str]]] = {
    "execution": [
        {
            "page": "Execution",
            "section": "KPI cards",
            "detail": "Review Planned, Matched, Executed, Action due, and Match coverage cards.",
            "reason": "These cards show whether the issue is planning volume, matching coverage, or actual execution evidence.",
        },
        {
            "page": "Execution",
            "section": "Planned vs engaged HCPs chart",
            "detail": "Use this chart for HCP-level execution and engagement-rate questions.",
            "reason": "HCP execution can differ from event execution, especially when matched rows have partial engagement evidence.",
        },
        {
            "page": "Execution",
            "section": "Execution event matrix table",
            "detail": "Sort/filter the event rows by match status, execution status, unmatched reason, country, and month.",
            "reason": "Specific event-level questions need row evidence, not just summary cards.",
        },
    ],
    "workflow": [
        {
            "page": "Execution",
            "section": "Workflow status cards",
            "detail": "Check Pending requests, Pending reports, Reports approved, and Reports correction.",
            "reason": "These show where governance is stuck after a request is created.",
        },
        {
            "page": "Execution",
            "section": "Request approval/confirmation and post approval/confirmation panels",
            "detail": "Compare approval, confirmation, pending, rejected, deleted, and sent-for-correction counts.",
            "reason": "Workflow bottlenecks are split across request-stage and post-event-stage status.",
        },
        {
            "page": "Execution",
            "section": "Workflow request table",
            "detail": "Open the request rows for rep name, intervention type, owner stage, expense submitted date, and expense confirmed date.",
            "reason": "Specific workflow questions require the individual request rows behind the aggregate status counts.",
        },
    ],
    "intervention": [
        {
            "page": "Execution",
            "section": "Intervention request mix chart",
            "detail": "Use the chart to compare request, matched, executed-request, executed-snapshot, action-due, and pending-report volumes by intervention type.",
            "reason": "Intervention mix questions depend on comparing request volume with execution and reporting evidence.",
        },
        {
            "page": "Execution",
            "section": "Intervention mix table",
            "detail": "Check each intervention type/subtype row for requests, executed evidence, action-due evidence, approved count, pending report count, spend, and FX status.",
            "reason": "The table is the auditable source for specific intervention category comparisons.",
        },
    ],
    "budget": [
        {
            "page": "Budget",
            "section": "Budget summary cards",
            "detail": "Review planned budget, confirmed contracted amount, BTU spend, BTC spend, actual spend, unspent gap, and overrun.",
            "reason": "Budget questions need the finance-specific totals rather than execution-only counts.",
        },
        {
            "page": "Budget",
            "section": "BTU/BTC split and variance visuals",
            "detail": "Use these cards/charts for direct HCP spend, overhead spend, and reconciliation issues.",
            "reason": "BTU/BTC questions require the split between direct HCP spend and overhead spend.",
        },
        {
            "page": "Budget",
            "section": "Event gap table",
            "detail": "Sort/filter rows by unspent gap, overrun, spend-without-plan, plan-without-spend, currency, and FX status.",
            "reason": "Specific budget exceptions are row-level issues and should be verified in the event gap table.",
        },
    ],
    "doctor": [
        {
            "page": "Doctor ROI",
            "section": "ROI summary cards",
            "detail": "Check total doctors, dark horses, no-RCPA count, missing FX count, and provisional FX count.",
            "reason": "Doctor opportunity questions need both engagement/spend and RCPA coverage context.",
        },
        {
            "page": "Doctor ROI",
            "section": "Quadrant matrix",
            "detail": "Use the quadrant view to compare high-value engaged doctors, dark horses, low-reward doctors, and insufficient-data doctors.",
            "reason": "The quadrant view explains the opportunity type behind each doctor segment.",
        },
        {
            "page": "Doctor ROI",
            "section": "Doctor ROI table and doctor detail drawer",
            "detail": "Open individual doctors for Pcode, name, specialty, class, spend, prescriptions, RCPA trend, brand mix, and engagement history.",
            "reason": "Specific doctor recommendations must be verified at doctor-row and detail-drawer level.",
        },
    ],
    "quality": [
        {
            "page": "Data Quality",
            "section": "Ingestion and source-file cards",
            "detail": "Check loaded files, row counts, rows skipped, latest ingestion status, and stale-ingestion warnings.",
            "reason": "Source freshness and load completeness determine whether dashboard answers are trustworthy.",
        },
        {
            "page": "Data Quality",
            "section": "Validation issues and unmatched records",
            "detail": "Review validation warnings/errors, unmatched source type, reason code, candidate match, and confidence.",
            "reason": "Matching and validation issues explain why execution, budget, or workflow counts may look incomplete.",
        },
        {
            "page": "Data Quality",
            "section": "FX quality and coverage panels",
            "detail": "Check currency code, rate status, rate-to-USD, source, missing FX, provisional FX, Pcode coverage, and RCPA coverage.",
            "reason": "Financial and doctor ROI answers are only as reliable as FX, Pcode, and RCPA coverage.",
        },
    ],
}


def _topics_from_context(context: dict[str, Any]) -> list[str]:
    return [
        topic
        for topic, section in (
            ("execution", "execution"),
            ("workflow", "workflow"),
            ("intervention", "interventions"),
            ("budget", "budget"),
            ("doctor", "doctorRoi"),
            ("quality", "dataQuality"),
        )
        if isinstance(context.get(section), dict)
    ]


def _dedupe_pointers(pointers: list[dict[str, Any]]) -> list[dict[str, Any]]:
    seen: set[tuple[str, str, str]] = set()
    result: list[dict[str, Any]] = []
    for pointer in pointers:
        key = (
            str(pointer.get("page")),
            str(pointer.get("section")),
            str(pointer.get("detail")),
        )
        if key in seen:
            continue
        seen.add(key)
        result.append(pointer)
    return result
