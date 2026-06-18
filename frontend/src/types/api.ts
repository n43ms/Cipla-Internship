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
  plannedBudgetUsd: number;
  estimatedInterventionLocal: number;
  estimatedInterventionUsd: number;
  confirmedContractedAmountLocal: number;
  confirmedContractedAmountUsd: number;
  confirmedVsEstimatedVarianceLocal: number;
  confirmedVsEstimatedVarianceUsd: number;
  directHcpBtuSpendLocal: number;
  directHcpBtuSpendUsd: number;
  overheadBtcSpendLocal: number;
  overheadBtcSpendUsd: number;
  actualTotalSpendLocal: number;
  actualTotalSpendUsd: number;
  associationAmountLocal: number;
  unspentGapUsd: number;
  overrunAmountUsd: number;
  planWithoutSpendCount: number;
  spendWithoutPlanCount: number;
  btuBtcReconciliationIssueCount: number;
  missingFxCount: number;
  provisionalFxCount: number;
  currencyCodes: string[];
  fxRateStatuses: string[];
  rows: BudgetGapRow[];
};

export type BudgetGapRow = {
  eventName: string | null;
  eventType: string | null;
  country: string;
  month: string;
  matchStatus: string;
  plannedBudgetUsd?: number | null;
  estimatedInterventionLocal?: number | null;
  confirmedContractedAmountLocal?: number | null;
  actualTotalExpenseLocal?: number | null;
  directHcpBtuSpendLocal?: number | null;
  overheadBtcSpendLocal?: number | null;
  actualTotalExpenseUsd?: number | null;
  unspentGapUsd?: number | null;
  overrunAmountUsd?: number | null;
  currencyCode?: string | null;
  fxRateStatus: string;
  btuBtcReconciliationStatus: string;
  spendWithoutPlan: boolean;
  planWithoutSpend: boolean;
  scopeStatus?: string | null;
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

export type DoctorRoiRow = {
  countryCode: string;
  countryName: string;
  pcodeNormalized: string;
  doctorName: string | null;
  speciality: string | null;
  doctorClass: string | null;
  activeStatus: string | null;
  engagementCount: number;
  lastEngagementDate: string | null;
  directHcpBtuSpendUsd: number;
  overheadBtcSpendUsd: number;
  totalRoiSpendUsd: number;
  ciplaPrescriptionQty: number;
  competitorPrescriptionQty: number;
  totalPrescriptionQty: number;
  ciplaShareQty: number | null;
  spendPerCiplaPrescriptionUsd: number | null;
  roiSegment: string;
  quadrantX: number;
  quadrantY: number;
  quadrantLabel: string;
  darkHorseFlag: boolean;
  hasRcpa: boolean;
  hasMissingFx: boolean;
  hasProvisionalFx: boolean;
};

export type DoctorRoiResponse = {
  meta: ResponseMeta;
  page: number;
  pageSize: number;
  total: number;
  rows: DoctorRoiRow[];
  quadrantCounts: Record<string, number>;
  segmentCounts: Record<string, number>;
};

export type DoctorDetailResponse = {
  meta: ResponseMeta;
  profile: DoctorRoiRow;
  engagementHistory: Array<{
    requestId: string | null;
    interventionName: string | null;
    interventionType: string | null;
    month: string | null;
    actualInterventionDate: string | null;
    totalRoiSpendUsd: number | null;
    fxRateStatus: string | null;
  }>;
  prescriptionTrend: Array<{
    month: string;
    ciplaPrescriptionQty: number;
    competitorPrescriptionQty: number;
    totalPrescriptionQty: number;
  }>;
  brandMix: Array<{
    brandGroup: string;
    ownOrCompetitor: string;
    prescriptionQty: number;
    prescriptionValueLocal: number;
  }>;
};

export type FilterOption = {
  value: string;
  label: string;
};

export type FiltersResponse = {
  countries: FilterOption[];
  months: FilterOption[];
  interventionTypes: FilterOption[];
  specialities: FilterOption[];
  doctorClasses: FilterOption[];
  roiSegments: FilterOption[];
  latestIngestionStatus: string;
};

export type IngestionLatestResponse = {
  id: string | null;
  status: string;
  startedAt: string | null;
  completedAt: string | null;
  sourceFileCount: number;
  totalRowsSeen: number;
  totalRowsLoaded: number;
  totalRowsSkipped: number;
  warningCount: number;
  errorCount: number;
};

export type DataQualityResponse = {
  meta: ResponseMeta;
  latestIngestion: IngestionLatestResponse;
  sourceFileCount: number;
  loadedFileCount: number;
  rowsSeen: number;
  rowsLoaded: number;
  rowsSkipped: number;
  validationErrorCount: number;
  validationWarningCount: number;
  matchCoverage: number;
  pcodeCoverage: number;
  rcpaCoverage: number;
  missingFxCount: number;
  provisionalFxCount: number;
  btuBtcReconciliationIssueCount: number;
  missingConfirmedAmountCount: number;
  spendWithoutPlanCount: number;
  planWithoutSpendCount: number;
  requestWorkflowCoverage: number;
  postWorkflowCoverage: number;
  interventionTypeCoverage: number;
  unmatchedEventCount: number;
  derivedSnapshotCount: number;
  staleIngestion: boolean;
  validationIssues: Array<{
    severity: string;
    sourceFile: string | null;
    sheetName: string | null;
    rowNumber: number | null;
    entityType: string | null;
    fieldName: string | null;
    errorCode: string;
    message: string;
  }>;
};
