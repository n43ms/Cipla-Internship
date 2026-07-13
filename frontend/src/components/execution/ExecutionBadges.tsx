import { formatTitleText } from "../../utils/textFormat";

type BadgeTone = "good" | "warn" | "muted" | "info";

const toneClass: Record<BadgeTone, string> = {
  good: "border-emerald-300/20 bg-emerald-300/[0.07] text-emerald-200/75",
  warn: "border-amber-300/20 bg-amber-300/[0.07] text-amber-200/75",
  muted: "border-zinc-700 bg-zinc-800/70 text-zinc-400",
  info: "border-cyan-300/20 bg-cyan-300/[0.07] text-cyan-200/75",
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
  return <span className={`rounded-full border px-2 py-1 text-xs font-medium ${toneClass[tone]}`}>{formatTitleText(value)}</span>;
}

export function ConfidenceBadge({ value }: { value: number }) {
  const tone: BadgeTone = value >= 0.95 ? "good" : value >= 0.72 ? "warn" : "muted";
  return <span className={`rounded-full border px-2 py-1 text-xs font-medium ${toneClass[tone]}`}>{Math.round(value * 100)}% confidence</span>;
}

export function SourceDerivationBadge({ sourceCounts }: { sourceCounts: Record<string, number> }) {
  const derived = sourceCounts.derived_from_consolidation ?? 0;
  if (!derived) return null;
  return <span className={`rounded-full border px-2 py-1 text-xs font-medium ${toneClass.info}`}>{derived} Derived from consolidation</span>;
}
