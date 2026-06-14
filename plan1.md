**CIPLA EMEU EXECUTION INTELLIGENCE DASHBOARD**
**Technical Architecture, Product Context, and Implementation Guide**
**Prepared by: Staff Engineer Review**

---

**PART ONE — HIGH LEVEL ARCHITECTURE OVERVIEW**

---

**What this system is**

This is a data intelligence platform for Cipla's EMEU/PBP (Emerging Markets Europe / Pharma Business Partners) division. It ingests marketing execution data from multiple disconnected Excel and binary sources, stores it in a relational database, exposes it through a typed REST API, visualizes it in a modern dashboard, and layers a natural language query interface on top. The system answers three questions that currently require manual spreadsheet work to answer: how well is our marketing plan being executed this month, where is our budget being left on the table, and are we spending money on the doctors who actually prescribe our drugs.

---

**System layers and what each one owns**

The system has five layers with clean separation between them.

The ingestion layer is a standalone Python CLI application. It owns all file reading, parsing, validation, cleaning, transformation, deduplication, and database writes. It runs independently of the web application. It is the only layer that touches the raw Excel and xlsb files. It produces a validation report on every run so you know what loaded cleanly, what failed, and what was skipped. It uses upsert semantics everywhere so it can be re-run safely when Abhijeet sends updated data.

The database layer is a PostgreSQL database hosted on Supabase. It owns all persistent state. It has seven tables with proper foreign keys, unique constraints, and indexes. It is the single source of truth for all downstream layers. No layer other than the ingestion script writes to it. The API only reads.

The backend layer is a FastAPI application written in Python. It owns all business logic, data aggregation, computation of KPIs, filtering, sorting, and AI orchestration. It exposes a typed REST API with clear contracts, validation, error handling, and pagination. It reads from Supabase. It calls the Claude API for the AI query feature. It never writes to the database. It is stateless and can be restarted at any time without side effects.

The frontend layer is a React application written in TypeScript. It owns all UI concerns, state management, routing, chart rendering, and user interaction. It calls the FastAPI backend exclusively — it never touches Supabase or the Claude API directly. It has proper loading states, error states, and empty states throughout. It is built to look credible and polished enough to demo to Abhijeet, Pralhad, and leadership.

The AI layer lives inside the FastAPI backend as a dedicated service module. It owns the Claude API integration, context construction from live database queries, prompt engineering, and response formatting. It does not hallucinate data — every piece of context it gives Claude is queried from the database at request time. It is used only for reasoning, summarization, and natural language response — all calculations and filtering are done by the database and backend before being handed to Claude.

---

**Data flow end to end**

Abhijeet sends Excel and xlsb files. You drop them into a local data directory. You run the Python ingestion CLI which reads every file, validates columns, cleans data, checks join coverage, aggregates RCPA rows, and upserts into Supabase. The ingestion script prints a summary showing how many rows were inserted, how many were updated, how many failed, and what percentage of doctors in the interventions table have matching RCPA records. Once ingestion is confirmed clean, the FastAPI backend automatically reflects the new data on the next API call because it queries the database live. The React frontend queries the backend on page load and on filter changes. The AI chat panel sends user questions to the backend which queries the database for a fresh KPI snapshot, constructs a grounded context block, and calls Claude.

---

**PART TWO — DETAILED TRANSCRIPT SUMMARY**

---

**Context and participants**

The meeting was recorded on June 11, 2026. Abhijeet Mudila is a senior manager in Cipla's EMEU/PBP division. Aditya Emmanual is a sophomore intern. The call was approximately 30 minutes and covered a screen-sharing walkthrough of Cipla's current reporting system and the vision for what should be built.

---

**The business problem Abhijeet described**

Cipla's marketing team plans events every month across six markets — Sri Lanka, Nepal, Myanmar, Oman, UAE, and Malaysia. These events involve hiring doctors as speakers, paying them honorariums, and inviting other doctors as attendees. The purpose is to generate awareness and advocacy for Cipla's drug portfolio. Every planned event has a sanctioned budget that head office approves upfront.

The problem is that nobody has visibility into whether these events are actually happening. The plan lives in Excel. The execution data lives in a smart contract system that exports raw reports. The prescription data for the same doctors lives in a separate audit system. Nobody connects these three datasets, so the team is functionally blind to three things: which events failed to happen and how much budget was left unspent, which markets are tracking well or poorly against their monthly goals, and whether the doctors receiving Cipla's money are actually the ones prescribing Cipla's drugs.

Abhijeet described a dual impact when an event is not executed. First, the company misses a marketing opportunity. Second, the sanctioned budget goes unspent, which means head office approved money that the team failed to use — and that reflects badly in governance reviews.

---

**The five components Abhijeet walked through**

The first component is the yearly planner. This is what Abhijeet called the Bible. It is an Excel file per country that contains every planned event for the fiscal year broken down by country, therapy area, month, event type, event name, whether it is centrally or locally driven, which brands are involved, how many doctors will be paid as speakers with honorariums, the honorarium rate per doctor, how many will attend as delegates at no cost, operational costs like travel and refreshments, and the total sanctioned budget in USD. He showed Nepal and Sri Lanka planners live on the call.

The second component is the smart contract execution data. Every event that gets raised in Cipla's internal system (the smart contract) generates a request with a unique REQ_ID, a planned budget, an approval chain through up to six levels of management, and eventually an actual expense and a list of doctors who attended. This data is exported as a consolidation report. The gap between the yearly planner and the consolidation report is where unexecuted events live.

The third component is the execution matrix. Abhijeet showed a monthly Excel file (the Execution YP Planner) that joins the yearly plan against the smart contract data to show per event: planned HCPs, engaged HCPs, raised request count, and intervention status as either Executed or Action Due. This is where the 7% execution figure came from — 108 doctors engaged out of 1,500 planned.

The fourth component is the RCPA ROI data. RCPA stands for Retail Chemist Prescription Audit. It is prescription data showing for each doctor, each brand, and each month how many prescriptions they wrote for Cipla drugs and how much monetary value those prescriptions represent. Abhijeet's insight was that if you join this to the smart contract data using the doctor's unique Pcode identifier, you can see whether the doctors receiving Cipla's money are actually prescribing. His example: a doctor receiving 300,000 rupees in sponsorships but writing only 30 prescriptions is a poor investment, while a doctor writing 3,500 prescriptions every month and receiving nothing is a missed opportunity.

The fifth component is the AI plugin. Abhijeet described wanting a simple query interface where field teams or managers can type a plain English question and get a direct, digestible answer — for example which doctors are the top performers, which market is the top executor, what are three key highlights from this week. He explicitly said the AI should produce very simple, digestible outputs.

---

**Scope and tool decisions made in the call**

Abhijeet confirmed the scope for the MVP is Sri Lanka and Nepal, with data from November 2025 onwards to give statistical significance for trend analysis. He said to use any tool — not necessarily Power BI — because forcing Power BI would turn the project into a learning exercise rather than a delivery. Once the proof of concept is validated by him and Pralhad, Anil will port the visualization logic to Power BI on their side. He told Aditya to think of it as a dashboard project, not a software engineering project, and to focus on making the visualizations clear and decision-relevant rather than overbuilding infrastructure.

---

**PART THREE — STEP BY STEP DETAILED ARCHITECTURE AND IMPLEMENTATION**

---

**PRELIMINARY: PROJECT STRUCTURE**

Before writing a single line of code, establish a clean folder structure and stick to it. This is the directory layout for the entire project.

```
cipla-dashboard/
├── ingestion/
│   ├── __init__.py
│   ├── main.py                  (CLI entry point)
│   ├── config.py                (paths, env vars)
│   ├── validators.py            (schema checks, column presence)
│   ├── cleaners.py              (date parsing, string normalization)
│   ├── loaders/
│   │   ├── __init__.py
│   │   ├── yearly_planner.py
│   │   ├── execution_monthly.py
│   │   ├── consolidation.py
│   │   └── rcpa.py
│   ├── models.py                (Pydantic models for validated rows)
│   └── report.py                (ingestion summary reporter)
│
├── backend/
│   ├── main.py                  (FastAPI app entry point)
│   ├── config.py                (settings via pydantic-settings)
│   ├── database.py              (Supabase client singleton)
│   ├── routers/
│   │   ├── __init__.py
│   │   ├── execution.py
│   │   ├── budget.py
│   │   ├── doctors.py
│   │   └── ai_query.py
│   ├── services/
│   │   ├── __init__.py
│   │   ├── execution_service.py
│   │   ├── budget_service.py
│   │   ├── doctor_service.py
│   │   └── ai_service.py
│   ├── schemas/
│   │   ├── __init__.py
│   │   ├── execution.py
│   │   ├── budget.py
│   │   ├── doctors.py
│   │   └── ai_query.py
│   └── utils/
│       ├── __init__.py
│       └── date_utils.py
│
├── frontend/
│   ├── src/
│   │   ├── api/                 (typed API client functions)
│   │   ├── components/
│   │   │   ├── ui/              (reusable primitives: Card, Badge, Table)
│   │   │   ├── charts/          (ExecutionBarChart, BudgetLineChart, ROIScatter)
│   │   │   └── panels/          (AIPanel, DrillDownPanel)
│   │   ├── pages/
│   │   │   ├── ExecutionMatrix.tsx
│   │   │   ├── BudgetUtilization.tsx
│   │   │   ├── DoctorROI.tsx
│   │   │   └── EventTracker.tsx
│   │   ├── hooks/               (useExecution, useDoctors, useAI)
│   │   ├── types/               (TypeScript interfaces matching API responses)
│   │   ├── store/               (global state: selected country, month)
│   │   ├── App.tsx
│   │   └── main.tsx
│   ├── package.json
│   └── vite.config.ts
│
├── .env                         (never commit this)
├── .env.example                 (commit this with placeholder values)
├── requirements.txt
└── README.md
```

This structure has clear separation of concerns. The ingestion code never imports from the backend. The backend never imports from the ingestion layer. The frontend only communicates with the backend through the typed API client in src/api/.

---

**STEP 1 — ENVIRONMENT AND DEPENDENCIES**

Create a .env file at the project root with the following variables. Never commit this file.

```
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_SERVICE_KEY=your-service-role-key
SUPABASE_ANON_KEY=your-anon-key
ANTHROPIC_API_KEY=your-claude-api-key
DATA_DIR=./data/raw
```

Use the service role key in the ingestion script because it bypasses Row Level Security and needs write access. Use the anon key in the FastAPI backend because it is read-only and respects RLS. Never expose the service role key to the frontend.

Python dependencies (requirements.txt):

```
fastapi==0.111.0
uvicorn[standard]==0.30.0
supabase==2.5.0
pydantic==2.7.0
pydantic-settings==2.3.0
pandas==2.2.0
openpyxl==3.1.2
pyxlsb==1.0.10
anthropic==0.28.0
python-dotenv==1.0.1
httpx==0.27.0
```

Frontend dependencies (run in the frontend directory):

```
npm create vite@latest . -- --template react-ts
npm install recharts axios @tanstack/react-query zustand tailwindcss @headlessui/react lucide-react
npm install -D @types/react @types/recharts
```

Use React Query for all server state — it handles caching, loading states, refetching, and error states automatically and cleanly. Use Zustand for global client state — the selected country and month that drive all four tabs. Do not use Redux for this project; it is overengineered for this scope.

---

**STEP 2 — DATABASE SCHEMA**

Log into your Supabase project and open the SQL editor. Run the following schema. Order matters because of foreign key dependencies.

```sql
-- Table 1: countries
CREATE TABLE countries (
  id SERIAL PRIMARY KEY,
  name TEXT NOT NULL UNIQUE,
  created_at TIMESTAMPTZ DEFAULT NOW()
);

INSERT INTO countries (name) VALUES
  ('Sri Lanka'), ('Nepal'), ('Myanmar'), ('Oman'), ('UAE'), ('Malaysia');

-- Table 2: doctors
CREATE TABLE doctors (
  pcode BIGINT PRIMARY KEY,
  doctor_name TEXT NOT NULL,
  speciality TEXT,
  doctor_class CHAR(1) CHECK (doctor_class IN ('A', 'B', 'C')),
  country_id INTEGER REFERENCES countries(id),
  brand_group TEXT,
  patch_name TEXT,
  active_status TEXT,
  updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_doctors_country ON doctors(country_id);
CREATE INDEX idx_doctors_class ON doctors(doctor_class);

-- Table 3: yearly_plan
CREATE TABLE yearly_plan (
  id SERIAL PRIMARY KEY,
  country_id INTEGER NOT NULL REFERENCES countries(id),
  therapy TEXT,
  plan_month TEXT NOT NULL,
  fiscal_year TEXT NOT NULL DEFAULT 'FY27',
  event_type TEXT NOT NULL,
  event_name TEXT NOT NULL,
  central_or_local TEXT,
  brand_name_1 TEXT,
  brand_name_2 TEXT,
  num_honorarium_doctors INTEGER DEFAULT 0,
  honorarium_cost_per_doctor_usd NUMERIC(10,2) DEFAULT 0,
  total_honorarium_cost_usd NUMERIC(10,2) DEFAULT 0,
  num_delegate_doctors INTEGER DEFAULT 0,
  total_planned_doctors INTEGER DEFAULT 0,
  total_planned_pharmacies INTEGER DEFAULT 0,
  operational_cost_per_doctor_usd NUMERIC(10,2) DEFAULT 0,
  total_operational_cost_usd NUMERIC(10,2) DEFAULT 0,
  total_cost_usd NUMERIC(10,2) DEFAULT 0,
  ho_finalized TEXT,
  comments TEXT,
  created_at TIMESTAMPTZ DEFAULT NOW(),
  UNIQUE(country_id, plan_month, fiscal_year, event_type, event_name)
);

CREATE INDEX idx_yp_country_month ON yearly_plan(country_id, plan_month);
CREATE INDEX idx_yp_event_type ON yearly_plan(event_type);

-- Table 4: execution_monthly
CREATE TABLE execution_monthly (
  id SERIAL PRIMARY KEY,
  country_id INTEGER NOT NULL REFERENCES countries(id),
  month_label TEXT NOT NULL,
  fiscal_year TEXT NOT NULL DEFAULT 'FY27',
  event_type TEXT NOT NULL,
  event_name TEXT NOT NULL,
  event_name_clean TEXT NOT NULL,
  planned_hcps INTEGER DEFAULT 0,
  engaged_hcps INTEGER DEFAULT 0,
  raised_request_count INTEGER DEFAULT 0,
  intervention_status TEXT CHECK (intervention_status IN ('Executed', 'Action due', 'Unknown')),
  execution_pct NUMERIC(5,2) GENERATED ALWAYS AS (
    CASE WHEN planned_hcps > 0
    THEN ROUND((engaged_hcps::NUMERIC / planned_hcps::NUMERIC) * 100, 2)
    ELSE 0 END
  ) STORED,
  yearly_plan_id INTEGER REFERENCES yearly_plan(id),
  created_at TIMESTAMPTZ DEFAULT NOW(),
  UNIQUE(country_id, month_label, fiscal_year, event_type, event_name_clean)
);

CREATE INDEX idx_em_country_month ON execution_monthly(country_id, month_label);
CREATE INDEX idx_em_status ON execution_monthly(intervention_status);

-- Table 5: interventions (Consolidation report)
CREATE TABLE interventions (
  id SERIAL PRIMARY KEY,
  req_id INTEGER NOT NULL UNIQUE,
  country_id INTEGER NOT NULL REFERENCES countries(id),
  rep_code TEXT,
  rep_name TEXT,
  intervention_date DATE,
  actual_intervention_date DATE,
  month_label TEXT,
  venue TEXT,
  intervention_name TEXT,
  intervention_type TEXT,
  intervention_sub_type TEXT,
  topic_remarks TEXT,
  estimated_budget_usd NUMERIC(10,2) DEFAULT 0,
  total_btc NUMERIC(10,2) DEFAULT 0,
  confirmed_budget_usd NUMERIC(10,2) DEFAULT 0,
  total_actual_expenses_usd NUMERIC(10,2) DEFAULT 0,
  num_doctors_expected INTEGER DEFAULT 0,
  num_doctors_attended INTEGER DEFAULT 0,
  doctor_category_expected TEXT,
  approval_status TEXT,
  confirmation_status TEXT,
  doctor_names_expected TEXT,
  doctor_names_attended TEXT,
  doctor_class_expected TEXT,
  doctor_class_attended TEXT,
  expected_pcode_raw TEXT,
  actual_pcode_raw TEXT,
  city TEXT,
  cancellation_reason TEXT,
  created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_interventions_country ON interventions(country_id);
CREATE INDEX idx_interventions_month ON interventions(month_label);
CREATE INDEX idx_interventions_type ON interventions(intervention_type);

-- Table 6: intervention_doctors (normalized doctor attendance)
CREATE TABLE intervention_doctors (
  id SERIAL PRIMARY KEY,
  intervention_id INTEGER NOT NULL REFERENCES interventions(id) ON DELETE CASCADE,
  pcode BIGINT REFERENCES doctors(pcode),
  doctor_name TEXT,
  doctor_class TEXT,
  attendance_type TEXT NOT NULL CHECK (attendance_type IN ('expected', 'actual')),
  UNIQUE(intervention_id, pcode, attendance_type)
);

CREATE INDEX idx_id_pcode ON intervention_doctors(pcode);
CREATE INDEX idx_id_intervention ON intervention_doctors(intervention_id);

-- Table 7: rcpa_monthly (aggregated prescription data)
CREATE TABLE rcpa_monthly (
  id SERIAL PRIMARY KEY,
  pcode BIGINT NOT NULL REFERENCES doctors(pcode),
  country_id INTEGER NOT NULL REFERENCES countries(id),
  month_date DATE NOT NULL,
  brand_group TEXT NOT NULL,
  sku TEXT,
  own_or_competitor TEXT,
  prescription_qty INTEGER DEFAULT 0,
  prescription_value NUMERIC(14,2) DEFAULT 0,
  created_at TIMESTAMPTZ DEFAULT NOW(),
  UNIQUE(pcode, month_date, brand_group, sku, own_or_competitor)
);

CREATE INDEX idx_rcpa_pcode ON rcpa_monthly(pcode);
CREATE INDEX idx_rcpa_country_month ON rcpa_monthly(country_id, month_date);
CREATE INDEX idx_rcpa_brand ON rcpa_monthly(brand_group);
```

A few design decisions worth noting. The execution_pct column in execution_monthly is a generated column — the database computes it automatically from engaged_hcps and planned_hcps. You never have to calculate it in application code. The intervention_doctors table normalizes the raw comma-separated Pcode strings from the Consolidation report into one row per doctor per intervention. The UNIQUE constraints everywhere are what make upserts safe — you can re-run the ingestion script with updated data without creating duplicates.

---

**STEP 3 — INGESTION LAYER**

The ingestion layer is the most technically complex part of the project because the source data is messy. This is where you spend the most careful engineering effort.

**ingestion/config.py**

```python
import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

SUPABASE_URL = os.environ["SUPABASE_URL"]
SUPABASE_SERVICE_KEY = os.environ["SUPABASE_SERVICE_KEY"]

DATA_DIR = Path(os.getenv("DATA_DIR", "./data/raw"))

FILES = {
    "yearly_planner_nepal": DATA_DIR / "FY27_-_Yearly_Planner_Template_Nepal_vf.xlsx",
    "yearly_planner_sri_lanka": DATA_DIR / "FY27_-_Yearly_Planner_Template_Sri_Lanka_vf1_NEW.xlsx",
    "execution_apr": DATA_DIR / "Executiion_YP_Planner_All_BU_s_Apr_Month.xlsx",
    "execution_may": DATA_DIR / "Execution_YP_Planner_All_Bu_s_May_Month.xlsx",
    "consolidation": DATA_DIR / "Consolidation_report_Nov_25_-_01_Jun_26_-_AJ.xlsx",
    "rcpa_nepal_myanmar_current": DATA_DIR / "Nepal___Myanmar_RCPA_Report_Apr_25-mar_26.xlsb",
    "rcpa_sri_lanka_current": DATA_DIR / "Sri_Lanka_RCPA_Report_Apr_25_-_Mar_26.xlsb",
}

TARGET_COUNTRIES = {"Nepal", "Sri Lanka"}
FISCAL_YEAR = "FY27"
```

**ingestion/cleaners.py**

```python
import re
from datetime import datetime, date

EXCEL_EPOCH = datetime(1899, 12, 30)

def excel_serial_to_date(serial: float) -> date | None:
    if not serial or not isinstance(serial, (int, float)):
        return None
    try:
        return (EXCEL_EPOCH + __import__('datetime').timedelta(days=int(serial))).date()
    except Exception:
        return None

def parse_month_to_date(value) -> date | None:
    if value is None:
        return None
    if isinstance(value, (int, float)):
        d = excel_serial_to_date(value)
        if d:
            return d.replace(day=1)
        return None
    if isinstance(value, str):
        for fmt in ("%b-%y", "%b-%Y", "%B-%Y", "%Y-%m-%d"):
            try:
                return datetime.strptime(value.strip(), fmt).date().replace(day=1)
            except ValueError:
                continue
    return None

def normalize_event_name(name: str) -> str:
    if not name:
        return ""
    name = name.strip()
    # Strip trailing month suffix like " - Apr" or " - May 2026"
    name = re.sub(r'\s*[-–]\s*(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[\w\s]*$', '', name, flags=re.IGNORECASE)
    return name.strip()

def normalize_country(name: str) -> str:
    return name.strip().title() if name else ""

def safe_int(value) -> int:
    try:
        return int(float(value)) if value is not None else 0
    except (ValueError, TypeError):
        return 0

def safe_float(value) -> float:
    try:
        return float(value) if value is not None else 0.0
    except (ValueError, TypeError):
        return 0.0

def parse_pcode_list(raw: str | None) -> list[int]:
    if not raw:
        return []
    parts = re.split(r'[;,\s]+', str(raw).strip())
    result = []
    for p in parts:
        try:
            val = int(float(p.strip()))
            if val > 0:
                result.append(val)
        except (ValueError, TypeError):
            continue
    return result
```

**ingestion/loaders/rcpa.py**

This is the most performance-sensitive loader because the files are 370,000 to 425,000 rows. Read row by row using pyxlsb, accumulate into a dictionary keyed by (pcode, month_date, brand_group, sku, own_or_competitor), and only upsert the aggregated values.

```python
from pyxlsb import open_workbook
from collections import defaultdict
from ingestion.cleaners import parse_month_to_date, safe_int, safe_float
from ingestion.config import TARGET_COUNTRIES

def load_rcpa(filepath, supabase_client, country_filter: set[str]) -> dict:
    """
    Reads an xlsb RCPA file row by row, aggregates prescription data
    per (pcode, month, brand_group, sku, own_competitor), and upserts.
    Returns a summary dict with counts.
    """
    aggregated: dict[tuple, dict] = defaultdict(lambda: {"qty": 0, "value": 0.0})
    doctors_seen: dict[int, dict] = {}

    country_col_map = {
        "BU": 0, "Level3": 1, "Level2": 2, "Level1": 3, "Location": 4,
        "Empid": 5, "UserName": 6, "Role": 7, "Designation": 8,
        "Month": 9, "DoctorName": 10, "Pcode": 11, "ActiveStatus": 12,
        "CustomerType": 13, "Speciality": 14, "Class": 15,
        "PatchName": 16, "RCPADate": 17, "CampaignReported": 18,
        "BrandGroup": 19, "SKU": 20, "SKUDetail": 21,
        "OwnCompetitor": 22, "RCPAQty": 23, "RCPAValue": 24,
    }
    # Sri Lanka file has an extra ActiveStatus column at index 12.
    # We detect this from the header row.

    rows_read = 0
    rows_skipped = 0
    doctors_upserted = 0

    with open_workbook(str(filepath)) as wb:
        sheet_name = wb.sheets[0]
        with wb.get_sheet(sheet_name) as ws:
            header = None
            col_idx: dict[str, int] = {}

            for row_data in ws.rows():
                vals = [c.v for c in row_data]

                if header is None:
                    header = [str(v).strip() if v else "" for v in vals]
                    # Build column index from actual header
                    for i, h in enumerate(header):
                        col_idx[h] = i
                    continue

                bu = vals[col_idx.get("BU", 0)]
                if bu not in country_filter:
                    rows_skipped += 1
                    continue

                try:
                    pcode_raw = vals[col_idx["Pcode"]]
                    if not pcode_raw:
                        rows_skipped += 1
                        continue
                    pcode = int(float(pcode_raw))

                    month_raw = vals[col_idx["Month"]]
                    month_date = parse_month_to_date(month_raw)
                    if not month_date:
                        rows_skipped += 1
                        continue

                    brand_group = str(vals[col_idx.get("Brand Group", col_idx.get("BrandGroup", 19))] or "").strip()
                    sku = str(vals[col_idx.get("SKU", 20)] or "").strip()
                    own_comp = str(vals[col_idx.get("Own/Competitor", col_idx.get("OwnCompetitor", 22))] or "").strip()
                    qty = safe_int(vals[col_idx.get("RCPA Quantity", col_idx.get("RCPAQty", 23))])
                    value = safe_float(vals[col_idx.get("RCPA Value", col_idx.get("RCPAValue", 24))])

                    key = (pcode, str(month_date), brand_group, sku, own_comp, str(bu))
                    aggregated[key]["qty"] += qty
                    aggregated[key]["value"] += value

                    if pcode not in doctors_seen:
                        doctor_name = str(vals[col_idx.get("Doctor Name", col_idx.get("DoctorName", 10))] or "").strip()
                        speciality = str(vals[col_idx.get("Speciality", 14)] or "").strip()
                        doc_class = str(vals[col_idx.get("Class", 15)] or "").strip().upper()[:1]
                        patch = str(vals[col_idx.get("PATCHNAME", col_idx.get("PatchName", 16))] or "").strip()
                        status_col = col_idx.get("Active Status", col_idx.get("Status Doctor (Mar'26)", -1))
                        active_status = str(vals[status_col] if status_col >= 0 else "").strip()

                        doctors_seen[pcode] = {
                            "pcode": pcode,
                            "doctor_name": doctor_name,
                            "speciality": speciality,
                            "doctor_class": doc_class if doc_class in ("A", "B", "C") else None,
                            "active_status": active_status,
                            "patch_name": patch,
                            "bu": bu,
                        }

                    rows_read += 1

                except Exception as e:
                    rows_skipped += 1
                    continue

    # Upsert doctors first (rcpa_monthly has FK to doctors)
    doctor_rows = list(doctors_seen.values())
    # Fetch country IDs
    countries_resp = supabase_client.table("countries").select("id, name").execute()
    country_map = {r["name"]: r["id"] for r in countries_resp.data}

    for i in range(0, len(doctor_rows), 500):
        batch = doctor_rows[i:i+500]
        for d in batch:
            d["country_id"] = country_map.get(d.pop("bu"))
        supabase_client.table("doctors").upsert(
            batch, on_conflict="pcode"
        ).execute()
        doctors_upserted += len(batch)

    # Upsert rcpa_monthly aggregates
    rcpa_rows = []
    for (pcode, month_date, brand_group, sku, own_comp, bu), sums in aggregated.items():
        rcpa_rows.append({
            "pcode": pcode,
            "country_id": country_map.get(bu),
            "month_date": month_date,
            "brand_group": brand_group,
            "sku": sku,
            "own_or_competitor": own_comp,
            "prescription_qty": sums["qty"],
            "prescription_value": round(sums["value"], 2),
        })

    inserted = 0
    for i in range(0, len(rcpa_rows), 500):
        batch = rcpa_rows[i:i+500]
        supabase_client.table("rcpa_monthly").upsert(
            batch, on_conflict="pcode,month_date,brand_group,sku,own_or_competitor"
        ).execute()
        inserted += len(batch)

    return {
        "rows_read": rows_read,
        "rows_skipped": rows_skipped,
        "unique_doctors": len(doctors_seen),
        "doctors_upserted": doctors_upserted,
        "rcpa_rows_upserted": inserted,
    }
```

**ingestion/loaders/consolidation.py**

```python
from openpyxl import load_workbook
from ingestion.cleaners import safe_int, safe_float, parse_pcode_list, normalize_country
from datetime import datetime

EXPECTED_COLUMNS = [
    "DIVISION", "Rep Code", "REQUESTED FS", "REQ_ID", "INTERVENTION DATE",
    "Months", "Venue", "INTERVENTION NAME", "INTERVENTION TYPE",
    "ESTIMATED INTERVENTION", "APPROVE/CONFIRMED TOTAL INTERVENTION",
    "NUMBER OF CUSTOMER EXPECTED TO ATTEND", "TOTAL ACTUAL EXPENSES FOR INTERVENTION",
    "DOCTORS ATTENDED INTERVENTION", "Dr. NAME EXPECTED", "Dr.NAME ATTENDED",
    "Dr.CLASS EXPECTED", "Dr.CLASS ATTENDED", "Expected PCODE", "Actual PCODE",
    "ACTUAL DATE OF INTERVENTION", "PENDING FOR APPROVAL Request",
    "PENDING FOR CONFIRMATION Request", "CANCELLATION REASON", "CITY"
]

def load_consolidation(filepath, supabase_client, target_countries: set[str]) -> dict:
    wb = load_workbook(str(filepath), read_only=True)
    ws = wb["Working"]

    header = None
    col_idx: dict[str, int] = {}
    interventions_inserted = 0
    doctors_inserted = 0
    rows_skipped = 0

    countries_resp = supabase_client.table("countries").select("id, name").execute()
    country_map = {r["name"]: r["id"] for r in countries_resp.data}

    intervention_batch = []
    doctor_pairs: list[tuple[int, list[int], list[int], list[str], list[str]]] = []

    for row in ws.iter_rows(values_only=True):
        if header is None:
            header = [str(c).strip() if c else "" for c in row]
            col_idx = {h: i for i, h in enumerate(header)}
            continue

        division = row[col_idx.get("DIVISION", 0)]
        if not division or normalize_country(str(division)) not in target_countries:
            rows_skipped += 1
            continue

        req_id_raw = row[col_idx.get("REQ_ID", 3)]
        if not req_id_raw:
            rows_skipped += 1
            continue

        try:
            req_id = int(float(req_id_raw))
        except (ValueError, TypeError):
            rows_skipped += 1
            continue

        def get(col_name, default=None):
            idx = col_idx.get(col_name)
            return row[idx] if idx is not None and idx < len(row) else default

        def get_date(col_name):
            v = get(col_name)
            if isinstance(v, datetime):
                return v.date().isoformat()
            return None

        country_name = normalize_country(str(division))
        country_id = country_map.get(country_name)

        expected_pcode_raw = str(get("Expected PCODE") or "")
        actual_pcode_raw = str(get("Actual PCODE") or "")
        expected_pcodes = parse_pcode_list(expected_pcode_raw)
        actual_pcodes = parse_pcode_list(actual_pcode_raw)
        expected_names = [n.strip() for n in str(get("Dr. NAME EXPECTED") or "").split(";") if n.strip()]
        expected_classes = [c.strip() for c in str(get("Dr.CLASS EXPECTED") or "").split(";") if c.strip()]
        actual_names = [n.strip() for n in str(get("Dr.NAME ATTENDED") or "").split(";") if n.strip()]
        actual_classes = [c.strip() for c in str(get("Dr.CLASS ATTENDED") or "").split(";") if c.strip()]

        intervention = {
            "req_id": req_id,
            "country_id": country_id,
            "rep_code": str(get("Rep Code") or "").strip(),
            "rep_name": str(get("REQUESTED FS") or "").strip(),
            "intervention_date": get_date("INTERVENTION DATE"),
            "actual_intervention_date": get_date("ACTUAL DATE OF INTERVENTION"),
            "month_label": str(get("Months") or "").strip(),
            "venue": str(get("Venue") or "").strip(),
            "intervention_name": str(get("INTERVENTION NAME") or "").strip(),
            "intervention_type": str(get("INTERVENTION TYPE") or "").strip(),
            "intervention_sub_type": str(get("INTERVENTION SUB TYPE") or "").strip(),
            "topic_remarks": str(get("TOPIC/REMARKS") or "").strip(),
            "estimated_budget_usd": safe_float(get("ESTIMATED INTERVENTION")),
            "total_btc": safe_float(get("TOTAL BTC")),
            "confirmed_budget_usd": safe_float(get("APPROVE/CONFIRMED TOTAL INTERVENTION")),
            "total_actual_expenses_usd": safe_float(get("TOTAL ACTUAL EXPENSES FOR INTERVENTION")),
            "num_doctors_expected": safe_int(get("NUMBER OF CUSTOMER EXPECTED TO ATTEND")),
            "num_doctors_attended": safe_int(get("DOCTORS ATTENDED INTERVENTION")),
            "doctor_category_expected": str(get("DR.CATEGORY EXPECTED TO ATTEND") or "").strip(),
            "approval_status": str(get("PENDING FOR APPROVAL Request") or "").strip(),
            "confirmation_status": str(get("PENDING FOR CONFIRMATION Request") or "").strip(),
            "doctor_names_expected": str(get("Dr. NAME EXPECTED") or "").strip(),
            "doctor_names_attended": str(get("Dr.NAME ATTENDED") or "").strip(),
            "doctor_class_expected": str(get("Dr.CLASS EXPECTED") or "").strip(),
            "doctor_class_attended": str(get("Dr.CLASS ATTENDED") or "").strip(),
            "expected_pcode_raw": expected_pcode_raw,
            "actual_pcode_raw": actual_pcode_raw,
            "city": str(get("CITY") or "").strip(),
            "cancellation_reason": str(get("CANCELLATION REASON") or "").strip(),
        }

        intervention_batch.append(intervention)
        doctor_pairs.append((req_id, expected_pcodes, actual_pcodes, expected_names, actual_names))

    wb.close()

    # Upsert interventions in batches of 200
    req_to_id: dict[int, int] = {}
    for i in range(0, len(intervention_batch), 200):
        batch = intervention_batch[i:i+200]
        resp = supabase_client.table("interventions").upsert(
            batch, on_conflict="req_id"
        ).execute()
        if resp.data:
            for r in resp.data:
                req_to_id[r["req_id"]] = r["id"]
        interventions_inserted += len(batch)

    # Fetch all req_ids to get their database IDs (upsert may not return IDs for existing rows)
    all_req_ids = [b["req_id"] for b in intervention_batch]
    for i in range(0, len(all_req_ids), 500):
        chunk = all_req_ids[i:i+500]
        resp = supabase_client.table("interventions").select("id, req_id").in_("req_id", chunk).execute()
        for r in resp.data:
            req_to_id[r["req_id"]] = r["id"]

    # Upsert intervention_doctors
    id_rows = []
    for req_id, exp_pcodes, act_pcodes, exp_names, act_names in doctor_pairs:
        int_id = req_to_id.get(req_id)
        if not int_id:
            continue
        for j, pcode in enumerate(exp_pcodes):
            id_rows.append({
                "intervention_id": int_id,
                "pcode": pcode if pcode > 0 else None,
                "doctor_name": exp_names[j] if j < len(exp_names) else None,
                "doctor_class": None,
                "attendance_type": "expected",
            })
        for j, pcode in enumerate(act_pcodes):
            id_rows.append({
                "intervention_id": int_id,
                "pcode": pcode if pcode > 0 else None,
                "doctor_name": act_names[j] if j < len(act_names) else None,
                "doctor_class": None,
                "attendance_type": "actual",
            })

    for i in range(0, len(id_rows), 500):
        batch = id_rows[i:i+500]
        supabase_client.table("intervention_doctors").upsert(
            batch, on_conflict="intervention_id,pcode,attendance_type"
        ).execute()
        doctors_inserted += len(batch)

    return {
        "interventions_upserted": interventions_inserted,
        "intervention_doctors_upserted": doctors_inserted,
        "rows_skipped": rows_skipped,
    }
```

**ingestion/main.py**

```python
import sys
import time
from supabase import create_client
from ingestion.config import SUPABASE_URL, SUPABASE_SERVICE_KEY, FILES, TARGET_COUNTRIES
from ingestion.loaders.yearly_planner import load_yearly_planner
from ingestion.loaders.execution_monthly import load_execution_monthly
from ingestion.loaders.consolidation import load_consolidation
from ingestion.loaders.rcpa import load_rcpa

def main():
    print("Initializing Supabase client...")
    sb = create_client(SUPABASE_URL, SUPABASE_SERVICE_KEY)

    results = {}
    start = time.time()

    print("\n[1/4] Loading yearly planners...")
    for key in ["yearly_planner_nepal", "yearly_planner_sri_lanka"]:
        r = load_yearly_planner(FILES[key], sb, TARGET_COUNTRIES)
        results[key] = r
        print(f"  {key}: {r}")

    print("\n[2/4] Loading execution monthly files...")
    for key in ["execution_apr", "execution_may"]:
        r = load_execution_monthly(FILES[key], sb, TARGET_COUNTRIES)
        results[key] = r
        print(f"  {key}: {r}")

    print("\n[3/4] Loading consolidation report...")
    r = load_consolidation(FILES["consolidation"], sb, TARGET_COUNTRIES)
    results["consolidation"] = r
    print(f"  consolidation: {r}")

    print("\n[4/4] Loading RCPA files (large files, this will take a few minutes)...")
    for key in ["rcpa_nepal_myanmar_current", "rcpa_sri_lanka_current"]:
        r = load_rcpa(FILES[key], sb, TARGET_COUNTRIES)
        results[key] = r
        print(f"  {key}: {r}")

    elapsed = round(time.time() - start, 1)
    print(f"\n✓ Ingestion complete in {elapsed}s")

    # Join coverage check
    print("\nRunning join coverage check...")
    id_count = sb.table("intervention_doctors").select("pcode", count="exact").neq("pcode", None).execute()
    matched = sb.table("intervention_doctors").select("pcode", count="exact").neq("pcode", None).execute()
    rcpa_pcodes = sb.rpc("count_distinct_rcpa_pcodes", {}).execute()
    print(f"  Intervention doctors with a Pcode: {id_count.count}")
    print(f"  RCPA unique Pcodes: {rcpa_pcodes.data}")
    print("\nIngestion report complete.")

if __name__ == "__main__":
    main()
```

To run the ingestion: from the project root, run `python -m ingestion.main`

---

**STEP 4 — FASTAPI BACKEND**

**backend/config.py**

```python
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    supabase_url: str
    supabase_anon_key: str
    anthropic_api_key: str

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

settings = Settings()
```

**backend/database.py**

```python
from functools import lru_cache
from supabase import create_client, Client
from backend.config import settings

@lru_cache(maxsize=1)
def get_supabase() -> Client:
    return create_client(settings.supabase_url, settings.supabase_anon_key)
```

**backend/schemas/execution.py**

```python
from pydantic import BaseModel
from typing import Optional

class ExecutionSummary(BaseModel):
    total_events: int
    executed_events: int
    action_due_events: int
    event_execution_pct: float
    total_planned_hcps: int
    total_engaged_hcps: int
    hcp_execution_pct: float
    total_sanctioned_budget_usd: float
    total_actual_spend_usd: float
    budget_gap_usd: float

class ExecutionMatrixRow(BaseModel):
    event_name: str
    event_type: str
    therapy: Optional[str]
    planned_hcps: int
    engaged_hcps: int
    raised_requests: int
    execution_pct: float
    intervention_status: str
    sanctioned_budget_usd: float
    actual_spend_usd: float
    budget_gap_usd: float

class ExecutionMatrixResponse(BaseModel):
    summary: ExecutionSummary
    events: list[ExecutionMatrixRow]
    country: str
    month: str
```

Define similarly typed schemas for all other routers. Every API response should have a typed Pydantic model. This prevents you from accidentally returning raw database rows and makes the TypeScript types on the frontend trivial to write.

**backend/services/execution_service.py**

```python
from supabase import Client
from backend.schemas.execution import ExecutionSummary, ExecutionMatrixRow, ExecutionMatrixResponse

def get_execution_matrix(
    db: Client,
    country: str,
    month: str
) -> ExecutionMatrixResponse:
    country_resp = db.table("countries").select("id").eq("name", country).single().execute()
    if not country_resp.data:
        raise ValueError(f"Country not found: {country}")
    country_id = country_resp.data["id"]

    em_resp = db.table("execution_monthly").select(
        "event_name, event_type, planned_hcps, engaged_hcps, raised_request_count, "
        "intervention_status, execution_pct, yearly_plan_id"
    ).eq("country_id", country_id).eq("month_label", month).execute()

    rows = em_resp.data or []

    # Fetch yearly plan budgets for these events
    yp_ids = [r["yearly_plan_id"] for r in rows if r.get("yearly_plan_id")]
    yp_budgets: dict[int, float] = {}
    if yp_ids:
        yp_resp = db.table("yearly_plan").select("id, total_cost_usd").in_("id", yp_ids).execute()
        yp_budgets = {r["id"]: r["total_cost_usd"] for r in yp_resp.data}

    # Fetch actual spend from interventions for this country and month
    int_resp = db.table("interventions").select(
        "intervention_name, total_actual_expenses_usd"
    ).eq("country_id", country_id).eq("month_label", month).execute()
    actual_spend_by_name: dict[str, float] = {}
    for r in int_resp.data or []:
        key = r["intervention_name"].lower().strip()
        actual_spend_by_name[key] = actual_spend_by_name.get(key, 0) + r["total_actual_expenses_usd"]

    matrix_rows = []
    total_planned = total_engaged = total_sanctioned = total_actual = 0
    executed = action_due = 0

    for r in rows:
        sanctioned = yp_budgets.get(r.get("yearly_plan_id"), 0.0)
        actual = actual_spend_by_name.get(r["event_name"].lower().strip(), 0.0)
        gap = sanctioned - actual

        matrix_rows.append(ExecutionMatrixRow(
            event_name=r["event_name"],
            event_type=r["event_type"],
            therapy=None,
            planned_hcps=r["planned_hcps"],
            engaged_hcps=r["engaged_hcps"],
            raised_requests=r["raised_request_count"],
            execution_pct=float(r["execution_pct"] or 0),
            intervention_status=r["intervention_status"] or "Unknown",
            sanctioned_budget_usd=sanctioned,
            actual_spend_usd=actual,
            budget_gap_usd=gap,
        ))

        total_planned += r["planned_hcps"]
        total_engaged += r["engaged_hcps"]
        total_sanctioned += sanctioned
        total_actual += actual
        if r["intervention_status"] == "Executed":
            executed += 1
        else:
            action_due += 1

    total_events = len(rows)
    event_pct = round((executed / total_events * 100), 2) if total_events > 0 else 0
    hcp_pct = round((total_engaged / total_planned * 100), 2) if total_planned > 0 else 0

    summary = ExecutionSummary(
        total_events=total_events,
        executed_events=executed,
        action_due_events=action_due,
        event_execution_pct=event_pct,
        total_planned_hcps=total_planned,
        total_engaged_hcps=total_engaged,
        hcp_execution_pct=hcp_pct,
        total_sanctioned_budget_usd=round(total_sanctioned, 2),
        total_actual_spend_usd=round(total_actual, 2),
        budget_gap_usd=round(total_sanctioned - total_actual, 2),
    )

    return ExecutionMatrixResponse(summary=summary, events=matrix_rows, country=country, month=month)
```

All business logic lives in service functions. Routers stay thin and only handle HTTP concerns.

**backend/routers/execution.py**

```python
from fastapi import APIRouter, Depends, Query, HTTPException
from supabase import Client
from backend.database import get_supabase
from backend.schemas.execution import ExecutionMatrixResponse
from backend.services.execution_service import get_execution_matrix

router = APIRouter(prefix="/api/execution", tags=["Execution"])

@router.get("/matrix", response_model=ExecutionMatrixResponse)
def execution_matrix(
    country: str = Query(..., description="Country name e.g. Nepal"),
    month: str = Query(..., description="Month label e.g. May"),
    db: Client = Depends(get_supabase),
):
    try:
        return get_execution_matrix(db, country, month)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal error computing execution matrix")
```

Follow the same pattern for budget, doctors, and ai_query routers. Route handlers are 10 lines maximum. Everything else is in services.

**backend/services/ai_service.py**

```python
import anthropic
from supabase import Client
from backend.config import settings

client = anthropic.Anthropic(api_key=settings.anthropic_api_key)

def build_kpi_context(db: Client, country: str, month: str) -> str:
    # Pull live KPI data to ground the AI response
    country_resp = db.table("countries").select("id").eq("name", country).single().execute()
    if not country_resp.data:
        return "No data available for this country."
    cid = country_resp.data["id"]

    em = db.table("execution_monthly").select(
        "event_name, planned_hcps, engaged_hcps, intervention_status"
    ).eq("country_id", cid).eq("month_label", month).execute()

    top_rx = db.table("rcpa_monthly").select(
        "pcode, prescription_qty, prescription_value"
    ).eq("country_id", cid).order("prescription_qty", desc=True).limit(10).execute()

    context_lines = [
        f"Country: {country}, Month: {month}",
        "",
        "EXECUTION SUMMARY:",
    ]
    executed = sum(1 for r in em.data if r["intervention_status"] == "Executed")
    action_due = sum(1 for r in em.data if r["intervention_status"] == "Action due")
    total_planned = sum(r["planned_hcps"] for r in em.data)
    total_engaged = sum(r["engaged_hcps"] for r in em.data)
    context_lines.append(f"  Total events: {len(em.data)}, Executed: {executed}, Action due: {action_due}")
    context_lines.append(f"  Planned HCPs: {total_planned}, Engaged HCPs: {total_engaged}")
    if total_planned > 0:
        context_lines.append(f"  HCP execution rate: {round(total_engaged/total_planned*100, 1)}%")

    context_lines.append("")
    context_lines.append("ACTION DUE EVENTS (top 5 by missed doctors):")
    missed = [(r["event_name"], r["planned_hcps"] - r["engaged_hcps"]) for r in em.data if r["intervention_status"] == "Action due"]
    missed.sort(key=lambda x: x[1], reverse=True)
    for name, gap in missed[:5]:
        context_lines.append(f"  - {name}: {gap} doctors not yet engaged")

    return "\n".join(context_lines)

def query_ai(db: Client, country: str, month: str, question: str) -> str:
    context = build_kpi_context(db, country, month)

    system_prompt = (
        "You are an executive assistant for Cipla's marketing operations team. "
        "You receive structured data about marketing execution performance across markets. "
        "Answer questions concisely and directly using the provided data context. "
        "Do not invent numbers. If the context does not contain enough information to answer, say so clearly. "
        "Keep answers short — 2 to 5 sentences or a brief bullet list maximum."
    )

    user_message = f"Context:\n{context}\n\nQuestion: {question}"

    response = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=500,
        system=system_prompt,
        messages=[{"role": "user", "content": user_message}]
    )

    return response.content[0].text
```

**backend/main.py**

```python
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.routers import execution, budget, doctors, ai_query

app = FastAPI(title="Cipla Execution Intelligence API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(execution.router)
app.include_router(budget.router)
app.include_router(doctors.router)
app.include_router(ai_query.router)

@app.get("/health")
def health():
    return {"status": "ok"}
```

Run the backend with: `uvicorn backend.main:app --reload --port 8000`

The interactive API documentation is automatically available at http://localhost:8000/docs — use this to test every endpoint before touching the frontend.

---

**STEP 5 — FRONTEND**

**Technology decisions**

Use Vite with the React TypeScript template. Use Tailwind CSS for all styling — it produces clean, consistent UI without writing CSS files. Use React Query for all API calls. Use Zustand for the global country and month selectors. Use Recharts for all charts. Use Lucide React for icons.

**src/store/filters.ts**

```typescript
import { create } from 'zustand'

interface FilterStore {
  country: string
  month: string
  setCountry: (c: string) => void
  setMonth: (m: string) => void
}

export const useFilterStore = create<FilterStore>((set) => ({
  country: 'Nepal',
  month: 'May',
  setCountry: (country) => set({ country }),
  setMonth: (month) => set({ month }),
}))
```

**src/api/execution.ts**

```typescript
import axios from 'axios'

const BASE = import.meta.env.VITE_API_URL || 'http://localhost:8000'

export interface ExecutionSummary {
  total_events: number
  executed_events: number
  action_due_events: number
  event_execution_pct: number
  total_planned_hcps: number
  total_engaged_hcps: number
  hcp_execution_pct: number
  total_sanctioned_budget_usd: number
  total_actual_spend_usd: number
  budget_gap_usd: number
}

export interface ExecutionMatrixRow {
  event_name: string
  event_type: string
  therapy: string | null
  planned_hcps: number
  engaged_hcps: number
  raised_requests: number
  execution_pct: number
  intervention_status: 'Executed' | 'Action due' | 'Unknown'
  sanctioned_budget_usd: number
  actual_spend_usd: number
  budget_gap_usd: number
}

export interface ExecutionMatrixResponse {
  summary: ExecutionSummary
  events: ExecutionMatrixRow[]
  country: string
  month: string
}

export const fetchExecutionMatrix = async (
  country: string,
  month: string
): Promise<ExecutionMatrixResponse> => {
  const { data } = await axios.get(`${BASE}/api/execution/matrix`, {
    params: { country, month },
  })
  return data
}
```

Define matching typed functions for every backend endpoint. This creates a clean API contract layer and means the components never write axios calls inline.

**src/hooks/useExecution.ts**

```typescript
import { useQuery } from '@tanstack/react-query'
import { fetchExecutionMatrix } from '../api/execution'
import { useFilterStore } from '../store/filters'

export function useExecutionMatrix() {
  const { country, month } = useFilterStore()
  return useQuery({
    queryKey: ['execution-matrix', country, month],
    queryFn: () => fetchExecutionMatrix(country, month),
    staleTime: 1000 * 60 * 5, // 5 minutes cache
  })
}
```

**src/pages/ExecutionMatrix.tsx — structure only**

The page is composed of three sections. The top section has four KPI cards showing event execution percentage, HCP execution percentage, budget utilized, and budget gap. Each card shows the number prominently, a subtle trend indicator if historical data allows, and a colour (green for healthy, amber for moderate, red for concerning). The middle section has a stacked bar chart from Recharts showing planned versus engaged HCPs per event type for the selected month — this is the visual Abhijeet showed on screen. The bottom section has a data table with one row per event, sortable columns, a search input, and a status filter. Each row has a coloured badge for Executed (green) or Action due (red). Clicking any row opens a right-side panel showing the full intervention detail from the Consolidation report including the approval chain.

Every section has three states: a loading skeleton using Tailwind animate-pulse, an error state with a descriptive message, and the data state. Never render a blank page.

**src/components/panels/AIPanel.tsx — structure only**

The AI panel is a fixed sidebar on the right edge of the screen, toggled by a floating button. It has a chat interface with a message list and an input at the bottom. Four pre-built prompt chips appear above the input: "What's at risk this month", "Top prescribers not engaged", "Biggest budget gaps", "Weekly highlights". Sending a message calls POST /api/ai/query, shows a loading indicator (a pulsing dot), and renders the response as formatted text. The panel maintains the conversation history in React state for the duration of the session.

---

**STEP 6 — BUILD ORDER AND MILESTONES**

Milestone 1 is data verified. Run the ingestion script, verify all tables have data in Supabase, check that the doctor ROI join works by running a manual SQL query joining intervention_doctors to rcpa_monthly on pcode. Only proceed when the join returns meaningful rows.

Milestone 2 is API verified. Stand up FastAPI, test the execution matrix endpoint in the /docs interface with Nepal and May as parameters. Verify the response shape matches your Pydantic schema. Test all seven endpoints before touching the frontend.

Milestone 3 is first demoable tab. Build the Execution Matrix tab in React end to end with real data, all three states (loading, error, data), the KPI cards, the bar chart, and the table. This is your first checkpoint with Abhijeet.

Milestone 4 is full dashboard. Add Budget Utilization, Doctor ROI, and Event Tracker tabs. The Doctor ROI scatter plot is your headline feature — make it look sharp.

Milestone 5 is AI layer. Add the AI panel. Test that responses are grounded in real data and not hallucinated. Tune the system prompt if responses are too generic.

Milestone 6 is polish and demo prep. Add country and month selectors to the top nav that drive all four tabs simultaneously. Add a data freshness indicator showing when the data was last ingested. Make sure the app looks good at 1920x1080 and 1440x900.

---

**ARCHITECTURAL RISKS AND HOW TO HANDLE THEM**

The biggest risk is the Pcode join coverage. Not all doctors in the Consolidation report will have a matching Pcode in the RCPA data. This is expected — some interventions are with doctors who are not in the prescription tracking system. Run the join coverage check in your ingestion report and surface the percentage. If coverage is below 60% it is worth raising with Abhijeet before the demo.

The second risk is RCPA file read time. The three files contain a combined 1.1 million rows. The chunked ingestion approach handles this but it will take 5 to 15 minutes to run. This is fine for an offline ingestion script. Never run RCPA ingestion from a web request.

The third risk is the event name join between Execution YP Planner and Yearly Planner. The execution file appends " - May" or " - Apr" to event names. Your normalize_event_name function strips this suffix. Verify that the join is working after ingestion by checking how many execution_monthly rows have a non-null yearly_plan_id. If it is below 70% there is a naming inconsistency you need to investigate and fix in the cleaner.

The fourth risk is Sri Lanka having no dedicated sheet in the May Execution file. Sri Lanka execution data for May must be derived from the Consolidation report filtered to DIVISION equals Sri Lanka and month_label equals May-26. Your execution service already does this correctly but test it explicitly.

---

**ON YOUR RESUME AND IN INTERVIEWS**

This project is worth describing in terms of the engineering decisions, not the features. You designed a data pipeline that ingests 1.1 million rows from binary Excel files, aggregated them to a clean relational model with proper foreign keys and join coverage validation, built a typed REST API in FastAPI, and built a React dashboard with TypeScript and React Query. You implemented a grounded AI query feature using context injection rather than hallucination. The core join — linking doctor engagement spend to prescription output via a unique ID — is the business insight that makes the whole project meaningful.

When a FAANG interviewer asks "tell me about a project," this is the answer: you took a real business problem, did the data modeling work from scratch on messy real data, made architectural decisions about where to aggregate versus where to store raw data, built a typed end-to-end system, and delivered something a non-technical stakeholder found genuinely useful. That is what a staff engineer does.