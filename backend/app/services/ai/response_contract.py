from __future__ import annotations

import json
import re
from typing import Any

from backend.app.services.ai.answer_policy import confidence_for_context, evidence_refs_for_context


class AiResponseContractError(ValueError):
    pass


def parse_structured_answer(raw_answer: str, context: dict[str, Any]) -> dict[str, Any]:
    payload = _extract_json(raw_answer)
    markdown = _string_field(payload, "markdownAnswer")
    if not markdown:
        raise AiResponseContractError("Gemini response did not include markdownAnswer.")

    requested_refs = payload.get("evidenceRefs", [])
    valid_refs, invalid_count = _validated_evidence_refs(requested_refs, context)
    if not valid_refs:
        valid_refs = evidence_refs_for_context(context)

    limitations = _string_list(payload.get("limitations"))
    assumptions = _string_list(payload.get("assumptions"))
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
                "section": section,
                "label": label,
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
