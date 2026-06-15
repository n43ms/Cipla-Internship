These documents are comprehensive and coherent. They tell a consistent story across all six files with good traceability — spec defines the what, finalplan and plan define the how, data-model defines the entities, research explains the why, and quickstart defines how to validate it all. Here is an honest evaluation of what is solid, what is inconsistent, and what is missing.

---

**What is solid and correct**

The three-table audit design in data-model.md — `ingestion_runs`, `source_files`, and `ingestion_run_files` — is the right call and correctly fixes the earlier mistake of treating `file_hash` as sufficient to model run participation. Keep this exactly as specified.

The event_matches reconciliation strategy is the strongest architectural decision in these docs. The match_method and match_confidence fields mean weak joins are visible data, not hidden assumptions. This is what makes the dashboard trustworthy.

The materialized view approach for KPIs is correct. Dashboard APIs should query pre-computed views, not join raw canonical tables on every request.

The RCPA aggregation decision — aggregate in Python before writing to the database — is the right call at this data volume. The grain defined in data-model.md (country, month, Pcode, brand group, SKU, own/competitor, source file) is appropriate.

The security constraints are clean and consistent across all documents: service role key only in ingestion and backend server, frontend talks only to the backend API, AI provider never called from the frontend. These are stated the same way in every doc.

---

**Where there are inconsistencies between documents**

The XLSB reader decision is stated differently across files. research.md clearly says python-calamine as primary with pyxlsb as fallback. plan.md says the same. But finalplan.md says "pyxlsb or python-calamine" with no clear primary. The quickstart.md omits this entirely. Pick python-calamine as primary now and document that decision in your implementation config. Do not leave it ambiguous when you write the actual loader.

The data access layer is similarly inconsistent. research.md makes a clear, well-reasoned case for SQLAlchemy 2.0 plus Alembic. finalplan.md hedges with "Supabase Python client or SQLAlchemy." plan.md adopts SQLAlchemy. Go with SQLAlchemy and Alembic everywhere. The Supabase Python client is useful for the ingestion script's simple upserts but SQLAlchemy handles migrations, transactions, and typed repositories correctly. Do not use the Supabase client as your primary data layer.

---

**What is missing and needs to be added before you start coding**

The Excel serial number date format is not mentioned anywhere in these documents. During our actual file inspection we discovered that the current-year Nepal/Myanmar RCPA file and the Sri Lanka RCPA file store months as Excel serial numbers (values like 45772) rather than string formats like Apr-25. Your month normalizer in code must handle this as a fourth format alongside the three listed in finalplan.md. Add it to the RCPA normalizer spec now or you will hit a silent data loss bug in production.

Exchange rates have no seed or source defined. The data-model.md defines the `exchange_rates` table and finalplan.md mentions currency normalization, but nowhere in these six documents does it say where exchange rate values come from or when they get populated. For MVP you need to manually seed one rate per currency at a fixed representative date and document that this is a static seed, not a live feed. Add this to your quickstart.

The `question_redacted` field in `ai_query_logs` has no redaction logic defined. It is named as if redaction happens, but the implementation detail of what gets stripped or masked is not specified anywhere. Define this before you build the AI logging step — at minimum it should strip any content that looks like a doctor name, Pcode, or monetary value before storage.

The Alembic setup is assumed in quickstart.md (step 3 runs `alembic upgrade head`) but the prerequisites section does not mention configuring alembic.ini or the database URL. Add the Alembic initialization steps to the quickstart or someone running it from scratch will hit an immediate failure.

Test fixtures are called out as synthetic and small across multiple docs but no fixture structure or naming convention is defined. Before you write a single test, decide where synthetic fixtures live (`ingestion/tests/fixtures/`), what format they take (tiny xlsx and xlsb files with three to five rows), and which edge cases each fixture covers. The test list in finalplan.md section 14 is thorough but needs fixtures to be runnable.

The Sri Lanka May execution derivation is correctly identified as a limitation but the derivation logic is not specified. The spec says "derives execution evidence from consolidation requests" but does not define the SQL or Python logic for how you construct a Sri Lanka May execution snapshot from the consolidation report. You need to write this out explicitly before you build the execution snapshot loader — otherwise the decision gets made ad hoc in the middle of a loader function where it is hard to test.

---

**One data model concern to resolve before migrations**

The unique constraint on `rcpa_prescriptions` is not explicitly defined in data-model.md. The aggregate grain includes `source_file_id`, which means if you run ingestion twice with the same file, you will get two sets of aggregated rows unless the upsert conflict target includes all grain columns including `source_file_id`. If `source_file_id` is part of the unique constraint, re-ingesting the same file is idempotent. If it is not, re-ingesting produces duplicates. Make this explicit in your migration before writing the RCPA loader.

---

**Verdict**

These are production-quality planning documents. The architecture is sound, the entity model is correct, the milestone ordering is right, and the security posture is clean. Fix the seven gaps above — the serial date format, exchange rate seeding, redaction logic, Alembic setup in quickstart, fixture structure, Sri Lanka May derivation logic, and the RCPA unique constraint — before you write any code. Everything else is implementation-ready.