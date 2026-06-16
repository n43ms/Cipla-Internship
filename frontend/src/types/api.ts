export type FxRateStatus = "official" | "provisional" | "missing";

export type ResponseMeta = {
  generatedAt: string;
  latestIngestionRunId?: string | null;
  latestIngestionStatus: string;
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
