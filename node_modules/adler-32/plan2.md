**HONEST EVALUATION: IS THIS A BETTER PLAN?**

The short answer is yes, it is architecturally more correct and more rigorous than what we had before. But it is not a drop-in replacement — some parts are genuinely better, some parts are over-engineered for your current situation, and a few things it says are improvements that our prior discussion already handled correctly. Here is a precise breakdown of every meaningful difference.

---

**WHERE THIS PLAN IS GENUINELY BETTER AND YOU SHOULD ADOPT IT**

The event_matches table is the single biggest improvement in this document. Our prior architecture relied on event name string matching happening invisibly inside your ingestion Python code. This plan makes it an explicit, queryable, auditable database table with a match_method column (exact, normalized, fuzzy, manual) and a match_confidence score. This matters for three concrete reasons. First, when Abhijeet or Pralhad look at the dashboard and ask "why does this event show no execution data," you can query the event_matches table and tell them exactly why — the event name normalized to X but no match was found in the consolidation report. Second, weak matches (fuzzy) are flagged rather than silently accepted, so the dashboard can warn users when a metric is based on uncertain data. Third, you can add a manual override later where Abhijeet can tell the system "this event in the planner is the same as this event in the consolidation report" without rerunning ingestion. This is real product thinking. Adopt it completely.

Storing Pcode as text rather than BIGINT is correct and we should have done this from the start. The Nepal/Myanmar RCPA files store Pcode as a float (929400.0) and the Sri Lanka file also has it as a float. When you cast float to integer you risk losing precision on large IDs or introducing a 0 where the value was None. More importantly, Pcode might not always be purely numeric — if Cipla ever introduces alphanumeric doctor IDs in a future market you would break. Storing pcode_raw (exactly as it appears in the source) and pcode_normalized (cleaned, whitespace stripped, decimal removed) as text columns is the right call. Adopt this completely and update the doctors table and all foreign references.

The calendar_months table solves a real problem we glossed over. We have month values stored as "Apr-24", "Apr'26", serial numbers like 45772, and "May-26" across different files. Rather than normalizing these ad-hoc in ingestion code and then storing inconsistent strings in tables, a canonical calendar_months table gives you one row per month with month_start_date as a proper DATE, fiscal_year as "FY27", fiscal_month_number (1 through 12 where 1 is April), and display_label. Everything that references a month gets a foreign key to this table. This makes filtering by month in SQL straightforward and eliminates string comparison bugs. Adopt this completely.

Materialized views for KPI computation is architecturally cleaner than what we had. In our plan the execution summary KPIs were computed in Python inside the FastAPI service function — joining tables, summing, dividing. That works but it means the same computation runs on every API request. Materialized views push that computation into PostgreSQL, refresh on demand after each ingestion run, and make the API layer a simple SELECT from a pre-computed view. The API stays fast even as data grows, and the KPI logic lives in SQL where it can be inspected, version-controlled, and tested independently of application code. The five views proposed — mv_execution_kpis, mv_budget_utilization, mv_doctor_roi, mv_data_quality, mv_unmatched_events — map directly to your five dashboard tabs. Adopt this completely.

The data quality dashboard as a first-class tab is a product improvement our plan did not include. When event match coverage is 60% you want the user to see a warning, not a misleading KPI. The mv_data_quality view and the mv_unmatched_events view make this possible. A dedicated data quality section that shows "14 events in the yearly planner have no match in the consolidation report" is both honest and actionable. This also gives you something credible to show Abhijeet in a governance review — you are not hiding data quality issues, you are surfacing them. Adopt this completely.

The explicit test plan is something we did not have and should have had. The specific tests listed are all real edge cases grounded in the actual files — April status 1 versus blank normalization, Nepal planner preferring Yearly Planner FY27 v2 over YP FY27, Sri Lanka deriving May execution from consolidation rather than a country tab. These are the exact places where your ingestion will silently produce wrong data if you do not test them. Every one of these should become an actual Python test using pytest before you run ingestion on the real files.

Retaining the historical Nepal/Myanmar RCPA file (Apr 2024 to Mar 2025) for trend context is correct. We suggested ignoring it for MVP but Abhijeet mentioned trends explicitly in the call. If you can show that a doctor's prescription volume grew from 200/month last year to 350/month this year, and that growth coincides with Cipla events they attended, you have demonstrated marketing ROI causally, not just correlatively. That is a much stronger story. Keep this file in scope.

The Nepal planner canonical sheet selection is a detail we almost got wrong. The Nepal planner has two substantive sheets — YP FY27 and Yearly Planner FY27 v2. The v2 sheet has an additional HO Finalized column. This plan explicitly says to prefer v2 if present. That is the right call because v2 is more complete.

---

**WHERE THIS PLAN IS OVER-ENGINEERED FOR YOUR CURRENT SITUATION**

The raw_source_rows table storing every source row as a raw JSON payload is the most over-engineered element in the plan. The intent is good — full auditability, ability to re-derive anything from the raw data. The problem is practical scale. The three current-year RCPA files contain approximately 1.175 million rows. Storing every one as a JSON blob in raw_source_rows means inserting 1.175 million rows into a table that was not designed for efficient querying of business data. Supabase free tier has a 500MB database limit. At an average of 400 bytes per JSON row for RCPA data, 1.175 million rows is roughly 470MB — almost your entire database budget just for raw rows you will never query directly. For the yearly planner files and consolidation report (a few thousand rows total) raw storage is fine. For RCPA files you should skip raw storage and rely on the aggregated rcpa_prescriptions table as your canonical record instead. The ingestion report (row counts, validation error counts, hash checks) gives you enough auditability without storing every raw row.

The full staging layer — separate validated staging tables before canonical tables — adds a two-phase write process that doubles your ingestion complexity and ingestion time. In a production ETL system at a company with multiple engineers this is correct practice. For a solo intern project with eight known files from one stakeholder, the overhead is not justified at this stage. A pragmatic middle ground: validate in Python with Pydantic models before writing to canonical tables, and write validation errors to the validation_errors table. This gives you the error capture benefit without the full staging table overhead.

The source_sheets table storing column lists and row counts is genuinely useful for the workbook profiler during development but adds little value in production after the files are confirmed to load correctly. Build the profiler as a development tool, not as a persistent database table.

---

**WHERE OUR PRIOR PLAN HAD DETAILS THIS ONE LACKS**

This architecture plan does not mention the Sri Lanka RCPA currency issue. Sri Lanka RCPA values are in Sri Lankan Rupees, Nepal values are in Nepali Rupees, Myanmar values are in Myanmar Kyat. If you display raw RCPA values across countries on the same chart the numbers are meaningless for comparison. Either you need to normalize to USD using an exchange rate table, or you need to clearly label currency on every value and avoid cross-country monetary comparisons. This plan does not address it.

This plan does not specify how to handle the pcode semicolon-separated strings in the Consolidation report for multi-doctor events. That parsing logic is the most fragile part of the ingestion and needs explicit handling — splitting on semicolons, validating each piece is numeric, handling nulls and empty strings.

This plan does not mention that the execution_monthly data for Sri Lanka in May must come from the Consolidation report because the May Execution file has no Sri Lanka tab. It mentions it in passing under "Source-specific decisions" but does not explain the derivation logic.

---

**WHAT THE COMBINED FINAL ARCHITECTURE SHOULD LOOK LIKE**

Take this plan as the architectural skeleton and layer in the implementation specifics from our prior conversation. The specific changes to make:

Adopt the event_matches table exactly as described. Adopt the calendar_months table. Adopt pcode as text with pcode_raw and pcode_normalized. Adopt materialized views for all KPI computation. Adopt the data quality tab and unmatched events view. Adopt the test plan in full. Retain the historical RCPA file.

Skip raw_source_rows for RCPA data — aggregate in Python and write only to rcpa_prescriptions. Keep raw_source_rows for the other files (yearly planner, execution monthly, consolidation) where row counts are small enough that full storage is fine. Keep validation_errors. Keep ingestion_runs. Keep source_files with file hash for change detection.

Skip the full staging table layer — validate with Pydantic in Python and write errors to validation_errors, then write directly to canonical tables with upsert.

The resulting schema is fourteen tables plus five materialized views. That is more than our original seven tables but every table earns its place. This is what a defensible, portfolio-grade architecture looks like.

---

**FINAL VERDICT**

This document is a genuine improvement on the prior plan in the areas that matter most — reconciliation strategy, KPI computation location, Pcode handling, and data quality visibility. It is over-engineered in the raw storage layer for RCPA scale. It is under-specified on implementation details that our file analysis conversations filled in. The right move is to merge both: use this document as your architectural governance document and use the implementation code and file-specific details from our earlier conversation as your execution guide. Do not treat either one as complete without the other.