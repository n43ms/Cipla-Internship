import { LoaderCircle } from "lucide-react";

export function TableLoadingOverlay({
  isFetching,
  label = "Refreshing table",
}: {
  isFetching: boolean;
  label?: string;
}) {
  if (!isFetching) return null;

  return (
    <div
      className="pointer-events-none absolute inset-0 z-10 grid place-items-center bg-[#111315]/55 backdrop-blur-[1px]"
      role="status"
      aria-live="polite"
    >
      <div className="flex items-center gap-2 rounded-lg border border-accent/15 bg-zinc-950/85 px-3 py-2 text-xs text-zinc-300 shadow-lg shadow-black/25">
        <LoaderCircle aria-hidden="true" className="h-4 w-4 animate-spin text-accent" />
        {label}
      </div>
    </div>
  );
}
