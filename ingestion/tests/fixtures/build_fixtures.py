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
        [
            "Country",
            "Month",
            "Type of Event",
            "Name of the Event",
            "# Honorarium HCPs",
            "Delegate HCPs",
            "Total Cost (USD)",
            "Comments",
            "HO Finalized",
        ],
        [["Nepal", "Apr'26", "CME", "Diabetes CME - Apr", 10, 2, 1200, "priority", "yes"]],
    )
    write_workbook(
        ROOT / "xlsx" / "execution_may_tiny.xlsx",
        "Nepal",
        ["Month", "Event", "Status", "Raised Requests", "YP Total Doctors", "Approved Total Doctors"],
        [["May-26", "Diabetes CME", "Executed", 1, 15, 12]],
    )
    write_workbook(
        ROOT / "xlsx" / "consolidation_tiny.xlsx",
        "Working",
        [
            "DIVISION",
            "REQ_ID",
            "Months",
            "INTERVENTION NAME",
            "INTERVENTION DATE",
            "ACTUAL INTERVENTION DATE",
            "TOPIC/ REMARKS",
            "APPROVE/CONFIRMED TOTAL INTERVENTION",
            "ESTIMATED INTERVENTION",
            "TOTAL ACTUAL EXPENSES FOR INTERVENTION",
            "ACTUAL EXPENSE AGAINST BTU",
            "TOTAL ACTUAL BTC EXPENSE",
            "PENDING FOR APPROVAL Request",
            "PENDING FOR CONFIRMATION POST",
            "City",
            "STATE",
        ],
        [
            [
                "Sri Lanka",
                "REQ-1",
                "May-26",
                "Diabetes CME",
                "2026-05-10",
                "2026-05-11",
                "topic",
                31000,
                62000,
                15500,
                9300,
                6200,
                "Request Submitted Pending With Manager",
                "Report Approved",
                "Colombo",
                "Western",
            ]
        ],
    )
    write_workbook(
        ROOT / "xlsx" / "rcpa_tiny.xlsx",
        "RCPA",
        [
            "Country",
            "Month(formated)",
            "Pcode",
            "Doctor",
            "Speciality",
            "Class",
            "Patch",
            "Active Status",
            "Brand",
            "SKU Detail",
            "O & C",
            "Qty",
            "Value",
        ],
        [["Sri Lanka", 45772, "00123", "Dr Example", "Cardiology", "A", "Colombo 1", "Active", "Cipla Brand", "SKU A", "Own", 10, 3100]],
    )


if __name__ == "__main__":
    build()
