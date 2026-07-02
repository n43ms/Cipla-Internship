import json
from collections.abc import Iterator

import pytest
from fastapi.testclient import TestClient

from backend.app.database import get_session
from backend.app.main import create_app
from backend.app.services.ai.provider import AIProviderError, ProviderResult


class FakeSession:
    def execute(self, *args, **kwargs):
        raise AssertionError("database lookup should not be needed when AI log is patched")

    def commit(self):
        pass


def fake_session() -> Iterator[FakeSession]:
    yield FakeSession()


class SuccessProvider:
    provider_name = "gemini"
    model_name = "gemini-test"

    def generate(self, *, question: str, context: str, system_prompt: str) -> ProviderResult:
        assert "raw workbook" not in context.lower()
        assert "123456" in question
        assert "markdownAnswer" in system_prompt
        return ProviderResult(
            answer=json.dumps(
                {
                    "markdownAnswer": (
                        "**Execution risk** is concentrated in weak matches and pending reports."
                    ),
                    "evidenceRefs": [
                        {
                            "section": "execution",
                            "label": "Weak matches",
                            "value": 4,
                            "sourcePath": "execution.weakOrUnmatchedEvents",
                        }
                    ],
                    "assumptions": [],
                    "limitations": [],
                    "confidence": "medium",
                }
            ),
            provider="gemini",
            model="gemini-test",
        )


class FailingProvider:
    def __init__(
        self,
        code: str = "provider_quota_or_rate_limit",
        message: str = "free credits exhausted",
    ) -> None:
        self.code = code
        self.message = message

    def generate(self, *, question: str, context: str, system_prompt: str) -> ProviderResult:
        raise AIProviderError(self.code, self.message)


def test_ai_query_gemini_success_logs_detailed_question_when_redaction_disabled(
    monkeypatch,
) -> None:
    _patch_context(monkeypatch)
    logs = _patch_logging(monkeypatch)
    monkeypatch.setattr(
        "backend.app.services.ai.assistant_service.build_primary_provider",
        lambda settings: SuccessProvider(),
    )

    with _client() as client:
        response = client.post(
            "/api/ai/query",
            json={
                "question": "What is execution risk for Pcode 123456?",
                "pageContext": "execution",
                "filters": {"country": "LK", "month": "2026-05"},
            },
        )

    assert response.status_code == 200
    body = response.json()
    assert body["providerUsed"] == "gemini"
    assert body["fallbackUsed"] is False
    assert body["answerMarkdown"].startswith("**Execution risk**")
    assert body["evidenceRefs"][0]["sourcePath"] == "execution.weakOrUnmatchedEvents"
    assert body["agentSteps"]
    assert body["redactionApplied"] is False
    assert body["dashboardPointers"]
    assert "supportingMetrics" not in body
    assert any(pointer["page"] == "Execution" for pointer in body["dashboardPointers"])
    assert body["contextScope"]["filters"] == {"country": "LK", "month": "2026-05"}
    assert logs[0]["question_redacted"] == "What is execution risk for Pcode 123456?"


def test_ai_query_falls_back_on_malformed_gemini_json(monkeypatch) -> None:
    _patch_context(monkeypatch)
    _patch_logging(monkeypatch)

    class MalformedProvider:
        def generate(self, *, question: str, context: str, system_prompt: str) -> ProviderResult:
            return ProviderResult(
                answer="This is not JSON, so it cannot be contract-validated.",
                provider="gemini",
                model="gemini-test",
            )

    monkeypatch.setattr(
        "backend.app.services.ai.assistant_service.build_primary_provider",
        lambda settings: MalformedProvider(),
    )

    with _client() as client:
        response = client.post(
            "/api/ai/query",
            json={"question": "Which doctor ROI signals need attention?"},
        )

    assert response.status_code == 200
    body = response.json()
    assert body["providerUsed"] == "deterministic"
    assert body["fallbackUsed"] is True
    assert "not valid JSON" in body["limitations"][0]
    assert body["evidenceRefs"]


@pytest.mark.parametrize(
    ("code", "message"),
    [
        ("provider_quota_or_rate_limit", "free credits exhausted"),
        ("provider_timeout", "Gemini request timed out"),
        ("invalid_provider_response", "Gemini response did not contain text"),
    ],
)
def test_ai_query_falls_back_when_gemini_provider_fails(
    monkeypatch,
    code: str,
    message: str,
) -> None:
    _patch_context(monkeypatch)
    _patch_logging(monkeypatch)
    monkeypatch.setattr(
        "backend.app.services.ai.assistant_service.build_primary_provider",
        lambda settings: FailingProvider(code, message),
    )

    with _client() as client:
        response = client.post(
            "/api/ai/query",
            json={"question": "Summarize budget and workflow risk"},
        )

    assert response.status_code == 200
    body = response.json()
    assert body["providerUsed"] == "deterministic"
    assert body["fallbackUsed"] is True
    assert "Gemini was not used" in body["limitations"][0]
    assert body["confidence"] in {"medium", "high", "low"}
    assert any(pointer["page"] == "Budget" for pointer in body["dashboardPointers"])
    assert any(
        pointer["section"] == "Workflow status cards" for pointer in body["dashboardPointers"]
    )


def test_ai_query_refuses_unsupported_question(monkeypatch) -> None:
    _patch_context(monkeypatch)
    _patch_logging(monkeypatch)

    with _client() as client:
        response = client.post("/api/ai/query", json={"question": "Who won the football game?"})

    assert response.status_code == 200
    body = response.json()
    assert body["providerUsed"] == "deterministic"
    assert body["fallbackUsed"] is True
    assert body["confidence"] == "low"
    assert "only answer" in body["answer"]
    assert body["dashboardPointers"] == []


def _client() -> TestClient:
    app = create_app()
    app.dependency_overrides[get_session] = fake_session
    return TestClient(app)


def _patch_context(monkeypatch) -> None:
    def fake_context(
        session,
        question,
        page_context=None,
        filters=None,
        max_chars=9000,
        row_limit=40,
        query_plan=None,
    ):
        return {
            "questionTopicHint": page_context or "dashboard",
            "filters": filters or {},
            "execution": {"weakOrUnmatchedEvents": 4, "matchedEvents": 10},
            "workflow": {"pendingReportCount": 2},
            "budget": {"spendWithoutPlanCount": 1},
            "doctorRoi": {"darkHorseCount": 3},
            "dataQuality": {"validationWarningCount": 1},
            "limitations": ["RCPA is a historical baseline."],
            "dataQualityFlags": ["weak_match_coverage"],
            "contextPolicy": {"topN": 5, "maxCharacters": max_chars},
        }

    monkeypatch.setattr(
        "backend.app.services.ai.assistant_service.build_compact_context",
        fake_context,
    )


def _patch_logging(monkeypatch) -> list[dict]:
    logs: list[dict] = []

    def fake_log(self, **kwargs):
        logs.append(kwargs)

    monkeypatch.setattr("backend.app.repositories.ai_repository.AiRepository.log_query", fake_log)
    return logs
