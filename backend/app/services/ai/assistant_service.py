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
from backend.app.services.ai.query_planner import plan_query
from backend.app.services.ai.redaction import redact_payload, redact_text
from backend.app.services.ai.response_contract import (
    AiResponseContractError,
    parse_structured_answer,
)

SYSTEM_PROMPT = """
You are the Cipla EMEU Execution Intelligence assistant.
Answer only from the bounded structured dashboard context supplied by the backend.
Do not invent source files, rows, doctors, currencies, fields, formulas, or conclusions.
Use specific names, Pcodes, request IDs, event names, currencies, and amounts when present.
Use concise business language. Mention only limitations that directly affect the answer.
If the context cannot support the question, say so directly.
Never ask for raw workbook rows or secrets.
Never mention JSON keys, camelCase fields, sourcePath values, or internal context paths such as
workflow.ownerStageCounts, execution.eventRows, or execution.weakOrUnmatchedEvents.
When explaining where to verify something, use dashboard-facing names such as Execution KPI
cards, Workflow status cards, Execution event matrix table, Budget summary cards, Doctor ROI
table, Doctor detail drawer, Data Quality validation panels, or Intervention mix table.
Return only valid JSON with this exact shape:
{
  "markdownAnswer": "Markdown answer with bullets or bold where useful.",
  "evidenceRefs": [
    {
      "section": "doctorRoi",
      "label": "Dr Example / 12345",
      "value": "optional",
      "sourcePath": "doctorRoi.topDoctorOpportunityRows[0]"
    }
  ],
  "assumptions": [],
  "limitations": [],
  "confidence": "high|medium|low"
}
Each evidenceRefs.sourcePath must exist in the supplied context JSON.
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

        decision = route_question(provider_question, request.page_context)
        query_plan = plan_query(
            provider_question,
            page_context=request.page_context,
            default_row_limit=self.settings.ai_context_row_limit,
        )
        context = build_compact_context(
            self.session,
            question=provider_question,
            page_context=request.page_context,
            filters=request.filters,
            max_chars=self.settings.ai_context_max_chars,
            row_limit=self.settings.ai_context_row_limit,
            query_plan=query_plan,
        )
        context_scope_payload = context_scope(context)
        if self.settings.ai_redaction_enabled:
            provider_context, context_changed = redact_payload(context)
        else:
            provider_context = context
            context_changed = False
        redaction_applied = question_changed or context_changed

        if not decision.supported:
            payload = unsupported_response(
                provider_question,
                context_scope_payload,
                request.page_context,
            )
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
            structured = parse_structured_answer(result.answer, provider_context)
            response_payload = {
                "answer": structured["answer"],
                "answerMarkdown": structured["answerMarkdown"],
                "evidenceRefs": structured["evidenceRefs"],
                "agentSteps": _agent_steps(
                    model_step="completed",
                    provider=f"{result.provider}/{result.model}",
                    topics=decision.topics,
                ),
                "dashboardPointers": dashboard_pointers_for_topics(
                    decision.topics,
                    provider_context,
                ),
                "limitations": list(
                    dict.fromkeys(
                        [
                            *(str(item) for item in structured["limitations"]),
                            *(str(item) for item in context.get("limitations", [])),
                        ]
                    )
                ),
                "confidence": structured.get("confidence")
                or confidence_for_context(provider_context),
                "providerUsed": result.provider,
                "modelUsed": result.model,
                "fallbackUsed": False,
                "redactionApplied": redaction_applied,
                "contextScope": context_scope_payload,
            }
        except (AIProviderError, AiResponseContractError) as exc:
            error_code = (
                exc.code if isinstance(exc, AIProviderError) else "invalid_ai_response_contract"
            )
            error_message = exc.message if isinstance(exc, AIProviderError) else str(exc)
            fallback = deterministic_answer(
                provider_question,
                provider_context,
                reason=error_message,
            )
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


def _agent_steps(*, model_step: str, provider: str, topics: list[str]) -> list[dict[str, str]]:
    return [
        {
            "step": (
                f"Planned query topics: "
                f"{', '.join(topics) if topics else 'general dashboard'}."
            ),
            "status": "completed",
        },
        {
            "step": "Retrieved bounded structured dashboard evidence before using the model.",
            "status": "completed",
        },
        {
            "step": f"Asked {provider} to synthesize a JSON answer from retrieved evidence.",
            "status": model_step,
        },
        {
            "step": "Validated evidence references before returning the answer.",
            "status": "completed" if model_step == "completed" else "fallback",
        },
    ]
