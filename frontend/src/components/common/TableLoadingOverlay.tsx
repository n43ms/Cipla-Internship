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
      className="pointer-events-none absolute inset-0 z-10 bg-[#111315]/18 backdrop-blur-[1.5px]"
      role="status"
      aria-live="polite"
    >
      <div className="absolute inset-x-0 top-[5.95rem] flex justify-center px-4">
        <div className="flex items-center gap-3 rounded-full border border-accent/20 bg-zinc-950/65 px-4 py-3 text-sm font-medium text-zinc-300 shadow-2xl shadow-black/30 ring-1 ring-white/[0.035] backdrop-blur-xl">
        <span className="relative flex h-9 w-9 items-center justify-center">
          <span className="absolute inset-0 animate-ping rounded-full bg-accent/10" />
          <LoaderCircle aria-hidden="true" className="relative h-9 w-9 animate-spin text-accent/90" strokeWidth={1.8} />
        </span>
        <span>{label}</span>
        </div>
      </div>
    </div>
  );
}
