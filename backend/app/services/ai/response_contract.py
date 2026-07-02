from __future__ import annotations

import json
import re
from typing import Any

from backend.app.services.ai.answer_policy import confidence_for_context, evidence_refs_for_context


class AiResponseContractError(ValueError):
    pass


def parse_structured_answer(raw_answer: str, context: dict[str, Any]) -> dict[str, Any]:
    payload = _extract_json(raw_answer)
    markdown = _dashboard_safe_markdown(_string_field(payload, "markdownAnswer"))
    if not markdown:
        raise AiResponseContractError("Gemini response did not include markdownAnswer.")

    requested_refs = payload.get("evidenceRefs", [])
    valid_refs, invalid_count = _validated_evidence_refs(requested_refs, context)
    if not valid_refs:
        valid_refs = evidence_refs_for_context(context)

    limitations = [
        _dashboard_safe_markdown(item)
        for item in _string_list(payload.get("limitations"))
    ]
    assumptions = [
        _dashboard_safe_markdown(item)
        for item in _string_list(payload.get("assumptions"))
    ]
    if assumptions:
        limitations.extend(f"Assumption: {item}" for item in assumptions)
    if invalid_count:
        limitations.append(
            f"{invalid_count} Gemini evidence reference(s) were omitted because they were not "
            "present in the retrieved dashboard context."
        )

    return {
        "answer": _plain_text(markdown),
        "answerMarkdown": markdown,
        "evidenceRefs": valid_refs,
        "limitations": list(dict.fromkeys(limitations)),
        "confidence": _confidence(payload.get("confidence"), context),
    }


def _extract_json(raw_answer: str) -> dict[str, Any]:
    text = raw_answer.strip()
    fenced = re.search(r"```(?:json)?\s*(\{.*?\})\s*```", text, flags=re.S | re.I)
    if fenced:
        text = fenced.group(1)
    elif not text.startswith("{"):
        match = re.search(r"(\{.*\})", text, flags=re.S)
        if match:
            text = match.group(1)
    try:
        parsed = json.loads(text)
    except json.JSONDecodeError as exc:
        raise AiResponseContractError("Gemini response was not valid JSON.") from exc
    if not isinstance(parsed, dict):
        raise AiResponseContractError("Gemini JSON response was not an object.")
    return parsed


def _validated_evidence_refs(
    value: Any,
    context: dict[str, Any],
) -> tuple[list[dict[str, Any]], int]:
    if not isinstance(value, list):
        return [], 0
    refs: list[dict[str, Any]] = []
    invalid_count = 0
    for item in value[:12]:
        if not isinstance(item, dict):
            invalid_count += 1
            continue
        section = _string_field(item, "section")
        label = _string_field(item, "label")
        source_path = _string_field(item, "sourcePath")
        if not section or not label:
            invalid_count += 1
            continue
        if source_path and not _source_path_exists(context, source_path):
            invalid_count += 1
            continue
        if not source_path and section not in context:
            invalid_count += 1
            continue
        refs.append(
            {
                "section": _dashboard_section_label(section),
                "label": _dashboard_safe_markdown(label),
                "value": item.get("value"),
                "sourcePath": source_path or None,
            }
        )
    return refs, invalid_count


def _source_path_exists(context: dict[str, Any], source_path: str) -> bool:
    current: Any = context
    for part in source_path.split("."):
        match = re.fullmatch(r"([A-Za-z0-9_]+)(?:\[(\d+)])?", part)
        if not match:
            return False
        key, index = match.groups()
        if not isinstance(current, dict) or key not in current:
            return False
        current = current[key]
        if index is not None:
            if not isinstance(current, list):
                return False
            position = int(index)
            if position >= len(current):
                return False
            current = current[position]
    return True


def _string_field(payload: dict[str, Any], key: str) -> str:
    value = payload.get(key)
    return value.strip() if isinstance(value, str) else ""


def _string_list(value: Any) -> list[str]:
    if not isinstance(value, list):
        return []
    return [str(item).strip() for item in value if str(item).strip()]


def _confidence(value: Any, context: dict[str, Any]) -> str:
    if value in {"high", "medium", "low"}:
        return str(value)
    return confidence_for_context(context)


def _plain_text(markdown: str) -> str:
    text = re.sub(r"`([^`]+)`", r"\1", markdown)
    text = re.sub(r"\*\*([^*]+)\*\*", r"\1", text)
    text = re.sub(r"\*([^*]+)\*", r"\1", text)
    text = re.sub(r"^\s{0,3}#{1,6}\s*", "", text, flags=re.M)
    text = re.sub(r"^\s*[-*]\s+", "- ", text, flags=re.M)
    return text.strip()


_INTERNAL_PATH_LABELS = {
    "execution.eventRows": "Execution event matrix table",
    "execution.weakOrUnmatchedEvents": "Execution KPI cards",
    "execution.matchedEvents": "Execution KPI cards",
    "execution.executedEvents": "Execution KPI cards",
    "execution.actionDueEvents": "Execution KPI cards",
    "execution.matchCoverage": "Execution KPI cards",
    "execution.hcpExecutionRate": "Planned vs engaged HCPs chart",
    "workflow.ownerStageCounts": "Workflow status cards",
    "workflow.pendingReportCount": "Workflow status cards",
    "workflow.requestRows": "Workflow request table",
    "workflow.requestApprovalCounts": "Request approval panel",
    "workflow.requestConfirmationCounts": "Request confirmation panel",
    "workflow.postApprovalCounts": "Post approval panel",
    "workflow.postConfirmationCounts": "Post confirmation panel",
    "interventions.topRows": "Intervention mix table",
    "budget.topGapRows": "Budget event gap table",
    "budget.spendWithoutPlanCount": "Budget summary cards",
    "budget.unspentGapUsd": "Budget summary cards",
    "budget.overrunAmountUsd": "Budget summary cards",
    "doctorRoi.topDoctorOpportunityRows": "Doctor ROI table",
    "doctorRoi.matchedDoctorDetails": "Doctor detail drawer",
    "dataQuality.validationWarningCount": "Data Quality validation panels",
    "dataQuality.matchCoverage": "Data Quality coverage cards",
    "dataQuality.pcodeCoverage": "Data Quality coverage cards",
    "dataQuality.rcpaCoverage": "Data Quality coverage cards",
    "dataQuality.unmatchedBySource": "Data Quality unmatched records panel",
}

_SECTION_LABELS = {
    "execution": "Execution",
    "workflow": "Workflow",
    "interventions": "Intervention Mix",
    "budget": "Budget",
    "doctorRoi": "Doctor ROI",
    "dataQuality": "Data Quality",
}


def _dashboard_safe_markdown(text: str) -> str:
    safe = text
    internal_paths = sorted(
        _INTERNAL_PATH_LABELS.items(),
        key=lambda item: len(item[0]),
        reverse=True,
    )
    for path, label in internal_paths:
        safe = re.sub(rf"\b{re.escape(path)}\b", label, safe)
    safe = re.sub(
        r"\b(?:execution|workflow|interventions|budget|doctorRoi|dataQuality)"
        r"(?:\.[A-Za-z_][A-Za-z0-9_]*(?:\[\d+])?)+\b",
        "the relevant dashboard section",
        safe,
    )
    safe = re.sub(r"\bsourcePath\b", "dashboard source", safe)
    safe = re.sub(r"\bJSON context\b", "dashboard context", safe, flags=re.I)
    return safe.strip()


def _dashboard_section_label(section: str) -> str:
    return _SECTION_LABELS.get(section, section)
