import { useMemo, useState, type ChangeEvent } from "react";
import { AlertTriangle, CheckCircle2, FileSpreadsheet, Upload, XCircle } from "lucide-react";

import { uploadDataFiles } from "../../api/ingestion";
import type { UploadBatchResponse, UploadFileResult } from "../../types/api";

type DataUploadPanelProps = {
  onClose: () => void;
};

const SOURCE_LABELS: Record<string, string> = {
  consolidation: "Consolidated intervention report",
  doctor_contract: "Doctor contract report",
  rcpa: "RCPA report",
  msl_doctor_master: "Doctor master",
  ers_conference: "ERS conference file",
  cleaned_presentable: "Cleaned reference report",
  unknown: "Unknown file",
};

export function DataUploadPanel({ onClose }: DataUploadPanelProps) {
  const [files, setFiles] = useState<File[]>([]);
  const [result, setResult] = useState<UploadBatchResponse | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [uploading, setUploading] = useState(false);
  const totalSize = useMemo(
    () => files.reduce((sum, file) => sum + file.size, 0),
    [files],
  );

  function handleFiles(event: ChangeEvent<HTMLInputElement>) {
    setResult(null);
    setError(null);
    setFiles(Array.from(event.target.files ?? []));
  }

  async function handleUpload() {
    if (!files.length || uploading) return;
    setUploading(true);
    setError(null);
    setResult(null);
    try {
      setResult(await uploadDataFiles(files));
    } catch {
      setError("Upload failed. Check that the backend is running and try again.");
    } finally {
      setUploading(false);
    }
  }

  return (
    <div className="flex min-h-full flex-col gap-5">
      <header className="border-b border-white/[0.08] pb-4">
        <p className="eyebrow">Data refresh</p>
        <h2 className="mt-2 text-2xl font-semibold text-zinc-50">Upload new data/files</h2>
        <p className="mt-2 text-sm leading-6 text-zinc-400">
          Upload the original Excel exports. The system checks the files first and will not change
          the dashboard until the batch is accepted for ingestion.
        </p>
      </header>

      <label className="group grid cursor-pointer place-items-center rounded-lg border border-dashed border-accent/35 bg-accent/[0.045] px-5 py-8 text-center transition hover:border-accent/60 hover:bg-accent/[0.07]">
        <FileSpreadsheet className="h-9 w-9 text-accent" />
        <span className="mt-3 text-sm font-semibold text-zinc-100">
          Choose Excel files
        </span>
        <span className="mt-1 text-xs text-zinc-500">Supports .xlsx, .xlsb, and CRM .xls exports</span>
        <input
          className="sr-only"
          type="file"
          multiple
          accept=".xlsx,.xlsb,.xls"
          onChange={handleFiles}
        />
      </label>

      {files.length ? (
        <section className="rounded-lg border border-white/[0.08] bg-black/20">
          <div className="flex items-center justify-between gap-3 border-b border-white/[0.08] px-4 py-3">
            <div>
              <p className="text-sm font-semibold text-zinc-100">{files.length} file(s) selected</p>
              <p className="text-xs text-zinc-500">{formatBytes(totalSize)} total</p>
            </div>
            <button
              type="button"
              className="soft-button rounded-md px-3 py-2 text-xs"
              onClick={() => {
                setFiles([]);
                setResult(null);
                setError(null);
              }}
            >
              Clear
            </button>
          </div>
          <div className="max-h-44 overflow-y-auto px-4 py-2">
            {files.map((file) => (
              <div key={`${file.name}-${file.size}`} className="flex items-center justify-between gap-3 py-2 text-sm">
                <span className="min-w-0 truncate text-zinc-300">{file.name}</span>
                <span className="shrink-0 text-xs text-zinc-500">{formatBytes(file.size)}</span>
              </div>
            ))}
          </div>
        </section>
      ) : null}

      {error ? (
        <div className="rounded-lg border border-red-400/20 bg-red-500/[0.08] p-4 text-sm text-red-100">
          {error}
        </div>
      ) : null}

      {result ? <UploadResult result={result} /> : null}

      <div className="mt-auto flex flex-col gap-2 border-t border-white/[0.08] pt-4 sm:flex-row">
        <button
          type="button"
          className="soft-button inline-flex items-center justify-center gap-2 rounded-md border-accent/25 bg-accent/[0.1] px-4 py-2.5 text-sm font-semibold text-zinc-50 disabled:cursor-not-allowed disabled:opacity-50"
          disabled={!files.length || uploading}
          onClick={handleUpload}
        >
          <Upload className="h-4 w-4" />
          {uploading ? "Checking files..." : "Upload and check files"}
        </button>
        <button type="button" className="soft-button rounded-md px-4 py-2.5 text-sm" onClick={onClose}>
          Close
        </button>
      </div>
    </div>
  );
}

function UploadResult({ result }: { result: UploadBatchResponse }) {
  return (
    <section className="rounded-lg border border-white/[0.08] bg-[#101214]">
      <div className="grid grid-cols-3 divide-x divide-white/[0.08] border-b border-white/[0.08] text-center">
        <ResultMetric label="Uploaded" value={result.totalFiles} />
        <ResultMetric label="Accepted" value={result.acceptedCount} tone="good" />
        <ResultMetric label="Rejected" value={result.quarantinedCount} tone="warn" />
      </div>
      <div className="divide-y divide-white/[0.08]">
        {result.files.map((file) => <FileResultRow key={file.originalFilename} file={file} />)}
      </div>
      <div className="border-t border-white/[0.08] p-4">
        <p className="text-xs font-semibold uppercase tracking-wide text-zinc-500">Next steps</p>
        <ul className="mt-2 space-y-1 text-sm text-zinc-400">
          {result.nextSteps.map((step) => <li key={step}>{step}</li>)}
        </ul>
      </div>
    </section>
  );
}

function ResultMetric({ label, value, tone }: { label: string; value: number; tone?: "good" | "warn" }) {
  const color = tone === "good" ? "text-emerald-300" : tone === "warn" ? "text-amber-300" : "text-zinc-50";
  return (
    <div className="p-4">
      <p className={`text-2xl font-semibold ${color}`}>{value}</p>
      <p className="mt-1 text-xs uppercase tracking-wide text-zinc-500">{label}</p>
    </div>
  );
}

function FileResultRow({ file }: { file: UploadFileResult }) {
  const accepted = file.status === "accepted";
  const Icon = accepted ? CheckCircle2 : XCircle;
  return (
    <div className="p-4">
      <div className="flex items-start gap-3">
        <Icon className={`mt-0.5 h-5 w-5 shrink-0 ${accepted ? "text-emerald-300" : "text-amber-300"}`} />
        <div className="min-w-0 flex-1">
          <p className="truncate text-sm font-semibold text-zinc-100">{file.originalFilename}</p>
          <p className="mt-1 text-xs text-zinc-500">
            {SOURCE_LABELS[file.sourceType] ?? file.sourceType} · {file.fileFormat}
            {accepted ? ` · ${file.rowsSeen.toLocaleString()} rows seen` : ""}
          </p>
          {file.reasons.length ? (
            <div className="mt-3 rounded-md border border-amber-300/16 bg-amber-300/[0.06] p-3">
              {file.reasons.map((reason) => (
                <p key={reason} className="flex gap-2 text-xs leading-5 text-amber-100/85">
                  <AlertTriangle className="mt-0.5 h-3.5 w-3.5 shrink-0" />
                  {reason}
                </p>
              ))}
            </div>
          ) : null}
        </div>
      </div>
    </div>
  );
}

function formatBytes(value: number) {
  if (value < 1024) return `${value} B`;
  if (value < 1024 * 1024) return `${(value / 1024).toFixed(1)} KB`;
  return `${(value / (1024 * 1024)).toFixed(1)} MB`;
}
