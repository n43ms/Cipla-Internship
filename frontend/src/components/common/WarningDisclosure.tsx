import { AlertTriangle, CheckCircle2, ChevronDown, Info } from "lucide-react";
import { useMemo, useState, type ReactNode } from "react";

export type WarningTone = "neutral" | "info" | "warning" | "success";

type WarningDisclosureProps = {
  title: string;
  items?: string[];
  detail?: string;
  tone?: WarningTone;
  defaultOpen?: boolean;
  emptyLabel?: string;
  action?: ReactNode;
  className?: string;
};

export function WarningDisclosure({
  title,
  items = [],
  detail,
  tone = "warning",
  defaultOpen = false,
  emptyLabel = "No limitations reported",
  action,
  className = "",
}: WarningDisclosureProps) {
  const uniqueItems = useMemo(
    () => Array.from(new Set(items.map((item) => item.trim()).filter(Boolean))),
    [items],
  );
  const [open, setOpen] = useState(defaultOpen);
  const hasItems = uniqueItems.length > 0;
  const Icon = hasItems ? (tone === "info" ? Info : AlertTriangle) : CheckCircle2;
  const palette = paletteFor(tone, hasItems);

  return (
    <section className={`rounded-lg border ${palette.frame} ${className}`}>
      <button
        type="button"
        className="flex w-full items-center justify-between gap-3 px-4 py-3 text-left transition-colors duration-200 hover:bg-white/[0.025] focus:outline-none focus-visible:ring-2 focus-visible:ring-accent/25"
        onClick={() => hasItems && setOpen((value) => !value)}
        aria-expanded={hasItems ? open : undefined}
      >
        <span className="flex min-w-0 items-center gap-3">
          <span className={`grid h-8 w-8 shrink-0 place-items-center rounded-md ${palette.iconBg}`}>
            <Icon aria-hidden="true" className={`h-4 w-4 ${palette.icon}`} />
          </span>
          <span className="min-w-0">
            <span className="block text-sm font-medium text-zinc-100">{title}</span>
            <span className="block truncate text-xs text-zinc-500">
              {hasItems ? `${uniqueItems.length} ${uniqueItems.length === 1 ? "note" : "notes"} available` : emptyLabel}
              {detail ? ` · ${detail}` : ""}
            </span>
          </span>
        </span>
        <span className="flex shrink-0 items-center gap-2">
          {action}
          {hasItems ? (
            <ChevronDown
              aria-hidden="true"
              className={`h-4 w-4 text-zinc-500 transition-transform duration-200 ${open ? "rotate-180" : ""}`}
            />
          ) : null}
        </span>
      </button>
      {hasItems && open ? (
        <div className="border-t border-white/[0.06] px-4 py-3">
          <ul className="grid grid-cols-1 gap-2 text-xs text-zinc-300 sm:grid-cols-2">
            {uniqueItems.map((item) => (
              <li key={item} className="rounded-md border border-white/[0.06] bg-black/20 px-3 py-2 leading-5">
                {humanize(item)}
              </li>
            ))}
          </ul>
        </div>
      ) : null}
    </section>
  );
}

function paletteFor(tone: WarningTone, hasItems: boolean) {
  if (!hasItems) {
    return {
      frame: "border-emerald-300/15 bg-emerald-300/[0.035]",
      iconBg: "bg-emerald-300/[0.08]",
      icon: "text-emerald-200",
    };
  }
  if (tone === "info") {
    return {
      frame: "border-cyan-300/15 bg-cyan-300/[0.035]",
      iconBg: "bg-cyan-300/[0.08]",
      icon: "text-cyan-200",
    };
  }
  if (tone === "neutral") {
    return {
      frame: "border-white/[0.08] bg-white/[0.025]",
      iconBg: "bg-white/[0.06]",
      icon: "text-zinc-300",
    };
  }
  return {
    frame: "border-amber-300/15 bg-amber-300/[0.035]",
    iconBg: "bg-amber-300/[0.08]",
    icon: "text-amber-200",
  };
}

function humanize(value: string) {
  return value.replaceAll("_", " ");
}
