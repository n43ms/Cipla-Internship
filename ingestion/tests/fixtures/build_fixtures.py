from pathlib import Path

from openpyxl import Workbook

ROOT = Path(__file__).resolve().parent


def write_workbook(path: Path, sheet_name: str, headers: list[str], rows: list[list[object]]) -> None:
    workbook = Workbook()
    sheet = workbook.active
    sheet.title = sheet_name
    sheet.append(headers)
    for row in rows:
        sheet.append(row)
    path.parent.mkdir(parents=True, exist_ok=True)
    workbook.save(path)


def build() -> None:
    write_workbook(
        ROOT / "xlsx" / "planner_nepal_tiny.xlsx",
        "Yearly Planner FY27 v2",
        ["Country", "Month", "Type of Event", "Name of the Event", "Total Cost (USD)"],
        [["Nepal", "Apr'26", "CME", "Diabetes CME - Apr", 1200]],
    )
    write_workbook(
        ROOT / "xlsx" / "execution_may_tiny.xlsx",
        "Nepal",
        ["Month", "Event", "Status", "Raised Requests", "Approved Doctors"],
        [["May-26", "Diabetes CME", "Executed", 1, 12]],
    )
    write_workbook(
        ROOT / "xlsx" / "consolidation_tiny.xlsx",
        "Working",
        [
            "DIVISION",
            "REQ_ID",
            "Months",
            "INTERVENTION NAME",
            "APPROVE/CONFIRMED TOTAL INTERVENTION",
            "TOTAL ACTUAL EXPENSES FOR INTERVENTION",
        ],
        [["Sri Lanka", "REQ-1", "May-26", "Diabetes CME", 31000, 15500]],
    )
    write_workbook(
        ROOT / "xlsx" / "rcpa_tiny.xlsx",
        "RCPA",
        ["Country", "Month(formated)", "Pcode", "Doctor", "Brand", "O & C", "Qty", "Value"],
        [["Sri Lanka", 45772, "00123", "Dr Example", "Cipla Brand", "Own", 10, 3100]],
    )


if __name__ == "__main__":
    build()
