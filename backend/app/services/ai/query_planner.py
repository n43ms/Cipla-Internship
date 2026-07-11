from __future__ import annotations

import re
from dataclasses import dataclass, field

TOPIC_KEYWORDS: dict[str, tuple[str, ...]] = {
    "execution": ("execution", "planned", "matched", "action due", "action-due", "event", "hcp"),
    "workflow": ("workflow", "approval", "confirmation", "pending", "report", "bottleneck"),
    "intervention": ("intervention", "mix", "type", "program", "cme", "conference"),
    "budget": ("budget", "spend", "expense", "btu", "btc", "fx", "variance", "cost", "budget"),
    "doctor": (
        "doctor",
        "dr ",
        "dr.",
        "hcp",
        "roi",
        "rcpa",
        "prescription",
        "dark horse",
        "quadrant",
        "pcode",
        "sponsorship",
        "sponsored",
        "paid engagement",
        "no fee",
        "no-fee",
        "fmv",
        "contracted",
        "contract value",
    ),
    "territory": (
        "territory",
        "patch",
        "location",
        "underserved",
        "overserved",
    ),
    "quality": ("quality", "data", "validation", "coverage", "unmatched", "freshness", "missing"),
}

SECTION_BY_TOPIC = {
    "execution": "execution",
    "workflow": "workflow",
    "intervention": "interventions",
    "budget": "budget",
    "doctor": "doctorRoi",
    "territory": "territory",
    "quality": "dataQuality",
}

SUMMARY_SECTIONS = ("execution", "workflow", "budget", "doctorRoi", "dataQuality")


@dataclass(frozen=True)
class QueryPlan:
    topics: list[str]
    sections: set[str]
    detail_limit: int
    broad_limit: int
    doctor_search_terms: list[str] = field(default_factory=list)
    wants_specifics: bool = False


def plan_query(
    question: str,
    page_context: str | None = None,
    default_row_limit: int = 40,
) -> QueryPlan:
    normalized = question.lower()
    topics = _topics_for_question(normalized, page_context)
    wants_specifics = _wants_specifics(normalized)
    detail_limit = _detail_limit(default_row_limit, wants_specifics)
    sections = {SECTION_BY_TOPIC[topic] for topic in topics if topic in SECTION_BY_TOPIC}
    if not sections:
        sections = {"execution", "workflow", "budget", "doctorRoi", "dataQuality"}
    sections.update(_summary_support_sections(topics))
    return QueryPlan(
        topics=topics,
        sections=sections,
        detail_limit=detail_limit,
        broad_limit=min(8, max(5, default_row_limit // 4)),
        doctor_search_terms=_doctor_search_terms(question),
        wants_specifics=wants_specifics,
    )


def _topics_for_question(normalized_question: str, page_context: str | None) -> list[str]:
    topics = [
        topic
        for topic, keywords in TOPIC_KEYWORDS.items()
        if any(keyword in normalized_question for keyword in keywords)
    ]
    if page_context:
        page = page_context.lower()
        if page in {"doctors", "doctor", "doctor_roi"} and "doctor" not in topics:
            topics.append("doctor")
        elif page == "budget" and "budget" not in topics:
            topics.append("budget")
        elif page == "quality" and "quality" not in topics:
            topics.append("quality")
        elif page == "territory" and "territory" not in topics:
            topics.append("territory")
        elif page == "execution" and not topics:
            topics.extend(["execution", "workflow", "intervention"])
    return list(dict.fromkeys(topics))


def _summary_support_sections(topics: list[str]) -> set[str]:
    if "quality" in topics:
        return {"dataQuality"}
    if "doctor" in topics and "territory" in topics:
        return {"doctorRoi", "territory", "budget", "dataQuality"}
    if "doctor" in topics:
        return {"doctorRoi", "budget", "dataQuality"}
    if "territory" in topics:
        return {"territory", "doctorRoi", "dataQuality"}
    if "budget" in topics:
        return {"budget", "dataQuality"}
    if "execution" in topics or "workflow" in topics or "intervention" in topics:
        return {"execution", "workflow", "interventions", "dataQuality"}
    return set(SUMMARY_SECTIONS)


def _detail_limit(default_row_limit: int, wants_specifics: bool) -> int:
    base = max(5, min(int(default_row_limit or 20), 100))
    if wants_specifics:
        return min(max(base, 25), 60)
    return min(base, 20)


def _wants_specifics(normalized_question: str) -> bool:
    return any(
        marker in normalized_question
        for marker in (
            "which ",
            "who ",
            "list ",
            "name ",
            "names",
            "doctor",
            "pcode",
            "request",
            "event",
            "show ",
            "specific",
            "detail",
            "top ",
        )
    )


def _doctor_search_terms(question: str) -> list[str]:
    terms: list[str] = []
    pcode_pattern = (
        r"\b(?:pcode|p-code|doctor code|code)\s*[:#-]?\s*([A-Za-z0-9_-]{3,24})\b"
    )
    for match in re.finditer(pcode_pattern, question, flags=re.I):
        terms.append(match.group(1).strip())
    for match in re.finditer(r"\bdr\.?\s+([A-Za-z][A-Za-z .'-]{1,60})", question, flags=re.I):
        terms.append(f"Dr {match.group(1).strip()}")
    for match in re.finditer(r"\bdoctor\s+([A-Za-z][A-Za-z .'-]{2,60})", question, flags=re.I):
        candidate = match.group(1).strip()
        if not candidate.lower().startswith(("roi", "risk", "data", "details", "detail", "names")):
            terms.append(candidate)
    return list(dict.fromkeys(term for term in terms if term))
