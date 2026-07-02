import { apiPost } from "./client";
import type { AiContextScope, AiDashboardPointer, AiQueryRequest, AiQueryResponse } from "../types/api";

export async function queryAi(payload: AiQueryRequest) {
  const response = await apiPost<Partial<AiQueryResponse> & Record<string, unknown>, AiQueryRequest>(
    "/api/ai/query",
    payload,
  );
  return normalizeAiResponse(response);
}

function normalizeAiResponse(response: Partial<AiQueryResponse> & Record<string, unknown>): AiQueryResponse {
  return {
    answer: typeof response.answer === "string" ? response.answer : "",
    answerMarkdown: typeof response.answerMarkdown === "string" ? response.answerMarkdown : null,
    evidenceRefs: normalizeEvidenceRefs(response.evidenceRefs),
    agentSteps: normalizeAgentSteps(response.agentSteps),
    dashboardPointers: normalizeDashboardPointers(response.dashboardPointers),
    limitations: Array.isArray(response.limitations) ? response.limitations.map(String) : [],
    confidence: isConfidence(response.confidence) ? response.confidence : "low",
    providerUsed: typeof response.providerUsed === "string" ? response.providerUsed : "unknown",
    modelUsed: typeof response.modelUsed === "string" ? response.modelUsed : null,
    fallbackUsed: typeof response.fallbackUsed === "boolean" ? response.fallbackUsed : false,
    redactionApplied: typeof response.redactionApplied === "boolean" ? response.redactionApplied : false,
    contextScope: normalizeContextScope(response.contextScope),
  };
}

function normalizeEvidenceRefs(value: unknown): AiQueryResponse["evidenceRefs"] {
  if (!Array.isArray(value)) return [];
  return value
    .filter((item): item is Record<string, unknown> => Boolean(item) && typeof item === "object")
    .map((item) => ({
      section: stringOrFallback(item.section, "dashboard"),
      label: stringOrFallback(item.label, "Evidence"),
      value:
        typeof item.value === "string" ||
        typeof item.value === "number" ||
        typeof item.value === "boolean"
          ? item.value
          : null,
      sourcePath: typeof item.sourcePath === "string" ? item.sourcePath : null,
    }));
}

function normalizeAgentSteps(value: unknown): AiQueryResponse["agentSteps"] {
  if (!Array.isArray(value)) return [];
  return value
    .filter((item): item is Record<string, unknown> => Boolean(item) && typeof item === "object")
    .map((item) => ({
      step: stringOrFallback(item.step, "Processed dashboard evidence."),
      status: item.status === "fallback" ? "fallback" : "completed",
    }));
}

function normalizeDashboardPointers(value: unknown): AiDashboardPointer[] {
  if (!Array.isArray(value)) return [];
  return value
    .filter((item): item is Record<string, unknown> => Boolean(item) && typeof item === "object")
    .map((item) => ({
      page: stringOrFallback(item.page, "Dashboard"),
      section: stringOrFallback(item.section, "Relevant section"),
      detail: stringOrFallback(item.detail, "Verify this answer in the matching dashboard section."),
      reason: stringOrFallback(item.reason, "The backend did not include detailed pointer metadata."),
    }));
}

function normalizeContextScope(value: unknown): AiContextScope {
  if (!value || typeof value !== "object") {
    return { pageContext: "dashboard", filters: {}, topN: 0, maxCharacters: 0, sections: [] };
  }
  const scope = value as Record<string, unknown>;
  return {
    pageContext: stringOrFallback(scope.pageContext, "dashboard"),
    filters: scope.filters && typeof scope.filters === "object" ? (scope.filters as Record<string, unknown>) : {},
    topN: typeof scope.topN === "number" ? scope.topN : 0,
    maxCharacters: typeof scope.maxCharacters === "number" ? scope.maxCharacters : 0,
    sections: Array.isArray(scope.sections) ? scope.sections.map(String) : [],
  };
}

function isConfidence(value: unknown): value is AiQueryResponse["confidence"] {
  return value === "high" || value === "medium" || value === "low";
}

function stringOrFallback(value: unknown, fallback: string) {
  return typeof value === "string" && value.trim() ? value : fallback;
}
