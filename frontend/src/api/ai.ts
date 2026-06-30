import { apiPost } from "./client";
import type { AiQueryRequest, AiQueryResponse } from "../types/api";

export function queryAi(payload: AiQueryRequest) {
  return apiPost<AiQueryResponse, AiQueryRequest>("/api/ai/query", payload);
}
