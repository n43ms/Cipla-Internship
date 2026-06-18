type BadgeTone = "good" | "warn" | "muted" | "info";

const toneClass: Record<BadgeTone, string> = {
  good: "border-emerald-200 bg-emerald-50 text-emerald-700",
  warn: "border-amber-200 bg-amber-50 text-amber-700",
  muted: "border-slate-200 bg-slate-50 text-slate-600",
  info: "border-sky-200 bg-sky-50 text-sky-700",
};

export function StatusBadge({ value }: { value: string }) {
  const normalized = value.toLowerCase();
  const tone: BadgeTone =
    normalized.includes("unmatched") ||
    normalized.includes("weak") ||
    normalized.includes("pending") ||
    normalized.includes("correction") ||
    normalized.includes("rejected")
      ? "warn"
      : normalized === "matched" || normalized.includes("approved") || normalized.includes("executed")
        ? "good"
        : normalized.includes("derived")
          ? "info"
          : "muted";
  return <span className={`rounded-full border px-2 py-1 text-xs font-medium ${toneClass[tone]}`}>{value.replaceAll("_", " ")}</span>;
}

export function ConfidenceBadge({ value }: { value: number }) {
  const tone: BadgeTone = value >= 0.95 ? "good" : value >= 0.72 ? "warn" : "muted";
  return <span className={`rounded-full border px-2 py-1 text-xs font-medium ${toneClass[tone]}`}>{Math.round(value * 100)}% confidence</span>;
}

export function SourceDerivationBadge({ sourceCounts }: { sourceCounts: Record<string, number> }) {
  const derived = sourceCounts.derived_from_consolidation ?? 0;
  if (!derived) return null;
  return <span className={`rounded-full border px-2 py-1 text-xs font-medium ${toneClass.info}`}>{derived} derived from consolidation</span>;
}
