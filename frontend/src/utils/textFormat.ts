const TERM_OVERRIDES: Record<string, string> = {
  ai: "AI",
  api: "API",
  btc: "BTC",
  btu: "BTU",
  emeu: "EMEU",
  execai: "ExecAI",
  fastapi: "FastAPI",
  fmv: "FMV",
  fs: "FS",
  fx: "FX",
  hcp: "HCP",
  hq: "HQ",
  kpi: "KPI",
  kpis: "KPIs",
  lkr: "LKR",
  msl: "MSL",
  pbp: "PBP",
  pcode: "P-code",
  pcodes: "P-codes",
  postgresql: "PostgreSQL",
  rcpa: "RCPA",
  roi: "ROI",
  rx: "Rx",
  sku: "SKU",
  supabase: "Supabase",
  usd: "USD",
};

const PHRASE_OVERRIDES: Record<string, string> = {
  action_due: "Action due",
  action_due_snapshot: "Action-due snapshot",
  action_due_snapshots: "Action-due snapshots",
  all_subtypes: "All subtypes",
  approved: "Approved",
  data_quality: "Data Quality",
  derived_from_consolidation: "Derived from consolidation",
  doctor_roi: "Doctor ROI",
  high_effort_high_reward: "High Effort / High Reward",
  high_effort_low_reward: "High Effort / Low Reward",
  high_value_engaged: "High-Value Engaged",
  high_value_unengaged: "High-Value Unengaged",
  insufficient_data: "Insufficient Data",
  low_effort_high_reward: "Low Effort / High Reward",
  low_effort_low_reward: "Low Effort / Low Reward",
  low_value_engaged: "Low-Value Engaged",
  low_value_unengaged: "Low-Value Unengaged",
  missing_btu_btc_split: "BTU/BTC split not provided",
  missing_total_actual: "Missing total actual spend",
  no_fee: "No-fee",
  no_rcpa: "No RCPA",
  not_available: "Not available",
  not_created: "Not created",
  pending_owner: "Pending owner",
  post_report_approval_pending: "Post-report approval pending",
  report_pending: "Report pending",
  request_approved_report_pending: "Request approved; report pending",
  sent_for_correction: "Sent for correction",
};

export function formatDisplayText(value: string | null | undefined, fallback = "-") {
  if (value === null || value === undefined || value.trim() === "") return fallback;
  const normalized = value.trim().replace(/\s*\/\s*/g, " / ");
  const key = normalizeKey(normalized);
  if (PHRASE_OVERRIDES[key]) return PHRASE_OVERRIDES[key];
  return normalized
    .replaceAll("_", " ")
    .replaceAll("-", " ")
    .split(/\s+/)
    .filter(Boolean)
    .map(formatToken)
    .join(" ");
}

export function formatSentenceText(value: string | null | undefined, fallback = "-") {
  if (value === null || value === undefined || value.trim() === "") return fallback;
  const trimmed = value.trim();
  if (/[.;:,]/.test(trimmed) || (/[A-Z]/.test(trimmed) && !trimmed.includes("_"))) return trimmed;
  const display = formatDisplayText(trimmed, fallback);
  if (display === fallback) return display;
  return display.replace(/^./, (letter) => letter.toUpperCase());
}

export function formatTitleText(value: string | null | undefined, fallback = "-") {
  const display = formatDisplayText(value, fallback);
  if (display === fallback) return display;
  return display
    .split(" ")
    .map((word) => {
      if (word === "/" || word === "-") return word;
      if (word.includes("/")) return word;
      if (word.includes("-")) return word.split("-").map(formatTitleWord).join("-");
      return formatTitleWord(word);
    })
    .join(" ");
}

function formatTitleWord(word: string) {
  const lower = word.toLowerCase();
  return TERM_OVERRIDES[lower] ?? `${word[0]?.toUpperCase() ?? ""}${word.slice(1).toLowerCase()}`;
}

function formatToken(token: string) {
  const lower = token.toLowerCase();
  return TERM_OVERRIDES[lower] ?? lower;
}

function normalizeKey(value: string) {
  return value.toLowerCase().replace(/[^a-z0-9]+/g, "_").replace(/^_+|_+$/g, "");
}
