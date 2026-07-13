import type { ReactNode } from "react";

export const CHART_COLORS = {
  cyan: "#67e8f9",
  sky: "#7dd3fc",
  emerald: "#6ee7b7",
  green: "#34d399",
  amber: "#fcd34d",
  orange: "#fb923c",
  rose: "#fb7185",
  violet: "#c4b5fd",
  zinc: "#a1a1aa",
};

export const CHART_AXIS_TICK = { fill: "#a1a1aa", fontSize: 11 };
export const CHART_GRID_PROPS = {
  stroke: "rgba(161,161,170,0.18)",
  strokeDasharray: "4 6",
};
export const CHART_TOOLTIP_CURSOR = { fill: "rgba(103,232,249,0.07)", stroke: "rgba(103,232,249,0.18)" };
export const CHART_TOOLTIP_PROPS = {
  contentStyle: {
    background: "rgba(13, 17, 19, 0.96)",
    border: "1px solid rgba(103, 232, 249, 0.22)",
    borderRadius: 8,
    boxShadow: "0 18px 44px rgba(0,0,0,0.42)",
    color: "#e4e4e7",
  },
  labelStyle: { color: "#f4f4f5", fontWeight: 600 },
  itemStyle: { color: "#d4d4d8" },
};
export const CHART_LEGEND_PROPS = {
  iconType: "circle" as const,
  wrapperStyle: { color: "#d4d4d8", fontSize: 12, paddingTop: 8 },
};

export function ChartLegendPills({ items }: { items: Array<{ label: string; color: string; detail?: ReactNode }> }) {
  return (
    <div className="mt-3 flex flex-wrap gap-2 text-xs">
      {items.map((item) => (
        <span key={item.label} className="inline-flex items-center gap-2 rounded-full border border-white/[0.07] bg-white/[0.035] px-2.5 py-1 text-zinc-300">
          <span className="h-2.5 w-2.5 rounded-full shadow-[0_0_14px_rgba(103,232,249,0.26)]" style={{ backgroundColor: item.color }} />
          <span>{item.label}</span>
          {item.detail ? <span className="text-zinc-500">{item.detail}</span> : null}
        </span>
      ))}
    </div>
  );
}

export function compactChartValue(value: number) {
  return Intl.NumberFormat(undefined, { notation: "compact", maximumFractionDigits: 1 }).format(value);
}
