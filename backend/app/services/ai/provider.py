from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Protocol

import httpx

from backend.app.config import Settings

GEMINI_ENDPOINT = "https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent"
RETRYABLE_GEMINI_STATUSES = {429, 500, 502, 503, 504}


class AIProviderError(RuntimeError):
    def __init__(self, code: str, message: str) -> None:
        super().__init__(message)
        self.code = code
        self.message = message


@dataclass(frozen=True)
class ProviderResult:
    answer: str
    provider: str
    model: str


class AIProvider(Protocol):
    provider_name: str
    model_name: str

    def generate(self, *, question: str, context: Any, system_prompt: str) -> ProviderResult:
        ...


class NullProvider:
    provider_name = "null"
    model_name = "disabled"

    def generate(self, *, question: str, context: Any, system_prompt: str) -> ProviderResult:
        raise AIProviderError("provider_disabled", "AI provider is disabled.")


class TestProvider:
    provider_name = "test"
    model_name = "test-model"

    def __init__(self, answer: str = "Test provider answer.") -> None:
        self.answer = answer

    def generate(self, *, question: str, context: Any, system_prompt: str) -> ProviderResult:
        return ProviderResult(
            answer=self.answer,
            provider=self.provider_name,
            model=self.model_name,
        )


class DeterministicProvider:
    provider_name = "deterministic"
    model_name = "rules"

    def generate(self, *, question: str, context: Any, system_prompt: str) -> ProviderResult:
        return ProviderResult(
            answer=(
                "Deterministic safe mode is active. The assistant will answer from "
                "backend metrics without calling an external model."
            ),
            provider=self.provider_name,
            model=self.model_name,
        )


class GeminiProvider:
    provider_name = "gemini"

    def __init__(
        self,
        *,
        api_key: str,
        model: str,
        fallback_models: list[str] | None = None,
        timeout_seconds: float = 12.0,
    ) -> None:
        if not api_key:
            raise AIProviderError("missing_api_key", "AI_API_KEY is required for Gemini.")
        self.api_key = api_key
        self.model_name = model or "gemini-2.5-flash-lite"
        self.models = _dedupe_models([self.model_name, *(fallback_models or [])])
        self.timeout_seconds = timeout_seconds

    def generate(self, *, question: str, context: Any, system_prompt: str) -> ProviderResult:
        context_text = context if isinstance(context, str) else str(context)
        payload = _gemini_payload(
            question=question,
            context_text=context_text,
            system_prompt=system_prompt,
        )
        retryable_errors: list[str] = []
        try:
            with httpx.Client(timeout=self.timeout_seconds) as client:
                for model in self.models:
                    response = client.post(
                        GEMINI_ENDPOINT.format(model=model),
                        headers={
                            "x-goog-api-key": self.api_key,
                            "Content-Type": "application/json",
                        },
                        json=payload,
                    )
                    if response.status_code in RETRYABLE_GEMINI_STATUSES:
                        retryable_errors.append(f"{model}:{response.status_code}")
                        continue

                    _raise_for_gemini_response(response)
                    text = _extract_text(response.json())
                    if not text:
                        raise AIProviderError(
                            "invalid_provider_response",
                            f"Gemini model {model} response did not contain text.",
                        )
                    return ProviderResult(
                        answer=text.strip(),
                        provider=self.provider_name,
                        model=model,
                    )
        except httpx.TimeoutException as exc:
            raise AIProviderError("provider_timeout", "Gemini request timed out.") from exc
        except httpx.HTTPError as exc:
            raise AIProviderError("provider_http_error", str(exc)) from exc

        raise AIProviderError(
            "provider_capacity_or_rate_limit",
            "All configured Gemini models were unavailable or rate-limited: "
            + ", ".join(retryable_errors),
        )


def build_primary_provider(settings: Settings) -> AIProvider:
    provider = settings.ai_provider.lower().strip()
    if provider == "gemini":
        return GeminiProvider(
            api_key=settings.ai_api_key,
            model=settings.ai_model,
            fallback_models=_parse_model_list(settings.ai_model_fallbacks),
            timeout_seconds=settings.ai_timeout_seconds,
        )
    if provider == "test":
        return TestProvider()
    return NullProvider()


def _extract_text(data: dict) -> str:
    candidates = data.get("candidates")
    if not isinstance(candidates, list) or not candidates:
        return ""
    parts = candidates[0].get("content", {}).get("parts", [])
    if not isinstance(parts, list):
        return ""
    return "\n".join(str(part.get("text", "")) for part in parts if isinstance(part, dict)).strip()


def _parse_model_list(value: str) -> list[str]:
    return [model.strip() for model in value.split(",") if model.strip()]


def _dedupe_models(models: list[str]) -> list[str]:
    seen: set[str] = set()
    result: list[str] = []
    for model in models:
        normalized = model.strip()
        if normalized and normalized not in seen:
            result.append(normalized)
            seen.add(normalized)
    return result


def _gemini_payload(*, question: str, context_text: str, system_prompt: str) -> dict[str, Any]:
    return {
        "systemInstruction": {"parts": [{"text": system_prompt}]},
        "contents": [
            {
                "role": "user",
                "parts": [
                    {
                        "text": (
                            "Question:\n"
                            f"{question}\n\n"
                            "Compact structured dashboard context JSON:\n"
                            f"{context_text}"
                        )
                    }
                ],
            }
        ],
        "generationConfig": {
            "temperature": 0.2,
            "topP": 0.9,
            "maxOutputTokens": 700,
        },
    }


def _raise_for_gemini_response(response: httpx.Response) -> None:
    if response.status_code in {402, 403}:
        raise AIProviderError(
            "provider_quota_or_permission",
            f"Gemini returned {response.status_code}.",
        )
    if response.status_code >= 400:
        raise AIProviderError("provider_error", f"Gemini returned {response.status_code}.")
