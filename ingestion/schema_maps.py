from __future__ import annotations

from dataclasses import dataclass


def normalize_header(value: object) -> str:
    text = "" if value is None else str(value)
    return " ".join(
        text.replace("\n", " ")
        .replace("\r", " ")
        .replace("_", " ")
        .replace("-", " ")
        .strip()
        .lower()
        .split()
    )


@dataclass(frozen=True)
class SourceSchema:
    source_type: str
    required: set[str]
    aliases: dict[str, tuple[str, ...]]
    canonical_sheet_names: tuple[str, ...] = ()

    def alias_lookup(self) -> dict[str, str]:
        lookup: dict[str, str] = {}
        for canonical, aliases in self.aliases.items():
            lookup[normalize_header(canonical)] = canonical
            for alias in aliases:
                lookup[normalize_header(alias)] = canonical
        return lookup


PLANNER_SCHEMA = SourceSchema(
    source_type="planner",
    canonical_sheet_names=("Yearly Planner FY27 v2", "YP FY27"),
    required={"country", "month", "event_name"},
    aliases={
        "country": ("Country", "BU", "Division"),
        "therapy": ("Therapy", "TA", "Therapy Area"),
        "month": ("Month", "Months"),
        "event_type": ("Type of Event", "Event Type", "Intervention Type"),
        "event_name": ("Name of the Event", "Event", "Intervention Name", "Activity Name"),
        "central_or_local": ("Central/Local", "Central Local"),
        "brand_name_1": ("Brand Name 1", "Brand 1", "Brand"),
        "brand_name_2": ("Brand Name 2", "Brand 2"),
        "planned_total_hcps": ("# Total Planned Docs", "Total Planned Docs", "Planned HCPs"),
        "planned_patients": ("Planned Patients", "# Patients"),
        "planned_pharmacies": ("# Total Planned Pharmacy", "Total Planned Pharmacy", "Planned Pharmacies"),
        "total_planned_cost_usd": ("Total Cost (USD)", "Total cost proposed", "Total Planned Cost USD"),
    },
)

EXECUTION_SCHEMA = SourceSchema(
    source_type="execution_snapshot",
    canonical_sheet_names=("YP", "Nepal", "Myanmar", "Sri Lanka"),
    required={"event_name"},
    aliases={
        "country": ("Country", "BU", "Division"),
        "therapy": ("Therapy", "TA"),
        "month": ("Month", "Months"),
        "event_type": ("Type of Event", "Event Type", "Intervention Type"),
        "event_name": ("Event", "Name", "Name of the Event", "Intervention Name", "Activity Name"),
        "planned_hcps": ("Planned Doctors", "Planned HCPs", "YP Total Doctors"),
        "engaged_hcps": ("Approved Doctors", "Engaged HCPs", "HCP's Engaged count", "Approved Total Doctors"),
        "raised_request_count": ("Raised Requests", "Raised Request", "Raised Request Count", "Raised Total Requests"),
        "status": ("Status", "Intervention Status", "Execution Status"),
    },
)

CONSOLIDATION_SCHEMA = SourceSchema(
    source_type="consolidation",
    canonical_sheet_names=("Working",),
    required={"country", "month", "intervention_name"},
    aliases={
        "country": ("DIVISION", "Country", "BU"),
        "req_id": ("REQ_ID", "Request ID", "Req ID"),
        "month": ("Months", "Month"),
        "rep_code": ("REP CODE", "Rep Code"),
        "rep_name": ("REP NAME", "Rep Name"),
        "intervention_date": ("INTERVENTION DATE", "Intervention Date"),
        "actual_intervention_date": ("ACTUAL INTERVENTION DATE", "Actual Intervention Date"),
        "venue": ("Venue", "VENUE"),
        "intervention_name": ("INTERVENTION NAME", "Intervention Name"),
        "intervention_type": ("INTERVENTION TYPE", "Intervention Type"),
        "intervention_sub_type": ("INTERVENTION SUB TYPE", "Intervention Sub Type", "Subtype"),
        "estimated_intervention": ("ESTIMATED INTERVENTION",),
        "confirmed_contracted_amount": ("APPROVE/CONFIRMED TOTAL INTERVENTION",),
        "actual_total_expense": ("TOTAL ACTUAL EXPENSES FOR INTERVENTION",),
        "actual_btu_expense": ("ACTUAL EXPENSE AGAINST BTU",),
        "actual_btc_expense": ("TOTAL ACTUAL BTC EXPENSE",),
        "association_amount": ("Association Amount",),
        "expected_pcodes": ("Expected PCODE", "Expected Pcode"),
        "actual_pcodes": ("Actual PCODE", "Actual Pcode"),
        "expected_doctors": ("Dr. NAME EXPECTED", "Dr NAME EXPECTED", "Expected Doctors"),
        "actual_doctors": ("Dr.NAME ATTENDED", "Dr NAME ATTENDED", "Actual Doctors", "Attended Doctors"),
        "request_approval_status": ("Request Approval Status", "APPROVAL STATUS"),
        "request_confirmation_status": ("Request Confirmation Status", "Confirmation Status"),
        "post_approval_status": ("Post Approval Status", "Post Event Approval Status"),
        "post_confirmation_status": ("Post Confirmation Status", "Post Event Confirmation Status"),
        "current_owner_stage": ("Current Owner", "Current Stage", "Pending With"),
    },
)

RCPA_SCHEMA = SourceSchema(
    source_type="rcpa",
    canonical_sheet_names=("RCPA", "Data", "Sheet1"),
    required={"country", "month", "pcode", "brand_group", "quantity"},
    aliases={
        "country": ("BU", "Country", "Division"),
        "month": ("Month", "Month(formated)", "Month formatted", "Months"),
        "doctor_name": ("Doctor Name", "Doctor", "Dr Name"),
        "pcode": ("Pcode", "P Code", "PCODE"),
        "active_status": ("Active Status", "Status Doctor (Mar'25)", "Status Doctor (Mar'26)", "Status Doctor"),
        "brand_group": ("Brand", "Brand Group", "Brand Name"),
        "sku": ("SKU", "Sku", "Product", "Product Name"),
        "own_or_competitor": ("O & C", "Own/Competitor", "Own Competitor"),
        "quantity": ("RCPA Quantity", "Qty", "Quantity"),
        "value": ("RCPA Value", "Value", "Amount"),
        "speciality": ("Speciality", "Specialty"),
        "doctor_class": ("Class", "Doctor Class", "Category"),
        "patch_name": ("Patch", "Patch Name", "Territory"),
    },
)

SCHEMAS = {
    "planner": PLANNER_SCHEMA,
    "execution_snapshot": EXECUTION_SCHEMA,
    "consolidation": CONSOLIDATION_SCHEMA,
    "rcpa": RCPA_SCHEMA,
}
