from __future__ import annotations

import json
from time import perf_counter
from typing import Any

from sqlalchemy.orm import Session

from backend.app.config import get_settings
from backend.app.repositories.ai_repository import AiRepository
from backend.app.schemas.ai import AiQueryRequest, AiQueryResponse
from backend.app.services.ai.answer_policy import (
    confidence_for_context,
    dashboard_pointers_for_topics,
    deterministic_answer,
    route_question,
    unsupported_response,
)
from backend.app.services.ai.context_builder import build_compact_context, context_scope
from backend.app.services.ai.provider import AIProviderError, build_primary_provider
from backend.app.services.ai.redaction import redact_payload, redact_text

SYSTEM_PROMPT = """
You are the Cipla EMEU Execution Intelligence assistant.
Answer only from the bounded structured dashboard context supplied by the backend.
Do not invent source files, rows, doctors, currencies, fields, formulas, or conclusions.
Use concise business language. Mention limitations when the context includes them.
If the context cannot support the question, say so directly.
Never ask for raw workbook rows or secrets.
"""


class AssistantService:
    def __init__(self, session: Session) -> None:
        self.session = session
        self.repository = AiRepository(session)
        self.settings = get_settings()

    def answer(self, request: AiQueryRequest) -> AiQueryResponse:
        started = perf_counter()
        if self.settings.ai_redaction_enabled:
            provider_question, question_changed = redact_text(request.question)
        else:
            provider_question = request.question
            question_changed = False

        decision = route_question(provider_question)
        context = build_compact_context(
            self.session,
            question=provider_question,
            page_context=request.page_context,
            filters=request.filters,
            max_chars=self.settings.ai_context_max_chars,
            row_limit=self.settings.ai_context_row_limit,
        )
        context_scope_payload = context_scope(context)
        if self.settings.ai_redaction_enabled:
            provider_context, context_changed = redact_payload(context)
        else:
            provider_context = context
            context_changed = False
        redaction_applied = question_changed or context_changed

        if not decision.supported:
            payload = unsupported_response(provider_question, context_scope_payload)
            self._log(
                request=request,
                question_redacted=provider_question,
                context_summary=context_scope_payload | {"topics": [], "unsupported": True},
                answer=payload["answer"],
                provider=payload["providerUsed"],
                model=payload["modelUsed"],
                latency_ms=_elapsed_ms(started),
                error_code="unsupported_question",
                error_message=None,
            )
            return AiQueryResponse(**payload)

        provider = build_primary_provider(self.settings)
        error_code = None
        error_message = None
        try:
            result = provider.generate(
                question=provider_question,
                context=json.dumps(provider_context, sort_keys=True, default=str),
                system_prompt=SYSTEM_PROMPT,
            )
            response_payload = {
                "answer": result.answer,
                "dashboardPointers": dashboard_pointers_for_topics(
                    decision.topics,
                    provider_context,
                ),
                "limitations": list(
                    dict.fromkeys(str(item) for item in context.get("limitations", []))
                ),
                "confidence": confidence_for_context(provider_context),
                "providerUsed": result.provider,
                "modelUsed": result.model,
                "fallbackUsed": False,
                "redactionApplied": redaction_applied,
                "contextScope": context_scope_payload,
            }
        except AIProviderError as exc:
            error_code = exc.code
            error_message = exc.message
            fallback = deterministic_answer(provider_question, provider_context, reason=exc.message)
            response_payload = fallback | {
                "redactionApplied": redaction_applied,
                "contextScope": context_scope_payload,
            }

        self._log(
            request=request,
            question_redacted=provider_question,
            context_summary={
                **context_scope_payload,
                "topics": decision.topics,
                "providerConfigured": self.settings.ai_provider,
                "fallbackUsed": response_payload["fallbackUsed"],
                "redactionApplied": redaction_applied,
                "limitations": response_payload["limitations"][:6],
            },
            answer=response_payload["answer"],
            provider=response_payload["providerUsed"],
            model=response_payload.get("modelUsed"),
            latency_ms=_elapsed_ms(started),
            error_code=error_code,
            error_message=error_message,
        )
        return AiQueryResponse(**response_payload)

    def _log(
        self,
        *,
        request: AiQueryRequest,
        question_redacted: str,
        context_summary: dict[str, Any],
        answer: str,
        provider: str,
        model: str | None,
        latency_ms: int,
        error_code: str | None,
        error_message: str | None,
    ) -> None:
        filters = request.filters or {}
        self.repository.log_query(
            country=_string_or_none(filters.get("country")),
            month=_string_or_none(filters.get("month")),
            question_redacted=question_redacted,
            context_summary=context_summary,
            answer=answer,
            provider=provider,
            model=model,
            latency_ms=latency_ms,
            error_code=error_code,
            error_message=error_message,
        )


def _elapsed_ms(started: float) -> int:
    return int((perf_counter() - started) * 1000)


def _string_or_none(value: Any) -> str | None:
    return str(value) if value not in (None, "") else None
