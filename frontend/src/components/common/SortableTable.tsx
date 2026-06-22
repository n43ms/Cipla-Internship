import { useMemo, useState } from "react";
import { ArrowDown, ArrowUp, ArrowUpDown } from "lucide-react";

export type SortDirection = "asc" | "desc";
export type SortValue = string | number | boolean | null | undefined;
export type SortState<Key extends string = string> = { key: Key; direction: SortDirection };

type SortableHeaderProps<Key extends string> = {
  column: Key;
  label: string;
  sort: SortState<Key> | null;
  onSort: (column: Key) => void;
  className?: string;
};

export function SortableHeader<Key extends string>({ column, label, sort, onSort, className = "" }: SortableHeaderProps<Key>) {
  const active = sort?.key === column;
  const direction = active ? sort.direction : null;
  const ariaSort = direction === "asc" ? "ascending" : direction === "desc" ? "descending" : "none";
  return (
    <th className={`px-4 py-3 ${className}`} aria-sort={ariaSort} scope="col">
      <button
        type="button"
        className="group inline-flex min-h-7 items-center gap-1.5 whitespace-nowrap rounded-sm text-left font-semibold transition-colors duration-200 hover:text-zinc-200 focus:outline-none focus-visible:ring-2 focus-visible:ring-accent/35"
        onClick={() => onSort(column)}
        title={`${active ? `Sorted ${direction}. ` : ""}Click to sort ${direction === "asc" ? "descending" : "ascending"}`}
      >
        <span>{label}</span>
        {direction === "asc" ? (
          <ArrowUp aria-hidden="true" className="h-3.5 w-3.5 text-emerald-400" strokeWidth={2.4} />
        ) : direction === "desc" ? (
          <ArrowDown aria-hidden="true" className="h-3.5 w-3.5 text-rose-400" strokeWidth={2.4} />
        ) : (
          <ArrowUpDown aria-hidden="true" className="h-3.5 w-3.5 text-zinc-600 transition-colors duration-200 group-hover:text-zinc-400" />
        )}
        <span className="sr-only">{active ? `Sorted ${direction}` : "Not sorted"}</span>
      </button>
    </th>
  );
}

export function nextSort<Key extends string>(current: SortState<Key> | null, column: Key): SortState<Key> {
  if (current?.key === column) {
    return { key: column, direction: current.direction === "asc" ? "desc" : "asc" };
  }
  return { key: column, direction: "asc" };
}

export function useSortableRows<T, Key extends string>(
  rows: readonly T[],
  accessors: Record<Key, (row: T) => SortValue>,
  initialSort: SortState<Key> | null = null,
) {
  const [sort, setSort] = useState<SortState<Key> | null>(initialSort);
  const sortedRows = useMemo(() => {
    if (!sort) return [...rows];
    const accessor = accessors[sort.key];
    const multiplier = sort.direction === "asc" ? 1 : -1;
    return [...rows].sort((left, right) => multiplier * compareSortValues(accessor(left), accessor(right)));
  }, [accessors, rows, sort]);

  return {
    rows: sortedRows,
    sort,
    onSort: (column: Key) => setSort((current) => nextSort(current, column)),
  };
}

function compareSortValues(left: SortValue, right: SortValue) {
  if (left == null && right == null) return 0;
  if (left == null) return 1;
  if (right == null) return -1;
  if (typeof left === "number" && typeof right === "number") return left - right;
  if (typeof left === "boolean" && typeof right === "boolean") return Number(left) - Number(right);

  const leftText = String(left).trim();
  const rightText = String(right).trim();
  const leftNumber = numericText(leftText);
  const rightNumber = numericText(rightText);
  if (leftNumber !== null && rightNumber !== null) return leftNumber - rightNumber;
  return leftText.localeCompare(rightText, undefined, { numeric: true, sensitivity: "base" });
}

function numericText(value: string) {
  if (!/^-?\d[\d,]*(?:\.\d+)?%?$/.test(value)) return null;
  return Number(value.replaceAll(",", "").replace("%", ""));
}
