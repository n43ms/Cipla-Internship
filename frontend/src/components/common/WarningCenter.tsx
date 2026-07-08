import { AlertTriangle, CheckCircle2, Info, X } from "lucide-react";
import {
  createContext,
  useContext,
  useEffect,
  useMemo,
  useState,
  type ReactNode,
} from "react";

export type WarningTone = "info" | "warning" | "success";

export type WarningRecord = {
  id: string;
  title: string;
  items: string[];
  detail?: string;
  tone?: WarningTone;
};

type WarningCenterContextValue = {
  register: (record: WarningRecord) => void;
  unregister: (id: string) => void;
};

const WarningCenterContext = createContext<WarningCenterContextValue>({
  register: () => undefined,
  unregister: () => undefined,
});

const WarningRecordsContext = createContext<WarningRecord[]>([]);

export function WarningCenterProvider({ children }: { children: ReactNode }) {
  const [recordsById, setRecordsById] = useState<Record<string, WarningRecord>>({});
  const records = useMemo(
    () =>
      Object.values(recordsById)
        .map((record) => ({
          ...record,
          items: Array.from(new Set(record.items.map((item) => item.trim()).filter(Boolean))),
        }))
        .filter((record) => record.items.length > 0),
    [recordsById],
  );
  const contextValue = useMemo<WarningCenterContextValue>(
    () => ({
      register: (record) => setRecordsById((current) => ({ ...current, [record.id]: record })),
      unregister: (id) =>
        setRecordsById((current) => {
          const next = { ...current };
          delete next[id];
          return next;
        }),
    }),
    [],
  );

  return (
    <WarningCenterContext.Provider value={contextValue}>
      <WarningRecordsContext.Provider value={records}>{children}</WarningRecordsContext.Provider>
    </WarningCenterContext.Provider>
  );
}

export function WarningRegistration({ record }: { record: WarningRecord | null }) {
  const { register, unregister } = useContext(WarningCenterContext);
  const itemSignature = record?.items.join("\u0000") ?? "";
  const normalizedRecord = useMemo(
    () =>
      record
        ? {
            ...record,
            items: Array.from(new Set(record.items.map((item) => item.trim()).filter(Boolean))),
          }
        : null,
    [itemSignature, record?.detail, record?.id, record?.title, record?.tone],
  );

  useEffect(() => {
    if (!normalizedRecord || normalizedRecord.items.length === 0) return undefined;
    register(normalizedRecord);
    return () => unregister(normalizedRecord.id);
  }, [normalizedRecord, register, unregister]);

  return null;
}

export function WarningCenterDock() {
  const records = useContext(WarningRecordsContext);
  const [open, setOpen] = useState(false);
  const totalItems = records.reduce((sum, record) => sum + record.items.length, 0);

  useEffect(() => {
    if (records.length === 0) setOpen(false);
  }, [records.length]);

  if (records.length === 0) return null;

  return (
    <>
      <button
        type="button"
        className={`warning-dock-toggle ${open ? "warning-dock-toggle-open" : ""}`}
        onClick={() => setOpen((value) => !value)}
        aria-expanded={open}
        aria-controls="warning-dock"
        aria-label={open ? "Close data warning notes" : "Open data warning notes"}
      >
        <AlertTriangle className="h-4 w-4" />
        <span>Data warning notes</span>
        <span className="rounded-full bg-amber-300/15 px-1.5 py-0.5 text-[0.62rem] text-amber-100">
          {totalItems}
        </span>
      </button>

      <aside
        id="warning-dock"
        className={`warning-dock ${open ? "translate-x-0 opacity-100" : "pointer-events-none translate-x-[calc(100%+1rem)] opacity-0"}`}
        aria-hidden={!open}
      >
        <div className="flex h-full min-h-0 flex-col overflow-hidden rounded-l-2xl border border-white/[0.1] bg-[#0b0e10]/95 shadow-[0_24px_80px_rgba(0,0,0,0.46)] backdrop-blur-2xl">
          <div className="border-b border-white/[0.08] bg-white/[0.035] p-4">
            <div className="flex items-start justify-between gap-3">
              <div>
                <div className="flex items-center gap-2 text-zinc-300">
                  <AlertTriangle className="h-4 w-4 text-amber-300" />
                  <p className="text-xs font-semibold uppercase tracking-[0.2em] text-amber-100">
                    Data warning notes
                  </p>
                </div>
                
              </div>
              <button
                type="button"
                className="soft-button rounded-md p-2"
                onClick={() => setOpen(false)}
                aria-label="Close data warning notes"
              >
                <X className="h-4 w-4" />
              </button>
            </div>
          </div>
          <div className="min-h-0 flex-1 space-y-3 overflow-y-auto p-4">
            {records.map((record) => (
              <WarningGroup key={record.id} record={record} />
            ))}
          </div>
        </div>
      </aside>
    </>
  );
}

function WarningGroup({ record }: { record: WarningRecord }) {
  const Icon = record.tone === "info" ? Info : record.tone === "success" ? CheckCircle2 : AlertTriangle;
  const toneClasses =
    record.tone === "success"
      ? {
          section: "border-emerald-300/10 bg-emerald-300/[0.018]",
          icon: "text-emerald-300/75",
          title: "text-zinc-100",
          item: "border-emerald-300/[0.07] bg-white/[0.018] text-zinc-300",
        }
      : record.tone === "info"
        ? {
            section: "border-sky-300/10 bg-sky-300/[0.018]",
            icon: "text-sky-300/75",
            title: "text-zinc-100",
            item: "border-sky-300/[0.07] bg-white/[0.018] text-zinc-300",
          }
        : {
            section: "border-amber-300/10 bg-amber-300/[0.02]",
            icon: "text-amber-300/75",
            title: "text-zinc-100",
            item: "border-amber-300/[0.075] bg-amber-300/[0.018] text-zinc-300",
          };
  return (
    <section className={`rounded-xl border p-3 ${toneClasses.section}`}>
      <div className="flex items-start gap-2">
        <Icon className={`mt-0.5 h-4 w-4 shrink-0 ${toneClasses.icon}`} />
        <div className="min-w-0">
          <p className={`text-sm font-medium ${toneClasses.title}`}>{record.title}</p>
          {record.detail ? <p className="mt-1 text-xs leading-5 text-zinc-500">{record.detail}</p> : null}
        </div>
      </div>
      <ul className="mt-3 space-y-2 text-xs leading-5 text-zinc-300">
        {record.items.map((item) => (
          <li key={item} className={`flex gap-2 rounded-lg border px-3 py-2 ${toneClasses.item}`}>
            <span>{humanize(item)}</span>
          </li>
        ))}
      </ul>
    </section>
  );
}

function humanize(value: string) {
  return value.replaceAll("_", " ");
}
