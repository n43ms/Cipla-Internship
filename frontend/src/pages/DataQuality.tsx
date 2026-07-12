import { useQuery } from "@tanstack/react-query";
import { useEffect, useMemo } from "react";

import { getDataQuality } from "../api/filters";
import { DataFreshnessBanner, EmptyState, ErrorState, KpiCard, LoadingState } from "../components/common/DataStateComponents";
import { SortableHeader, useSortableRows, type SortValue } from "../components/common/SortableTable";
import type { DataQualityResponse } from "../types/api";

export function DataQuality({ onAiContextChange }: { onAiContextChange?: (context: { pageContext: string; filters: Record<string, unknown> }) => void }) {
  const quality = useQuery({ queryKey: ["data-quality"], queryFn: getDataQuality });

  useEffect(() => {
    onAiContextChange?.({ pageContext: "data_quality", filters: {} });
  }, [onAiContextChange]);

  if (quality.isLoading) return <main><LoadingState label="Loading data quality" /></main>;
  if (quality.isError) return <main className="p-6"><ErrorState title="Data quality unavailable" /></main>;
  if (!quality.data) return null;

  const data = quality.data;
  return (
    <main className="page-shell">
      <div className="mx-auto flex max-w-7xl flex-col gap-5">
        <header>
          <p className="eyebrow">Trust layer</p>
          <h1 className="page-title">Data quality</h1>
          <p className="page-copy">
            Shows freshness, row counts, validation issues, match coverage, Pcode coverage, RCPA coverage, FX quality, workflow coverage, and unmatched records before anyone acts on KPIs.
          </p>
        </header>
        <DataFreshnessBanner meta={data.meta} />
        <div className="grid min-w-0 grid-cols-1 gap-3 sm:grid-cols-2 xl:grid-cols-4">
          <KpiCard label="Loaded files" value={`${data.loadedFileCount}/${data.sourceFileCount}`} detail={data.latestIngestion.status} />
          <KpiCard label="Rows loaded" value={data.rowsLoaded.toLocaleString()} detail={`${data.rowsSkipped.toLocaleString()} skipped`} />
          <KpiCard label="Match coverage" value={`${Math.round(data.matchCoverage * 100)}%`} detail={`${data.unmatchedEventCount} unmatched records`} />
          <KpiCard label="RCPA coverage" value={`${Math.round(data.rcpaCoverage * 100)}%`} detail={`${data.rcpaCoveredMonthStart ?? "unknown"} to ${data.rcpaCoveredMonthEnd ?? "unknown"}`} />
          <KpiCard label="RCPA mapping" value={data.rcpaManualMappingCount} detail={`${data.rcpaSystemMappingCount + data.rcpaSourceMappingCount} system/source, ${data.rcpaUnknownMappingCount} unknown`} />
          <KpiCard label="Pcode coverage" value={`${Math.round(data.pcodeCoverage * 100)}%`} />
          <KpiCard label="BTU/BTC issues" value={data.btuBtcReconciliationIssueCount} />
          <KpiCard label="Workflow coverage" value={`${Math.round(data.requestWorkflowCoverage * 100)}%`} detail={`Post ${Math.round(data.postWorkflowCoverage * 100)}%`} />
        </div>
        <div className="grid min-w-0 grid-cols-1 gap-5 xl:grid-cols-2">
          <SimpleTable
            title="Source file participation"
            detail="Latest run per file. Current validation counts should be interpreted against this scope."
            headers={["File", "Type", "Status", "Loaded", "Skipped"]}
            rows={data.sourceFiles.map((row) => [
              row.sourceFile ?? "-",
              row.sourceType ?? "-",
              row.status ?? "-",
              row.rowsLoaded.toLocaleString(),
              row.rowsSkipped.toLocaleString(),
            ])}
          />
          <SimpleTable
            title="FX quality"
            detail="Official rates use company-provided FX values for dashboard conversion."
            headers={["Currency", "Status", "Rate", "Date", "Rows"]}
            rows={data.fxQuality.map((row) => [
              row.currencyCode,
              row.rateStatus,
              row.rateToUsd?.toString() ?? "-",
              row.rateDate ?? "-",
              row.rowCount.toLocaleString(),
            ])}
          />
          <SimpleTable
            title="Unmatched by source"
            detail="Primary-scope reconciliation gaps grouped by source and reason."
            headers={["Source", "Reason", "Records"]}
            rows={data.unmatchedBySource.map((row) => [row.sourceType, row.reasonCode.replaceAll("_", " "), row.recordCount.toLocaleString()])}
          />
          <SimpleTable
            title="Unmatched records"
            detail="Sample of records that need review before treating KPIs as final."
            headers={["Source", "Country", "Month", "Event", "Reason"]}
            rows={data.unmatchedRecords.map((row) => [
              row.sourceType,
              row.country,
              row.month,
              row.eventName ?? "-",
              (row.reasonCode ?? "unknown").replaceAll("_", " "),
            ])}
          />
        </div>
      </div>
    </main>
  );
}

function SimpleTable({ title, detail, headers, rows }: { title: string; detail: string; headers: string[]; rows: string[][] }) {
  const accessors = useMemo(
    () => Object.fromEntries(headers.map((_, index) => [String(index), (row: string[]) => row[index] as SortValue])) as Record<string, (row: string[]) => SortValue>,
    [headers],
  );
  const sorted = useSortableRows(rows, accessors);
  return (
    <div className="dashboard-card overflow-hidden">
      <div className="border-b border-zinc-800 p-4">
        <h2 className="font-semibold">{title}</h2>
        <p className="text-sm text-zinc-500">{detail}</p>
      </div>
      {rows.length ? (
        <div className="max-h-96 overflow-x-hidden overflow-y-auto">
          <table className="w-full table-fixed text-left text-xs lg:text-sm">
            <thead className="table-head sticky top-0">
              <tr>{headers.map((header, index) => <SortableHeader key={header} column={String(index)} label={header} sort={sorted.sort} onSort={sorted.onSort} className="px-3" />)}</tr>
            </thead>
            <tbody className="divide-y divide-zinc-800">
              {sorted.rows.map((row, index) => (
                <tr key={`${title}-${index}`}>
                  {row.map((cell, cellIndex) => (
                    <td key={`${title}-${index}-${cellIndex}`} className="truncate px-3 py-3" title={cell}>
                      {cell}
                    </td>
                  ))}
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      ) : (
        <EmptyState title={`No ${title.toLowerCase()}`} detail="No rows were returned by the backend." />
      )}
    </div>
  );
}
