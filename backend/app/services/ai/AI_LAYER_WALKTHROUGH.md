# Full AI Service Walkthrough

This document explains the AI service end to end, from the frontend AI drawer to the FastAPI router, dashboard context retrieval, Gemini/fallback generation, response validation, audit logging, and final rendering back in the browser.

## One-Line Mental Model

The AI layer is a guarded translator: it gathers compact, already-computed dashboard evidence from backend services, asks Gemini to explain it when available, validates the answer, falls back to deterministic rules when needed, and logs only sanitized metadata.

It does not ingest files, calculate source-of-truth KPIs, expose provider secrets, or send raw workbook rows to the model.

## End-To-End Flow

```text
frontend/src/components/ai/AiAssistantPanel.tsx
  -> frontend/src/api/ai.ts
  -> frontend/src/api/client.ts
  -> POST /api/ai/query
  -> backend/app/routers/ai.py
  -> backend/app/services/ai/assistant_service.py
  -> query_planner.py
  -> answer_policy.py
  -> context_builder.py
  -> existing dashboard services
  -> backend repositories
  -> SQL materialized views/tables
  -> provider.py (Gemini/test/null)
  -> response_contract.py
  -> answer_policy.py fallback if needed
  -> redaction.py when enabled
  -> backend/app/repositories/ai_repository.py
  -> ai_query_logs
  -> AiQueryResponse JSON
  -> frontend/src/api/ai.ts normalization
  -> frontend/src/components/ai/AiAssistantPanel.tsx rendering
```

## Frontend AI Layer

The frontend does not talk to Supabase, Gemini, or any AI provider directly. Its job is to capture the user's current dashboard context, send a typed question request to the backend, normalize the response defensively, and render the answer with evidence, confidence, limitations, and verification pointers.

### `frontend/src/main.tsx`

This is the React app entrypoint.

It creates a TanStack Query client:

```ts
const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      staleTime: 60_000,
      retry: 1,
    },
  },
});
```

Then it wraps the app:

```tsx
<QueryClientProvider client={queryClient}>
  <App />
</QueryClientProvider>
```

Why this matters for AI:

```text
React app starts
  -> QueryClientProvider enables useMutation/useQuery everywhere
  -> AiAssistantPanel can use useMutation(queryAi)
```

Strict I/O:

```text
Receives:
  Browser DOM root element

Hands off:
  App rendered inside React Query infrastructure
```

### `frontend/src/App.tsx`

This is the frontend shell that owns the current page and the current AI context.

Core state:

```ts
const [page, setPage] = useState<PageKey>("execution");
const [aiContext, setAiContext] = useState<AiContext>({
  pageContext: "execution",
  filters: {},
});
```

`page` controls which dashboard view is shown:

```text
execution -> ExecutionMatrix
budget    -> BudgetUtilization
doctors   -> DoctorRoi
quality   -> DataQuality
```

`aiContext` controls what the AI assistant knows about the user's current location and filters.

The important wiring:

```tsx
{page === "execution" ? <ExecutionMatrix onAiContextChange={setAiContext} /> : null}
{page === "budget" ? <BudgetUtilization onAiContextChange={setAiContext} /> : null}
{page === "doctors" ? <DoctorRoi onAiContextChange={setAiContext} /> : null}
{page === "quality" ? <DataQuality onAiContextChange={setAiContext} /> : null}

<AiAssistantPanel context={aiContext} />
```

ELI5:

```text
App is the front desk.
It knows which room the user is in.
Each page tells App, "Here are my current filters."
App passes that to the AI drawer so questions are grounded in the active page.
```

Strict I/O:

```text
Receives:
  User page navigation
  Page-level AI context updates from dashboard pages

Hands off:
  { pageContext, filters } to AiAssistantPanel
```

### Page Context Publishers

The dashboard pages publish context upward through `onAiContextChange`. This is what lets a question like "Where is risk highest?" mean different things depending on whether the user is on Execution, Budget, Doctor ROI, or Data Quality.

#### `frontend/src/pages/ExecutionMatrix.tsx`

Publishes:

```ts
onAiContextChange?.({
  pageContext: "execution",
  filters: activeFilters,
});
```

`activeFilters` contains:

```text
country
month
includeOutOfScope
```

Backend impact:

```text
pageContext="execution"
  -> query_planner gives execution/workflow/intervention topics more weight
  -> context_builder fetches execution summary, event rows, workflow rows, and intervention mix
```

#### `frontend/src/pages/BudgetUtilization.tsx`

Publishes:

```ts
onAiContextChange?.({
  pageContext: "budget",
  filters: aiFilters,
});
```

`aiFilters` contains:

```text
country
month
```

Backend impact:

```text
pageContext="budget"
  -> query_planner includes budget sections
  -> context_builder fetches budget summary and top budget gap rows
```

#### `frontend/src/pages/DoctorRoi.tsx`

Publishes:

```ts
onAiContextChange?.({
  pageContext: "doctor_roi",
  filters: aiFilters,
});
```

`aiFilters` can contain:

```text
country
month
brand
speciality
doctorClass
roiSegment
includeOutOfScope
```

Backend impact:

```text
pageContext="doctor_roi"
  -> query_planner includes doctor ROI sections
  -> context_builder fetches doctor opportunity rows
  -> if the question includes a P-code or doctor-like name, it may fetch doctor detail too
```

#### `frontend/src/pages/DataQuality.tsx`

Publishes:

```ts
onAiContextChange?.({
  pageContext: "data_quality",
  filters: {},
});
```

Backend impact:

```text
pageContext="data_quality"
  -> query_planner includes data quality sections
  -> context_builder fetches quality summary, unmatched records, and FX quality rows
```

### `frontend/src/components/ai/AiAssistantPanel.tsx`

This is the visible AI drawer.

ELI5:

```text
This is the chat box.
It remembers the typed question, opens/closes the side drawer, sends the question to the backend, and shows the answer with proof.
```

Important local state:

```ts
const [open, setOpen] = useState(false);
const [question, setQuestion] = useState("");
const [answer, setAnswer] = useState<AiQueryResponse | null>(null);
```

The network mutation:

```ts
const mutation = useMutation({
  mutationFn: queryAi,
  onSuccess: (data) => setAnswer(data),
});
```

This means:

```text
queryAi succeeds
  -> normalized AiQueryResponse is stored in answer
  -> AiAnswerCard renders it
```

The submit path:

```ts
mutation.mutate({
  question: trimmed,
  pageContext: context.pageContext,
  filters: context.filters,
});
```

Strict input:

```text
context.pageContext
  Current dashboard area, such as execution, budget, doctor_roi, data_quality

context.filters
  Current page filters, such as country/month/brand/speciality

question
  User's natural-language business question
```

Strict output:

```text
AiQueryRequest
  -> queryAi()
  -> backend POST /api/ai/query
```

Built-in UX states:

```text
Idle:
  Shows suggested prompts and textarea

Pending:
  Shows spinner while mutation.isPending

Error:
  Shows "The AI endpoint could not return an answer. Check that the backend is running."

Success:
  Renders AiAnswerCard
```

Suggested prompts are hard-coded product affordances:

```text
Where is execution risk highest?
Summarize budget and BTU/BTC risk.
Which doctor ROI signals need attention?
What data-quality limitations should I mention?
```

These prompts are intentionally aligned with supported backend topics. They reduce the chance that users ask unsupported questions outside the dashboard's evidence boundary.

### `AiAnswerCard` Inside `AiAssistantPanel.tsx`

This component renders the backend's structured answer.

It uses:

```text
answerMarkdown ?? answer
```

Then renders markdown with:

```tsx
<ReactMarkdown remarkPlugins={[remarkGfm]}>{answerMarkdown}</ReactMarkdown>
```

It displays:

```text
Status pill:
  Gemini/provider success or Safe fallback

Confidence:
  high / medium / low

Redaction badge:
  shown when backend applied redaction

Evidence used:
  evidenceRefs from backend response

ExecAI evidence workflow:
  agentSteps from backend response

Where to verify this:
  dashboardPointers from backend response

Limitations:
  limitations from backend response
```

This matters architecturally because the frontend does not just show a blob of model text. It shows structured proof around the answer. That is what makes the assistant auditable.

Strict I/O:

```text
Receives:
  AiQueryResponse

Hands off:
  Rendered markdown answer
  Evidence cards
  Workflow steps
  Dashboard verification pointers
  Limitations
```

### `frontend/src/api/ai.ts`

This is the frontend AI API wrapper and response hardener.

The call:

```ts
export async function queryAi(payload: AiQueryRequest) {
  const response = await apiPost<
    Partial<AiQueryResponse> & Record<string, unknown>,
    AiQueryRequest
  >("/api/ai/query", payload);
  return normalizeAiResponse(response);
}
```

ELI5:

```text
Send the question to the backend.
Do not blindly trust the response shape.
Patch missing/invalid fields into safe defaults before the UI renders them.
```

Why it uses `Partial<AiQueryResponse> & Record<string, unknown>`:

```text
The frontend expects AiQueryResponse,
but network responses can be malformed, incomplete, old, or from a failing backend.
So this file treats the response as unknown-ish first, then normalizes it.
```

Important normalization rules:

```text
answer:
  string or ""

answerMarkdown:
  string or null

evidenceRefs:
  array only; invalid items removed; label/section get fallbacks

agentSteps:
  array only; status is completed or fallback

dashboardPointers:
  array only; page/section/detail/reason get fallbacks

limitations:
  array only; values stringified

confidence:
  high / medium / low, otherwise low

providerUsed:
  string or "unknown"

modelUsed:
  string or null

fallbackUsed:
  boolean or false

redactionApplied:
  boolean or false

contextScope:
  valid object or default dashboard scope
```

Strict I/O:

```text
Receives:
  AiQueryRequest from AiAssistantPanel

Sends:
  POST /api/ai/query through apiPost

Receives:
  Raw JSON response from backend

Hands off:
  Fully normalized AiQueryResponse to the drawer
```

### `frontend/src/api/client.ts`

This is the shared HTTP client.

Base URL:

```ts
const API_BASE_URL = import.meta.env.VITE_API_BASE_URL ?? "http://localhost:8000";
```

POST helper:

```ts
export async function apiPost<TResponse, TBody>(path: string, body: TBody): Promise<TResponse> {
  const response = await fetch(`${API_BASE_URL}${path}`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body),
  });
  if (!response.ok) {
    throw new Error(`API request failed: ${response.status}`);
  }
  return (await response.json()) as TResponse;
}
```

ELI5:

```text
This knows where the backend lives.
It sends JSON.
If the backend returns an error status, it throws so React Query can show the error state.
```

Strict I/O:

```text
Receives:
  API path and request body

Hands off:
  Parsed JSON response or thrown Error
```

### `frontend/src/types/api.ts`

This file defines the frontend TypeScript contract for the AI request/response.

Request:

```ts
export type AiQueryRequest = {
  question: string;
  pageContext?: string | null;
  filters?: Record<string, unknown>;
};
```

Response:

```ts
export type AiQueryResponse = {
  answer: string;
  answerMarkdown: string | null;
  evidenceRefs: AiEvidenceRef[];
  agentSteps: AiAgentStep[];
  dashboardPointers: AiDashboardPointer[];
  limitations: string[];
  confidence: "high" | "medium" | "low";
  providerUsed: string;
  modelUsed: string | null;
  fallbackUsed: boolean;
  redactionApplied: boolean;
  contextScope: AiContextScope;
};
```

This mirrors `backend/app/schemas/ai.py`, but in frontend camelCase.

Important mapping:

```text
Backend Python:
  provider_used
  model_used
  fallback_used
  redaction_applied
  context_scope

Frontend TypeScript:
  providerUsed
  modelUsed
  fallbackUsed
  redactionApplied
  contextScope
```

That mapping works because backend schemas inherit from `ApiModel`, which serializes snake_case to camelCase.

### Full Browser-To-Backend-To-Browser AI Flow

```text
1. User opens dashboard.

2. main.tsx mounts App inside QueryClientProvider.

3. App renders the selected dashboard page.

4. The active page computes AI context from its filters.
   Example: ExecutionMatrix publishes { pageContext: "execution", filters: { country, month } }.

5. App stores that context in aiContext.

6. App passes aiContext into AiAssistantPanel.

7. User types a question or clicks a suggested prompt.

8. AiAssistantPanel.submit() trims the question and calls mutation.mutate().

9. queryAi() sends:
   POST /api/ai/query
   {
     question,
     pageContext,
     filters
   }

10. apiPost() sends JSON to:
    http://localhost:8000/api/ai/query
    or VITE_API_BASE_URL + /api/ai/query

11. Backend router validates request with AiQueryRequest.

12. AssistantService plans, retrieves context, calls Gemini or fallback, validates, logs, and returns AiQueryResponse.

13. queryAi() normalizes the backend JSON.

14. AiAssistantPanel stores the response in answer.

15. AiAnswerCard renders:
    answer markdown
    evidence used
    agent workflow
    dashboard pointers
    limitations
    provider/fallback status
```

### Frontend Security Boundary

The frontend intentionally cannot:

```text
Read Supabase credentials
Read Gemini API keys
Run SQL
Choose arbitrary backend repositories
Bypass backend evidence validation
Directly mutate ai_query_logs
```

The browser only sends:

```text
question
pageContext
filters
```

The backend decides:

```text
what topics are supported
which data sections to retrieve
how much context to send to the model
which evidence references are valid
what to log
whether to fall back
```

## External Touchpoints

### `backend/app/routers/ai.py`

This is the HTTP doorway for AI.

```python
@router.post("/query", response_model=AiQueryResponse, response_model_by_alias=True)
def query_ai(request: AiQueryRequest, session: Annotated[Session, Depends(get_session)]) -> AiQueryResponse:
    return AssistantService(session).answer(request)
```

It defines:

```text
POST /api/ai/query
```

It receives the frontend payload:

```json
{
  "question": "Where is execution risk highest?",
  "pageContext": "execution",
  "filters": {
    "country": "NP",
    "month": "2026-05"
  }
}
```

The router stays thin. It only validates request shape, obtains a database session, and delegates to `AssistantService`.

### `backend/app/schemas/ai.py`

This defines the AI API contract.

Main request schema:

```python
class AiQueryRequest(ApiModel):
    question: str
    page_context: str | None
    filters: dict[str, Any]
```

Main response schema:

```python
class AiQueryResponse(ApiModel):
    answer: str
    answer_markdown: str | None
    evidence_refs: list[AiEvidenceRef]
    agent_steps: list[AiAgentStep]
    dashboard_pointers: list[DashboardPointer]
    limitations: list[str]
    confidence: Literal["high", "medium", "low"]
    provider_used: str
    model_used: str | None
    fallback_used: bool
    redaction_applied: bool
    context_scope: AiContextScope
```

Because these schemas inherit from `ApiModel`, Python snake_case fields are serialized to frontend camelCase. For example, `provider_used` becomes `providerUsed`.

### `backend/app/repositories/ai_repository.py`

This writes the AI audit log.

It stores rows in:

```text
ai_query_logs
```

It logs:

```text
question_redacted
context_summary_json
answer
provider
model
latency_ms
error_code
error_message
country_id
calendar_month_id
```

It does not store raw workbook rows. It receives only the safe summary created by `AssistantService`.

## AI Service Package Files

## `assistant_service.py`

This is the main orchestrator for AI answers.

### Purpose

It coordinates the full AI request lifecycle:

```text
receive request
redact question if enabled
classify supported topic
plan context retrieval
build compact dashboard context
redact context if enabled
call provider
validate response
fallback on failure
log sanitized metadata
return AiQueryResponse
```

### Important Inputs

From the router:

```python
request: AiQueryRequest
session: Session
```

From settings:

```text
AI_PROVIDER
AI_API_KEY
AI_MODEL
AI_MODEL_FALLBACKS
AI_CONTEXT_MAX_CHARS
AI_CONTEXT_ROW_LIMIT
AI_REDACTION_ENABLED
AI_TIMEOUT_SECONDS
```

### Core Method

```python
def answer(self, request: AiQueryRequest) -> AiQueryResponse:
```

### Step-By-Step

1. Starts a timer with `perf_counter()` so latency can be logged.

2. Optionally redacts the user question:

```python
provider_question, question_changed = redact_text(request.question)
```

3. Routes the question:

```python
decision = route_question(provider_question)
```

If unsupported, it returns a policy refusal without calling Gemini.

4. Builds a query plan:

```python
query_plan = plan_query(...)
```

The plan decides which dashboard sections to retrieve and how many rows to include.

5. Builds compact dashboard context:

```python
context = build_compact_context(...)
```

This is the core safety boundary. Context comes from existing backend services, not from raw workbooks.

6. Optionally redacts the context:

```python
provider_context, context_changed = redact_payload(context)
```

7. Chooses provider:

```python
provider = build_primary_provider(self.settings)
```

8. Calls Gemini/test/null provider:

```python
result = provider.generate(
    question=provider_question,
    context=json.dumps(provider_context, sort_keys=True, default=str),
    system_prompt=SYSTEM_PROMPT,
)
```

9. Validates provider output:

```python
structured = parse_structured_answer(result.answer, provider_context)
```

10. If provider call or response validation fails, fallback:

```python
fallback = deterministic_answer(provider_question, provider_context, reason=error_message)
```

11. Logs safe metadata:

```python
self.repository.log_query(...)
```

12. Returns:

```python
AiQueryResponse(**response_payload)
```

### What The System Prompt Enforces

`SYSTEM_PROMPT` tells Gemini to:

```text
answer only from supplied dashboard context
avoid invented facts
avoid raw workbook rows/secrets
return strict JSON
include evidence references
include assumptions/limitations/confidence
```

The prompt matters, but the response contract validation is the real enforcement layer.

## `query_planner.py`

This decides what dashboard evidence the question needs.

### Purpose

It turns a natural-language question into a `QueryPlan`.

```python
@dataclass(frozen=True)
class QueryPlan:
    topics: list[str]
    sections: set[str]
    detail_limit: int
    broad_limit: int
    doctor_search_terms: list[str]
    wants_specifics: bool
```

### Topic Detection

It uses keyword groups:

```python
TOPIC_KEYWORDS = {
    "execution": (...),
    "workflow": (...),
    "intervention": (...),
    "budget": (...),
    "doctor": (...),
    "quality": (...),
}
```

Examples:

```text
"execution risk" -> execution
"pending reports" -> workflow
"BTU/BTC spend" -> budget
"dark horse doctors" -> doctor
"missing FX" -> budget + quality depending on terms
```

### Page Context Support

If the user asks a vague question from a page, page context helps:

```text
pageContext = "doctor_roi" -> include doctor topic
pageContext = "budget" -> include budget topic
pageContext = "execution" and no topics -> include execution/workflow/intervention
```

### Row Limits

If the question asks for specifics, the plan allows more detail rows:

```text
"which"
"who"
"list"
"doctor"
"pcode"
"request"
"event"
"top"
```

Otherwise it keeps a smaller row set.

### Doctor Search Terms

It extracts possible doctor names or Pcodes from questions like:

```text
"Pcode 12345"
"Dr Sharma"
"doctor Mehta"
```

Those terms let `context_builder.py` fetch specific doctor detail evidence.

## `context_builder.py`

This builds the bounded data package sent to Gemini.

### Purpose

It gathers dashboard evidence from existing backend services and shapes it into compact JSON.

It does not read raw workbook rows.

### Services It Calls

Depending on the query plan, it calls:

```text
ExecutionService
WorkflowService
InterventionService
BudgetService
DoctorService
DataQualityService
```

Those services call repositories, and repositories query materialized views/tables such as:

```text
mv_execution_kpis
mv_execution_event_matrix
mv_workflow_governance
mv_intervention_mix
mv_budget_utilization
mv_doctor_roi
mv_data_quality
request_doctors
execution_requests
rcpa_doctor_month_summary
rcpa_doctor_brand_summary
```

### Context Policy

The context includes an explicit policy:

```python
"contextPolicy": {
    "rawWorkbookRowsIncluded": False,
    "fullTablesIncluded": False,
    "rowLimit": ...,
    "broadRowLimit": ...,
    "topN": ...,
    "maxCharacters": ...,
}
```

This is both documentation and a guardrail.

### Main Function

```python
build_compact_context(...)
```

Inputs:

```text
session
question
page_context
filters
max_chars
row_limit
query_plan
```

Output:

```text
dict[str, Any]
```

### Section Examples

Execution context may include:

```text
plannedEvents
matchedEvents
weakOrUnmatchedEvents
executedEvents
actionDueEvents
matchCoverage
eventExecutionRate
hcpExecutionRate
eventRows
```

Workflow context may include:

```text
pendingRequestCount
pendingReportCount
reportsSentForCorrection
requestApprovalCounts
ownerStageCounts
requestRows
```

Budget context may include:

```text
plannedBudgetUsd
confirmedContractedAmountUsd
actualTotalSpendUsd
unspentGapUsd
overrunAmountUsd
missingFxCount
provisionalFxCount
topGapRows
```

Doctor ROI context may include:

```text
darkHorseCount
noRcpaCount
quadrantCounts
segmentCounts
topDoctorOpportunityRows
matchedDoctorDetails
```

Data quality context may include:

```text
loadedFileCount
rowsLoaded
validationWarningCount
matchCoverage
pcodeCoverage
rcpaCoverage
missingFxCount
unmatchedBySource
fxQuality
```

### Size Control

If the context is too large, `_fit_context()` progressively trims it:

```text
first: reduce detail rows
then: keep only summaries
finally: mark context as truncated
```

This protects provider cost, latency, and privacy.

## `provider.py`

This abstracts model providers.

### Purpose

It keeps Gemini-specific HTTP code away from business orchestration.

### Main Types

```python
class AIProvider(Protocol)
class ProviderResult
class AIProviderError
```

All providers expose:

```python
generate(question, context, system_prompt) -> ProviderResult
```

### Providers

#### `GeminiProvider`

Calls:

```text
https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent
```

It sends:

```text
system instruction
question
compact dashboard context JSON
generation config
```

It supports fallback models from `AI_MODEL_FALLBACKS`.

It treats these as retryable model statuses:

```python
{429, 500, 502, 503, 504}
```

If all models fail, it raises `AIProviderError`, and `AssistantService` falls back.

#### `NullProvider`

Used when AI is disabled or not configured.

It raises:

```text
provider_disabled
```

That intentionally triggers deterministic fallback.

#### `TestProvider`

Used by tests to return predictable output.

#### `DeterministicProvider`

Represents rule-based safe mode. In practice, the richer deterministic answer is built in `answer_policy.py`.

### Provider Selection

```python
build_primary_provider(settings)
```

Uses:

```text
AI_PROVIDER=gemini -> GeminiProvider
AI_PROVIDER=test -> TestProvider
anything else -> NullProvider
```

## `response_contract.py`

This validates Gemini output.

### Purpose

Gemini is allowed to synthesize language, but it must return a structured answer grounded in supplied context.

### Required Provider Output Shape

Gemini is instructed to return JSON:

```json
{
  "markdownAnswer": "...",
  "evidenceRefs": [
    {
      "section": "budget",
      "label": "Example row",
      "value": "optional",
      "sourcePath": "budget.topGapRows[0]"
    }
  ],
  "assumptions": [],
  "limitations": [],
  "confidence": "high"
}
```

### What It Checks

`parse_structured_answer()` checks:

```text
response is parseable JSON
JSON is an object
markdownAnswer exists
evidence refs are well-formed
evidenceRefs.sourcePath exists in the supplied context
confidence is high/medium/low
internal context paths are converted to dashboard-friendly labels
```

If Gemini cites fake evidence paths, those refs are removed.

If no valid refs remain, fallback refs are generated from available context.

If the response is badly malformed, it raises `AiResponseContractError`, and `AssistantService` uses deterministic fallback.

## `answer_policy.py`

This contains policy rules, fallback answers, evidence refs, and dashboard pointers.

### Purpose

It defines what the assistant is allowed to answer and how to respond when Gemini is unavailable or inappropriate.

### Supported Topic Routing

```python
route_question(question) -> TopicDecision
```

It uses the same topic keyword map from `query_planner.py`.

If no topic is detected, the assistant refuses:

```text
I can only answer questions grounded in this app's execution, workflow,
intervention, budget, doctor ROI, RCPA, and data-quality metrics.
```

### Confidence

```python
confidence_for_context(context)
```

Downgrades confidence when:

```text
limitations mention missing/unavailable data
dataQualityFlags include weak/missing/stale signals
```

### Deterministic Fallback

```python
deterministic_answer(question, context, reason=None)
```

This creates a safe answer from structured metrics without calling Gemini.

It summarizes risk signals such as:

```text
weak/unmatched execution records
pending reports
spend-without-plan rows
dark-horse doctor opportunities
validation warnings
```

### Dashboard Pointers

The policy maps topics to frontend verification locations:

```text
execution -> Execution KPI cards, event matrix
workflow -> Workflow status cards, request table
intervention -> Intervention mix chart/table
budget -> Budget summary cards, event gap table
doctor -> Doctor ROI table/detail drawer
quality -> Data Quality validation/coverage panels
```

These pointers are returned so the frontend can tell the user where to verify the answer.

## `redaction.py`

This masks sensitive strings before provider calls or logging when redaction is enabled.

### Purpose

Protects obvious sensitive identifiers and raw source snippets.

### What It Redacts

```text
Pcode-like numbers
large money amounts with currency markers
doctor-like names after Dr/Doctor/HCP/Pcode for
raw source/workbook row excerpts
```

Example:

```text
Dr Sharma had LKR 500000 spend for Pcode 12345
```

can become:

```text
Dr [NAME] had [AMOUNT] spend for Pcode [PCODE]
```

### Functions

```python
redact_text(value: str) -> tuple[str, bool]
redact_payload(value: Any) -> tuple[Any, bool]
```

`redact_payload()` recursively walks dicts/lists/tuples and redacts all strings.

## `__init__.py`

This marks `backend/app/services/ai/` as a Python package.

It currently contains only:

```python
"""ExecAI assistant services."""
```

It has no runtime behavior.

## How The Files Fit Together

### Normal Gemini Path

```text
AiAssistantPanel.tsx
  sends question/pageContext/filters
        |
        v
backend/app/routers/ai.py
  validates request and injects DB session
        |
        v
assistant_service.py
  starts request, redacts if enabled
        |
        v
answer_policy.py
  route_question() checks if supported
        |
        v
query_planner.py
  plan_query() chooses topics, sections, row limits
        |
        v
context_builder.py
  calls dashboard services and builds compact context
        |
        v
provider.py
  GeminiProvider sends question + context + system prompt
        |
        v
response_contract.py
  validates JSON answer and evidence references
        |
        v
assistant_service.py
  adds dashboard pointers, limitations, confidence, provider metadata
        |
        v
ai_repository.py
  logs sanitized context summary to ai_query_logs
        |
        v
AiQueryResponse
  returns to frontend AI drawer
```

### Unsupported Question Path

```text
assistant_service.py
  -> answer_policy.route_question()
  -> unsupported_response()
  -> ai_repository.log_query(error_code="unsupported_question")
  -> AiQueryResponse with fallbackUsed=true and confidence=low
```

Gemini is not called.

### Provider Failure Path

```text
assistant_service.py
  -> provider.generate()
  -> AIProviderError or AiResponseContractError
  -> answer_policy.deterministic_answer()
  -> ai_repository.log_query(error_code=...)
  -> AiQueryResponse with fallbackUsed=true
```

The frontend still receives a useful answer.

## What SQL Data The AI Ultimately Uses

The AI context builder calls dashboard services, and those services use repositories that query materialized views and canonical summary tables.

Typical backing sources:

```text
mv_execution_kpis
mv_execution_event_matrix
mv_workflow_governance
mv_intervention_mix
mv_budget_utilization
mv_doctor_roi
mv_data_quality
mv_unmatched_events
request_doctors
execution_requests
rcpa_doctor_month_summary
rcpa_doctor_brand_summary
```

So AI is grounded in the same data the dashboard displays.

## What The AI Layer Intentionally Does Not Do

```text
Does not read raw Excel files
Does not receive raw workbook rows
Does not calculate KPI source-of-truth metrics
Does not expose Gemini API key to frontend
Does not let frontend query Supabase directly
Does not trust Gemini evidence references without validation
Does not fail the UX when Gemini is unavailable
```

## Simple Final Summary

```text
main.tsx
  mounts React and provides React Query

App.tsx
  owns current dashboard page and AI context

dashboard pages
  publish pageContext and filters

AiAssistantPanel.tsx
  captures the question, sends mutation, renders answer/evidence/pointers

frontend/api/ai.ts
  posts request and normalizes backend JSON into AiQueryResponse

frontend/api/client.ts
  sends JSON to the configured backend URL

ai.py router
  HTTP entrypoint

assistant_service.py
  main coordinator

query_planner.py
  chooses topics and sections

context_builder.py
  retrieves compact dashboard evidence

provider.py
  calls Gemini/test/null providers

response_contract.py
  validates Gemini JSON and evidence paths

answer_policy.py
  supported-topic policy, fallback answers, dashboard pointers

redaction.py
  masks sensitive text when enabled

ai_repository.py
  logs sanitized query metadata
```

The full AI service is production-minded because the browser only sends question/context, the backend retrieves trusted dashboard evidence, model output is treated as untrusted synthesis, and the frontend renders the answer with evidence, workflow state, confidence, limitations, and verification pointers.
