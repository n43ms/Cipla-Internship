from pathlib import Path

from openpyxl import Workbook

ROOT = Path(__file__).resolve().parent


def write_workbook(
    path: Path, sheet_name: str, headers: list[str], rows: list[list[object]]
) -> None:
    if path.exists():
        return
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
        [
            "Month",
            "Event",
            "Status",
            "Raised Requests",
            "YP Total Doctors",
            "Approved Total Doctors",
        ],
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
        [
            [
                "Sri Lanka",
                45772,
                "00123",
                "Dr Example",
                "Cardiology",
                "A",
                "Colombo 1",
                "Active",
                "Cipla Brand",
                "SKU A",
                "Own",
                10,
                3100,
            ]
        ],
    )
    build_schema_drift()
    build_sponsorship_readiness()
    build_rcpa_readiness()


def build_schema_drift() -> None:
    write_workbook(
        ROOT / "xlsx" / "schema_drift_raw.xlsx",
        "Working",
        [
            "DIVISION",
            "Months",
            "INTERVENTION NAME",
            "REQ_ID",
            "Raw Only Field",
            "Unused Empty Field",
            "Doctor Sponsorship Remark",
        ],
        [
            [
                "Sri Lanka",
                "May-26",
                "International congress",
                "REQ-RAW-1",
                "raw value",
                None,
                "Business example only",
            ],
            [
                "Sri Lanka",
                "May-26",
                "National conference",
                "REQ-RAW-2",
                "raw value 2",
                None,
                "Second sample",
            ],
        ],
    )


def build_sponsorship_readiness() -> None:
    write_workbook(
        ROOT / "xlsx" / "consolidated_intervention_observed.xlsx",
        "Working",
        [
            "DIVISION",
            "FS HQ",
            "REQ_ID",
            "Months",
            "Intervention Start Date",
            "Intervention End Date",
            "INTERVENTION DATE",
            "ACTUAL DATE OF INTERVENTION",
            "Venue",
            "INTERVENTION NAME",
            "INTERVENTION TYPE",
            "INTERVENTION SUB TYPE",
            "TOTAL BTC",
            "EXPECTED BTU",
            "APPROVE/CONFIRMED TOTAL INTERVENTION",
            "TOTAL ACTUAL EXPENSES FOR INTERVENTION",
            "ACTUAL EXPENSE AGAINST BTU",
            "TOTAL ACTUAL BTC EXPENSE",
            "Association Contract ID",
            "Association Amount",
            "Expected PCODE",
            "Actual PCODE",
        ],
        [
            [
                "Sri Lanka",
                "Colombo HQ",
                "REQ-SP-1",
                "Jul-26",
                "2026-07-08",
                "2026-07-09",
                "2026-07-08",
                "2026-07-09",
                "Colombo",
                "International Congress",
                "International Conference",
                "ERS",
                1200,
                800,
                2000,
                2200,
                1000,
                1200,
                "C-001",
                1500,
                "P001",
                "P001",
            ],
            [
                "Nepal",
                "Kathmandu HQ",
                "REQ-SP-2",
                "Jul-26",
                "2026-07-11",
                "2026-07-11",
                "2026-07-11",
                "2026-07-11",
                "Kathmandu",
                "National CME",
                "National Conference",
                "Speaker",
                0,
                500,
                500,
                500,
                500,
                0,
                "C-002",
                500,
                "P002",
                None,
            ],
        ],
    )
    write_doctor_wise_html_xls(ROOT / "xls" / "doctor_wise_intervention_observed.xls")


def write_doctor_wise_html_xls(path: Path) -> None:
    if path.exists():
        return
    path.parent.mkdir(parents=True, exist_ok=True)
    headers = [
        "Division name",
        "Region",
        "TERRITORY_CODE",
        "FS HQ",
        "Request Date",
        "Expected Intervention date",
        "Intervention No.",
        "Type of intervention",
        "INTERVENTION SUBTYPE",
        "Intervention Name",
        "DR code",
        "Doctor Segment",
        "Doctor Name",
        "Estimated Intervention Amount",
        "BTU Expense",
        "Expense Against Advance",
        "BTC Expense",
        "Total Actual intervention Exp Amt",
        "FMV Speciality",
        "FMV Tier",
        "FMV Role",
        "FMV amount",
        "Contract ID",
        "Contracted Amount",
        "Status",
    ]
    rows = [
        [
            "Sri Lanka",
            "West",
            "T-001",
            "Colombo HQ",
            "2026-07-01",
            "2026-07-08",
            "REQ-SP-1",
            "International Conference",
            "ERS",
            "International Congress",
            "P001",
            "A",
            "Dr Alpha",
            2500,
            800,
            200,
            1000,
            2000,
            "Pulmonology",
            "Tier 1",
            "Delegate",
            3000,
            "C-001",
            2400,
            "Approved",
        ],
        [
            "Nepal",
            "Central",
            "T-002",
            "Kathmandu HQ",
            "2026-07-03",
            "2026-07-11",
            "REQ-SP-2",
            "No Fee Agreement",
            "Service",
            "National CME",
            "P002",
            "B",
            "Dr Beta",
            500,
            500,
            0,
            0,
            500,
            "Chest",
            "Tier 2",
            "Speaker",
            1000,
            "C-002",
            None,
            "Closed",
        ],
    ]
    header_cells = "".join(f"<th>{header}</th>" for header in headers)
    body_rows = []
    for row in rows:
        body_rows.append("".join(f"<td>{'' if value is None else value}</td>" for value in row))
    path.write_text(
        "<html><body><table>"
        "<tr><td>CRM Export</td></tr>"
        "<tr><td>Doctor Wise Intervention Report</td></tr>"
        "<tr><td></td></tr>"
        f"<tr>{header_cells}</tr>"
        + "".join(f"<tr>{cells}</tr>" for cells in body_rows)
        + "</table></body></html>",
        encoding="utf-8",
    )
    write_workbook(
        ROOT / "xlsx" / "schema_drift_cleaned.xlsx",
        "Working",
        [
            "Division",
            "Month",
            "Intervention Name",
            "Request ID",
            "Cleaned Only Field",
            "Doctor Sponsorship Notes",
        ],
        [
            [
                "Sri Lanka",
                "May-26",
                "International congress",
                "REQ-RAW-1",
                "cleaned value",
                "Business example only",
            ]
        ],
    )


def build_rcpa_readiness() -> None:
    headers = [
        "BU",
        "Location",
        "Month",
        "Doctor Name",
        "Pcode",
        "Customer Type",
        "Speciality",
        "Class",
        "PATCHNAME",
        "Brand",
        "SKU Detail",
        "O & C",
        "Qty",
        "Value",
        "Pcode Mapping Method",
    ]
    rows = [
        [
            "Sri Lanka",
            "Colombo",
            "Oct-25",
            "Dr Legacy",
            "SL001",
            "Active",
            "Chest",
            "A",
            "Patch A",
            "Cipla Brand",
            "SKU A",
            "Own",
            12,
            1200,
            "",
        ],
        [
            "Sri Lanka",
            "Colombo",
            "Nov-25",
            "Dr System",
            "SL002",
            "Active",
            "Chest",
            "B",
            "Patch B",
            "Competitor Brand",
            "SKU B",
            "Competitor",
            4,
            400,
            "",
        ],
        [
            "Nepal",
            "Kathmandu",
            "Dec-25",
            "Dr Source",
            "NP001",
            "Active",
            "Pulmonology",
            "A",
            "Patch C",
            "Cipla Brand",
            "SKU C",
            "Own",
            9,
            900,
            "source",
        ],
    ]
    write_workbook(ROOT / "xlsx" / "historical_rcpa_observed.xlsx", "RCPA", headers, rows)
    write_workbook(
        ROOT / "xlsx" / "monthly_rcpa_observed.xlsx",
        "Sri Lanka",
        headers,
        [
            rows[1],
            [
                "Sri Lanka",
                "Kandy",
                "Jul-26",
                "Dr Fresh",
                "SL003",
                "Active",
                "Chest",
                "A",
                "Patch D",
                "Cipla Brand",
                "SKU D",
                "Own",
                16,
                1600,
                "",
            ],
        ],
    )
    write_workbook(
        ROOT / "xlsx" / "msl_doctor_master_observed.xlsx",
        "MSL",
        [
            "BU",
            "Pcode",
            "Doctor Name",
            "Location",
            "Territory Id",
            "Patch",
            "Patchsname",
            "Legacy Code",
        ],
        [
            [
                "Sri Lanka",
                "SL001",
                "Dr Legacy",
                "Colombo",
                "T-001",
                "Patch A",
                "Patch A",
                "LEG-1",
            ],
        ],
    )


if __name__ == "__main__":
    build()
