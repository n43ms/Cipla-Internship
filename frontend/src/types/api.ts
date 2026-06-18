export type FxRateStatus = "official" | "provisional" | "missing";

export type ResponseMeta = {
  generatedAt: string;
  latestIngestionRunId?: string | null;
  latestIngestionStatus: string;
  filtersApplied: Record<string, unknown>;
  dataQualityFlags: string[];
  limitations: string[];
  sourceDerivationNotes?: string[];
};

export type HealthResponse = {
  status: "ok";
};

export type IngestionSummary = {
  id: string;
  status: string;
  rowsSeen: number;
  rowsLoaded: number;
  rowsSkipped: number;
  warningCount: number;
  errorCount: number;
};

export type BudgetSummaryResponse = {
  meta: ResponseMeta;
  plannedBudget: number;
  estimatedIntervention?: number | null;
  confirmedContractedAmount?: number | null;
  confirmedVsEstimatedVariance?: number | null;
  directHcpBtuSpend?: number | null;
  overheadBtcSpend?: number | null;
  actualTotalSpend: number;
  unspentGap?: number;
  overrunAmount?: number;
  currencyCode: string;
  missingFx: boolean;
  fxRateDate?: string | null;
  fxRateSource?: string | null;
  fxRateStatus: FxRateStatus;
};

export type ExecutionSummaryResponse = {
  meta: ResponseMeta;
  plannedEvents: number;
  matchedEvents: number;
  weakOrUnmatchedEvents: number;
  executedEvents: number;
  actionDueEvents: number;
  plannedEventsWithExecutedEvidence: number;
  plannedEventsWithActionDueEvidence: number;
  executedSnapshotCount: number;
  actionDueSnapshotCount: number;
  plannedHcps: number;
  engagedHcps: number;
  matchedEngagedHcps: number;
  rawEngagedHcps: number;
  hcpExecutionRate: number;
  eventExecutionRate: number;
  matchCoverage: number;
  snapshotSourceCounts: Record<string, number>;
  primaryScope: boolean;
  scopeStatuses: string[];
  scopeReasons: string[];
};

export type ExecutionFilterOption = {
  value: string;
  label: string;
};

export type ExecutionFilterOptionsResponse = {
  countries: ExecutionFilterOption[];
  months: ExecutionFilterOption[];
  recommendedMonth?: ExecutionFilterOption | null;
};

export type ExecutionEventRow = {
  sourceType: string;
  eventName: string | null;
  eventType: string | null;
  country: string;
  month: string;
  matchStatus: string;
  confidence: number;
  candidateMatch: string | null;
  plannedHcps?: number | null;
  engagedHcps?: number | null;
  executionStatus?: string | null;
  snapshotSource?: string | null;
  sourceDerivationNote?: string | null;
  unmatchedReasonCode?: string | null;
  unmatchedReasonDetail?: string | null;
  isPrimaryPhase4Scope?: boolean;
  scopeStatus?: string | null;
  scopeReason?: string | null;
  matchGrain?: string | null;
  sourceReferences: Record<string, unknown>;
};

export type EventListResponse = {
  meta: ResponseMeta;
  page: number;
  pageSize: number;
  total: number;
  rows: ExecutionEventRow[];
};

export type WorkflowSummaryResponse = {
  meta: ResponseMeta;
  requestApprovalCounts: Record<string, number>;
  requestConfirmationCounts: Record<string, number>;
  postApprovalCounts: Record<string, number>;
  postConfirmationCounts: Record<string, number>;
  ownerStageCounts: Record<string, number>;
  pendingRequestCount: number;
  pendingReportCount: number;
  reportsSentForCorrection: number;
  reportsApproved: number;
  expenseSubmittedCoverage: number;
  expenseConfirmedCoverage: number;
  primaryScope: boolean;
  scopeStatuses: string[];
  scopeReasons: string[];
};

export type WorkflowRequestRow = {
  reqId: string | null;
  country: string;
  month: string;
  repName: string | null;
  interventionType: string | null;
  requestApprovalStatus: string;
  requestConfirmationStatus: string;
  postApprovalStatus: string;
  postConfirmationStatus: string;
  currentOwnerStage: string | null;
  expenseSubmittedDate?: string | null;
  expenseConfirmedDate?: string | null;
  isPrimaryPhase4Scope?: boolean;
  scopeStatus?: string | null;
  scopeReason?: string | null;
};

export type WorkflowRequestsResponse = {
  meta: ResponseMeta;
  page: number;
  pageSize: number;
  total: number;
  rows: WorkflowRequestRow[];
};

export type InterventionMixRow = {
  interventionType: string;
  interventionSubType: string | null;
  requestCount: number;
  executedCount: number;
  executedRequestCount: number;
  matchedRequestCount: number;
  executedSnapshotCount: number;
  actionDueCount: number;
  actionDueRequestCount: number;
  actionDueSnapshotCount: number;
  matchedWithoutExecutionCount: number;
  approvedCount: number;
  reportPendingCount: number;
  confirmedContractedAmount: number | null;
  directHcpBtuSpend: number | null;
  overheadBtcSpend: number | null;
  totalActualSpend: number | null;
  fxRateStatus: FxRateStatus;
};

export type InterventionMixResponse = {
  meta: ResponseMeta;
  rows: InterventionMixRow[];
};
