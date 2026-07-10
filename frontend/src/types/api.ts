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
  estimatedInterventionLocal: number | null;
  estimatedInterventionUsd: number;
  confirmedContractedAmountLocal: number | null;
  confirmedContractedAmountUsd: number;
  confirmedVsEstimatedVarianceLocal: number | null;
  confirmedVsEstimatedVarianceUsd: number;
  directHcpBtuSpendLocal: number | null;
  directHcpBtuSpendUsd: number;
  overheadBtcSpendLocal: number | null;
  overheadBtcSpendUsd: number;
  actualTotalSpendLocal: number | null;
  actualTotalSpendUsd: number;
  associationAmountLocal: number | null;
  unspentGapUsd: number;
  overrunAmountUsd: number;
  planWithoutSpendCount: number;
  spendWithoutPlanCount: number;
  btuBtcReconciliationIssueCount: number;
  missingFxCount: number;
  provisionalFxCount: number;
  currencyCodes: string[];
  fxRateStatuses: string[];
  localTotalsByCurrency: LocalCurrencyTotal[];
  page: number;
  pageSize: number;
  total: number;
  sort: string;
  sortDirection: string;
  rows: BudgetGapRow[];
};

export type LocalCurrencyTotal = {
  currencyCode: string;
  estimatedInterventionLocal: number;
  confirmedContractedAmountLocal: number;
  directHcpBtuSpendLocal: number;
  overheadBtcSpendLocal: number;
  actualTotalSpendLocal: number;
  associationAmountLocal: number;
  rowCount: number;
  missingFxCount: number;
  provisionalFxCount: number;
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
  rowKind: string;
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
  sponsorshipCount: number;
  noFeeEngagementCount: number;
  paidEngagementCount: number;
  firstEngagementDate: string | null;
  lastEngagementDate: string | null;
  directHcpBtuSpendUsd: number;
  overheadBtcSpendUsd: number;
  totalRoiSpendUsd: number;
  contractedEngagementAmountUsd: number;
  fmvEngagementAmountUsd: number;
  contractSavingUsd: number;
  sponsorshipEngagementAmountMissingCount: number;
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
  darkHorseUnengagedFlag: boolean;
  highValueEngagedFlag: boolean;
  hasRcpa: boolean;
  hasMissingFx: boolean;
  hasProvisionalFx: boolean;
  rcpaFirstMonth: string | null;
  rcpaLastMonth: string | null;
  rcpaMonthCount: number;
};

export type DoctorRoiResponse = {
  meta: ResponseMeta;
  page: number;
  pageSize: number;
  total: number;
  sort: string;
  sortDirection: string;
  darkHorseCount: number;
  noRcpaCount: number;
  missingFxCount: number;
  provisionalFxCount: number;
  brandFilterMode: string | null;
  periodFilterMode: string;
  rows: DoctorRoiRow[];
  quadrantCounts: Record<string, number>;
  segmentCounts: Record<string, number>;
};

export type DoctorDetailResponse = {
  meta: ResponseMeta;
  profile: DoctorRoiRow;
  sponsorshipOutcome: {
    sponsorshipCount: number;
    paidEngagementCount: number;
    noFeeEngagementCount: number;
    paidServiceCount: number;
    contractedAmountUsd: number;
    fmvAmountUsd: number;
    contractSavingUsd: number;
    doctorAttributableExpenseLocal: number;
    knownEngagementInvestmentUsd: number;
    preWindowCiplaRxQty: number;
    postWindowCiplaRxQty: number;
    associatedRxMovementQty: number;
    preWindowMonthCount: number;
    postWindowMonthCount: number;
    evidenceConfidence: string;
    evidenceCaveats: string[];
  } | null;
  engagementHistory: Array<{
    requestId: string | null;
    interventionName: string | null;
    interventionType: string | null;
    interventionSubtype: string | null;
    month: string | null;
    actualInterventionDate: string | null;
    expectedInterventionDate: string | null;
    totalRoiSpendUsd: number | null;
    contractedAmountUsd: number | null;
    fmvAmountUsd: number | null;
    contractSavingUsd: number | null;
    fxRateStatus: string | null;
    evidenceSource: string;
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
  brands: FilterOption[];
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

export type TerritoryOpportunityRow = {
  countryCode: string;
  countryName: string;
  territoryName: string;
  patchName: string | null;
  firstMonth: string | null;
  lastMonth: string | null;
  doctorCount: number;
  engagedDoctorCount: number;
  ciplaPrescriptionQty: number;
  competitorPrescriptionQty: number;
  totalPrescriptionQty: number;
  ciplaShareQty: number | null;
  prescriptionsPerDoctor: number | null;
  engagementCount: number;
  sponsorshipCount: number;
  paidEngagementCount: number;
  noFeeEngagementCount: number;
  engagementsPerDoctor: number | null;
  contractedAmountUsd: number;
  fmvAmountUsd: number;
  contractSavingUsd: number;
  knownInvestmentUsd: number;
  manualMappingCount: number;
  unknownMappingCount: number;
  missingAmountCount: number;
  opportunityLabel: string;
  evidenceConfidence: "high" | "medium" | "low" | string;
  sourceCaveats: string[];
};

export type TerritoryOpportunityResponse = {
  meta: ResponseMeta;
  page: number;
  pageSize: number;
  total: number;
  rows: TerritoryOpportunityRow[];
  labelCounts: Record<string, number>;
};

export type UploadFileResult = {
  originalFilename: string;
  savedFilename: string | null;
  status: "accepted" | "quarantined";
  sourceType: string;
  fileFormat: string;
  confidence: number;
  rowsSeen: number;
  sheetCount: number;
  canonicalSheets: string[];
  warnings: string[];
  reasons: string[];
};

export type UploadBatchResponse = {
  batchId: string;
  refreshState: string;
  totalFiles: number;
  acceptedCount: number;
  quarantinedCount: number;
  manifestPath: string | null;
  summaryPath: string | null;
  files: UploadFileResult[];
  nextSteps: string[];
};

export type BatchIngestionStatusResponse = {
  batchId: string;
  refreshState: string;
  acceptedCount: number;
  quarantinedCount: number;
  ingestionRunId: string | null;
  rowsSeen: number;
  rowsLoaded: number;
  rowsSkipped: number;
  warningCount: number;
  errorCount: number;
  manifestPath: string | null;
  summaryPath: string | null;
  message: string;
  nextSteps: string[];
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
  rcpaManualMappingCount: number;
  rcpaSystemMappingCount: number;
  rcpaSourceMappingCount: number;
  rcpaUnknownMappingCount: number;
  rcpaCoveredMonthStart: string | null;
  rcpaCoveredMonthEnd: string | null;
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
  serialMonthParseCount: number;
  staticFxSeedDate: string | null;
  officialLkrRateToUsd: number | null;
  actualAttendanceMissingPcodeCount: number;
  unallocatedDoctorSpendLocal: number;
  unallocatedDoctorSpendUsd: number;
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
  sourceFiles: Array<{
    sourceFile: string | null;
    sourceType: string | null;
    status: string | null;
    rowsSeen: number;
    rowsLoaded: number;
    rowsSkipped: number;
    warningCount: number;
    errorCount: number;
    periodStart: string | null;
    periodEnd: string | null;
    storageMode: string;
    rowCountNote: string | null;
  }>;
  unmatchedBySource: Array<{
    sourceType: string;
    reasonCode: string;
    recordCount: number;
  }>;
  unmatchedRecords: Array<{
    sourceType: string;
    country: string;
    month: string;
    eventName: string | null;
    eventType: string | null;
    reasonCode: string | null;
    reasonDetail: string | null;
    candidateMatch: string | null;
    confidence: number;
  }>;
  fxQuality: Array<{
    currencyCode: string;
    rateStatus: string;
    rateToUsd: number | null;
    rateDate: string | null;
    source: string | null;
    rowCount: number;
  }>;
};

export type UnmatchedRecordsResponse = {
  meta: ResponseMeta;
  page: number;
  pageSize: number;
  total: number;
  rows: DataQualityResponse["unmatchedRecords"];
};

export type AiQueryRequest = {
  question: string;
  pageContext?: string | null;
  filters?: Record<string, unknown>;
};

export type AiDashboardPointer = {
  page: string;
  section: string;
  detail: string;
  reason: string;
};

export type AiEvidenceRef = {
  section: string;
  label: string;
  value?: string | number | boolean | null;
  sourcePath?: string | null;
};

export type AiAgentStep = {
  step: string;
  status: "completed" | "fallback";
};

export type AiContextScope = {
  pageContext: string;
  filters: Record<string, unknown>;
  topN: number;
  maxCharacters: number;
  sections: string[];
};

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
