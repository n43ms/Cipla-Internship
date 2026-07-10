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
        "planned_total_hcps": (
            "# Total Planned Docs",
            "# Total Planned Docs (A+X)",
            "Total Planned Docs",
            "Planned HCPs",
        ),
        "planned_honorarium_hcps": (
            "# No. of Doctors as Speakers/ Sponsorship (Honorarium HCPs) (A)",
            "No. of Doctors as Speakers/ Sponsorship (Honorarium HCPs) (A)",
            "Honorarium HCPs",
            "Honorarium Docs",
            "# Honorarium HCPs",
        ),
        "planned_delegate_hcps": (
            "# No. of Doctors as Delegates/ Attendees (No Honorarium) (X)",
            "No. of Doctors as Delegates/ Attendees (No Honorarium) (X)",
            "Delegate HCPs",
            "Delegate Docs",
            "# Delegate HCPs",
        ),
        "planned_patients": (
            "# Total No. of Patient's (If any)",
            "Total No. of Patient's (If any)",
            "Planned Patients",
            "# Patients",
        ),
        "planned_pharmacies": (
            "# Total Planned Pharmacy",
            "Total Planned Pharmacy",
            "Planned Pharmacies",
        ),
        "honorarium_cost_per_hcp_usd": (
            "Honorarium/ Sponsorship Cost per Doctor (USD) (B)",
            "Honorarium Cost per Doctor (USD) (B)",
            "Honorarium Cost/HCP USD",
            "Honorarium Cost per HCP USD",
        ),
        "total_honorarium_cost_usd": (
            "Total Honorarium Cost (USD) (A*B)",
            "Total Honorarium Cost USD",
            "Total Honorarium Cost",
        ),
        "operational_cost_per_unit_usd": (
            "Operational Cost Per Dr/Pharmacy (USD) (Y)",
            "Operational Cost/Unit USD",
            "Operational Cost per Unit USD",
        ),
        "total_operational_cost_usd": (
            "Total Operational Cost (USD) (A+X) * (Y)",
            "Total Operational Cost USD",
            "Total Operational Cost",
        ),
        "total_planned_cost_usd": (
            "Total Cost (USD)",
            "Total cost proposed",
            "Total Planned Cost USD",
        ),
        "comments": ("Comments", "Comment"),
        "country_comment": ("Country Comment", "Country Comments"),
        "ho_finalized": ("HO Finalized", "HO Finalised", "Finalized by HO", "Finalised by HO"),
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
        "planned_hcps": ("Planned Doctors", "Planned HCPs", "YP Total Doctors", "YP Total Drs"),
        "engaged_hcps": (
            "Approved Doctors",
            "Engaged HCPs",
            "HCP's Engaged count",
            "Approved Total Doctors",
            "Approved Total Drs",
        ),
        "raised_request_count": (
            "Raised Requests",
            "Raised Request",
            "Raised Request Count",
            "Raised Total Requests",
        ),
        "yp_total_doctors": ("YP Total Doctors", "YP Total Drs", "YP Doctors"),
        "raised_total_doctors": ("Raised Total Doctors", "Raised Total Drs", "Raised Doctors"),
        "approved_total_doctors": (
            "Approved Total Doctors",
            "Approved Total Drs",
            "Approved Doctors",
        ),
        "request_total_doctors": (
            "Request Total Doctors",
            "Request Total Drs",
            "Requested Doctors",
        ),
        "event_created_count": ("Event Created Count", "Events Created"),
        "status": ("Status", "Intervention Status", "Execution Status", "Count"),
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
        "rep_name": ("REP NAME", "Rep Name", "REQUESTED FS", "ME NAME"),
        "intervention_date": ("INTERVENTION DATE", "Intervention Date"),
        "actual_intervention_date": ("ACTUAL INTERVENTION DATE", "Actual Intervention Date"),
        "venue": ("Venue", "VENUE"),
        "intervention_name": ("INTERVENTION NAME", "Intervention Name"),
        "intervention_type": ("INTERVENTION TYPE", "Intervention Type"),
        "intervention_sub_type": ("INTERVENTION SUB TYPE", "Intervention Sub Type", "Subtype"),
        "topic_remarks": ("TOPIC/ REMARKS", "Topic Remarks", "Topic/Remarks", "Remarks"),
        "estimated_intervention": ("ESTIMATED INTERVENTION",),
        "confirmed_contracted_amount": ("APPROVE/CONFIRMED TOTAL INTERVENTION",),
        "actual_total_expense": ("TOTAL ACTUAL EXPENSES FOR INTERVENTION",),
        "actual_btu_expense": ("ACTUAL EXPENSE AGAINST BTU",),
        "actual_btc_expense": ("TOTAL ACTUAL BTC EXPENSE",),
        "association_amount": ("Association Amount",),
        "association_contract_id": (
            "Association Contract ID",
            "Association Agreement ID",
            "Contract ID",
        ),
        "association_deliverables": ("Association Deliverables", "Deliverables"),
        "expected_customer_count": (
            "NUMBER OF CUSTOMER EXPECTED TO ATTEND",
            "Expected Customer Count",
            "Expected Customers",
            "No. of Expected Customers",
        ),
        "attended_customer_count": (
            "DOCTORS ATTENDED INTERVENTION",
            "Attended Customer Count",
            "Attended Customers",
            "No. of Attended Customers",
        ),
        "expected_category_raw": (
            "DR.CATEGORY EXPECTED TO ATTEND",
            "Expected Category",
            "Expected Customer Category",
        ),
        "attended_category_raw": (
            "DR.CATEGORY ATTENDED THE INTERVENTION",
            "Attended Category",
            "Attended Customer Category",
        ),
        "expected_pcodes": ("Expected PCODE", "Expected Pcode"),
        "actual_pcodes": ("Actual PCODE", "Actual Pcode"),
        "expected_doctors": ("Dr. NAME EXPECTED", "Dr NAME EXPECTED", "Expected Doctors"),
        "actual_doctors": (
            "Dr.NAME ATTENDED",
            "Dr NAME ATTENDED",
            "Actual Doctors",
            "Attended Doctors",
        ),
        "request_approval_status": (
            "PENDING FOR APPROVAL Request",
            "Request Approval Status",
            "APPROVAL STATUS",
        ),
        "request_confirmation_status": (
            "PENDING FOR CONFIRMATION Request",
            "Request Confirmation Status",
            "Confirmation Status",
        ),
        "post_approval_status": (
            "PENDING FOR APPROVAL POST",
            "Post Approval Status",
            "Post Event Approval Status",
        ),
        "post_confirmation_status": (
            "PENDING FOR CONFIRMATION POST",
            "Post Confirmation Status",
            "Post Event Confirmation Status",
        ),
        "expense_submitted_date": ("Expense Submitted Date", "Expense Submission Date"),
        "expense_confirmed_date": ("Expense Confirmed Date", "Expense Confirmation Date"),
        "approval_status": ("Approval Status Final", "Final Approval Status"),
        "confirmation_status": ("Confirmation Status Final", "Final Confirmation Status"),
        "cancellation_reason": ("Cancellation Reason", "Cancel Reason"),
        "city": ("City", "CITY"),
        "state": ("State", "STATE"),
        "current_owner_stage": ("Current Owner", "Current Stage", "Pending With"),
        "level_1_approval": ("Level 1 Approval", "Approval Level 1", "L1 Approval"),
        "level_2_approval": ("Level 2 Approval", "Approval Level 2", "L2 Approval"),
        "level_3_approval": ("Level 3 Approval", "Approval Level 3", "L3 Approval"),
        "level_4_approval": ("Level 4 Approval", "Approval Level 4", "L4 Approval"),
        "level_5_approval": ("Level 5 Approval", "Approval Level 5", "L5 Approval"),
        "level_6_approval": ("Level 6 Approval", "Approval Level 6", "L6 Approval"),
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
        "active_status": (
            "Active Status",
            "Status Doctor (Mar'25)",
            "Status Doctor (Mar'26)",
            "Status Doctor",
        ),
        "brand_group": ("Brand", "Brand Group", "Brand Name"),
        "sku": ("SKU", "Sku", "Product", "Product Name"),
        "sku_detail": ("SKU Detail", "Sku Detail", "Product Detail"),
        "own_or_competitor": ("O & C", "Own/Competitor", "Own Competitor"),
        "quantity": ("RCPA Quantity", "Qty", "Quantity"),
        "value": ("RCPA Value", "Value", "Amount"),
        "speciality": ("Speciality", "Specialty"),
        "doctor_class": ("Class", "Doctor Class", "Category"),
        "patch_name": ("Patch", "Patch Name", "Territory"),
    },
)

DOCTOR_CONTRACT_SCHEMA = SourceSchema(
    source_type="doctor_contract",
    required={"country", "intervention_id", "doctor_code", "doctor_name"},
    aliases={
        "country": ("Division name", "Division", "BU", "Country"),
        "region": ("Region",),
        "territory_code": ("TERRITORY_CODE", "Territory Code"),
        "fs_hq": ("FS HQ", "FQ HQ"),
        "intervention_id": ("Intervention No.", "Intervention No", "Intervention ID"),
        "intervention_type": ("Type of intervention", "Intervention Type"),
        "intervention_subtype": ("INTERVENTION SUBTYPE", "Intervention Subtype", "Subtype"),
        "doctor_code": ("DR code", "DR Code", "Pcode", "P Code"),
        "doctor_segment": ("Doctor Segment",),
        "doctor_name": ("Doctor Name", "Dr Name"),
        "fmv_amount": ("FMV amount", "FMV Amount"),
        "contract_id": ("Contract ID",),
        "contracted_amount": ("Contracted Amount",),
        "status": ("Status",),
    },
)

CLEANED_PRESENTABLE_SCHEMA = SourceSchema(
    source_type="cleaned_presentable",
    required=set(),
    aliases={
        "country": ("Division", "BU", "Country"),
        "req_id": ("Request ID", "Req ID"),
        "intervention_id": ("Intervention ID", "Intervention No.", "Intervention No"),
        "intervention_name": ("Intervention Name", "Event Name"),
        "doctor_code": ("Pcode", "P Code", "DR code", "DR Code"),
        "doctor_name": ("Doctor Name", "Dr Name"),
        "contracted_amount": ("CON_AMOUNT", "Contracted Amount"),
        "fmv_role": ("FMVROLE", "FMV Role"),
        "intervention_type": ("TYPE", "Type"),
        "intervention_subtype": ("SUBTYPE", "Subtype"),
    },
)

SCHEMAS = {
    "planner": PLANNER_SCHEMA,
    "execution_snapshot": EXECUTION_SCHEMA,
    "consolidation": CONSOLIDATION_SCHEMA,
    "rcpa": RCPA_SCHEMA,
    "doctor_contract": DOCTOR_CONTRACT_SCHEMA,
    "cleaned_presentable": CLEANED_PRESENTABLE_SCHEMA,
}
