import httpx

from backend.app.config import Settings
from backend.app.services.ai.provider import AIProviderError, GeminiProvider, build_primary_provider


class FakeClient:
    def __init__(self, *, timeout: float) -> None:
        self.timeout = timeout

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, traceback) -> None:
        return None

    def post(self, url: str, headers: dict, json: dict) -> httpx.Response:
        FakeClient.calls.append(url)
        if "gemini-2.5-flash-lite" in url:
            return httpx.Response(503, json={"error": {"message": "high demand"}})
        return httpx.Response(
            200,
            json={"candidates": [{"content": {"parts": [{"text": "Fallback model answer."}]}}]},
        )


FakeClient.calls: list[str] = []


def test_gemini_provider_fails_over_to_next_lightweight_model(monkeypatch) -> None:
    FakeClient.calls = []
    monkeypatch.setattr("backend.app.services.ai.provider.httpx.Client", FakeClient)
    provider = GeminiProvider(
        api_key="test-key",
        model="gemini-2.5-flash-lite",
        fallback_models=["gemini-flash-lite-latest", "gemini-2.0-flash-lite"],
    )

    result = provider.generate(question="Summarize risk", context={}, system_prompt="System")

    assert result.provider == "gemini"
    assert result.model == "gemini-flash-lite-latest"
    assert result.answer == "Fallback model answer."
    assert len(FakeClient.calls) == 2


def test_gemini_provider_does_not_fail_over_on_permission_errors(monkeypatch) -> None:
    class PermissionClient(FakeClient):
        def post(self, url: str, headers: dict, json: dict) -> httpx.Response:
            PermissionClient.calls.append(url)
            return httpx.Response(403, json={"error": {"message": "permission denied"}})

    PermissionClient.calls = []
    monkeypatch.setattr("backend.app.services.ai.provider.httpx.Client", PermissionClient)
    provider = GeminiProvider(
        api_key="test-key",
        model="gemini-2.5-flash-lite",
        fallback_models=["gemini-flash-lite-latest"],
    )

    try:
        provider.generate(question="Summarize risk", context={}, system_prompt="System")
    except AIProviderError as exc:
        assert exc.code == "provider_quota_or_permission"
    else:
        raise AssertionError("Expected permission error")

    assert len(PermissionClient.calls) == 1


def test_build_primary_provider_parses_fallback_models() -> None:
    provider = build_primary_provider(
        Settings(
            AI_PROVIDER="gemini",
            AI_API_KEY="test-key",
            AI_MODEL="gemini-2.5-flash-lite",
            AI_MODEL_FALLBACKS="gemini-flash-lite-latest, gemini-2.0-flash-lite",
        )
    )

    assert isinstance(provider, GeminiProvider)
    assert provider.models == [
        "gemini-2.5-flash-lite",
        "gemini-flash-lite-latest",
        "gemini-2.0-flash-lite",
    ]
