from __future__ import annotations

import re
from dataclasses import dataclass, field
from difflib import SequenceMatcher

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

TOPIC_ALIASES: dict[str, tuple[str, ...]] = {
    "execution": (
        "exec",
        "executn",
        "excecution",
        "exection",
        "xecution",
        "mathed",
        "mached",
        "mach",
        "matcheds",
        "actiondue",
    ),
    "workflow": (
        "flow",
        "work flow",
        "wrkflow",
        "aproval",
        "approvl",
        "confirmaton",
        "confimation",
        "pendng",
        "bottlneck",
        "blocker",
        "blockers",
        "delay",
        "delays",
        "stuck",
    ),
    "intervention": (
        "interventon",
        "intervetion",
        "programme",
        "programmes",
        "conf",
        "confrence",
        "conferance",
        "conferrence",
    ),
    "budget": (
        "budgt",
        "buget",
        "budjet",
        "spnd",
        "spent",
        "spending",
        "expence",
        "expences",
        "expenditure",
        "money",
        "varience",
        "currncy",
        "curency",
    ),
    "doctor": (
        "docter",
        "docotr",
        "doctr",
        "drs",
        "hcps",
        "sponser",
        "sponsered",
        "sponserd",
        "sponship",
        "sponsorhip",
        "sponorship",
        "sponsrship",
        "sponserhip",
        "perscription",
        "prescrption",
        "presciption",
        "rx",
        "quadrent",
        "qadrant",
        "qudrant",
        "p-code",
        "p code",
        "nofee",
        "no fees",
        "contrct",
        "contrcted",
        "agreement",
        "honorarium",
        "honorariums",
    ),
    "territory": (
        "teritory",
        "terriotry",
        "terretory",
        "patches",
        "locaton",
        "area",
        "areas",
        "region",
        "regions",
        "underservd",
        "overservd",
    ),
    "quality": (
        "qualty",
        "qaulity",
        "validaton",
        "valdiation",
        "coverge",
        "unmatced",
        "freshnes",
        "missng",
        "wrong",
        "bad",
        "issue",
        "issues",
    ),
}

QUESTION_INTENT_TERMS = {
    "why",
    "what",
    "which",
    "who",
    "where",
    "how",
    "show",
    "tell",
    "explain",
    "summarize",
    "summarise",
    "compare",
    "recommend",
    "suggest",
    "rank",
    "find",
    "list",
    "analyze",
    "analyse",
    "review",
    "diagnose",
    "debug",
    "investigate",
}

IN_APP_ANCHORS = {
    "dashboard",
    "app",
    "data",
    "kpi",
    "metrics",
    "table",
    "chart",
    "rows",
    "filters",
    "supabase",
    "cipla",
    "emeu",
    "pbp",
    "execai",
    "doctor",
    "doctors",
    "hcp",
    "hcps",
    "roi",
    "spend",
    "budget",
    "territory",
    "territories",
    "workflow",
    "rcpa",
    "sponsorship",
    "execution",
}

EXTERNAL_TOPIC_TERMS = {
    "cricket",
    "football",
    "weather",
    "stock",
    "stocks",
    "movie",
    "movies",
    "song",
    "lyrics",
    "recipe",
    "election",
    "news",
    "flight",
    "hotel",
    "restaurant",
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
    normalized = normalize_question_text(question)
    topics = infer_topics(question, page_context)
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


def normalize_question_text(question: str) -> str:
    normalized = question.lower()
    normalized = re.sub(r"[^a-z0-9]+", " ", normalized)
    return re.sub(r"\s+", " ", normalized).strip()


def infer_topics(question: str, page_context: str | None = None) -> list[str]:
    normalized_question = normalize_question_text(question)
    tokens = set(normalized_question.split())
    topics = [
        topic
        for topic, keywords in TOPIC_KEYWORDS.items()
        if _matches_topic(normalized_question, tokens, keywords, TOPIC_ALIASES.get(topic, ()))
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
    if not topics and _is_in_app_ambiguous_question(tokens):
        topics.extend(["execution", "workflow", "budget", "doctor", "quality"])
    return list(dict.fromkeys(topics))


def looks_external_without_dashboard_anchor(question: str) -> bool:
    normalized = normalize_question_text(question)
    tokens = set(normalized.split())
    return (
        bool(tokens & EXTERNAL_TOPIC_TERMS)
        and not bool(tokens & IN_APP_ANCHORS)
        and not bool(infer_topics(question))
    )


def _matches_topic(
    normalized_question: str,
    tokens: set[str],
    keywords: tuple[str, ...],
    aliases: tuple[str, ...],
) -> bool:
    if any(_phrase_in_question(keyword, normalized_question) for keyword in (*keywords, *aliases)):
        return True
    normalized_keywords = [normalize_question_text(keyword) for keyword in keywords]
    keyword_tokens = {
        token
        for keyword in normalized_keywords
        for token in keyword.split()
        if len(token) >= 6
    }
    return any(_near_token_match(token, keyword_tokens) for token in tokens if len(token) >= 6)


def _phrase_in_question(phrase: str, normalized_question: str) -> bool:
    normalized_phrase = normalize_question_text(phrase)
    if not normalized_phrase:
        return False
    return re.search(rf"\b{re.escape(normalized_phrase)}\b", normalized_question) is not None


def _near_token_match(token: str, keyword_tokens: set[str]) -> bool:
    threshold = 0.78 if len(token) >= 8 else 0.8
    return any(SequenceMatcher(None, token, keyword).ratio() >= threshold for keyword in keyword_tokens)


def _is_in_app_ambiguous_question(tokens: set[str]) -> bool:
    if not tokens:
        return False
    if tokens & EXTERNAL_TOPIC_TERMS:
        return False
    return bool(tokens & QUESTION_INTENT_TERMS) and bool(tokens & IN_APP_ANCHORS)


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
