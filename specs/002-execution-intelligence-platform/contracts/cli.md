# CLI Contract: Local Ingestion

The ingestion CLI is the only MVP writer of source-derived business data.

## Common Options

```bash
python -m ingestion.main <command> \
  --data-dir data/raw \
  --run-label "manual-2026-06-14" \
  --environment local
```

Rules:

- source workbooks are read from `DATA_DIR` or `--data-dir`,
- real source files remain gitignored,
- every write command creates or references an `ingestion_runs` record,
- commands return non-zero when fatal validation prevents safe continuation.

## Commands

### profile

```bash
python -m ingestion.main profile --data-dir data/raw --output data/reports/profile.json
```

Output:

- detected files,
- source type classification,
- sheet names,
- used ranges,
- detected headers,
- required-column coverage,
- row counts,
- detected month value formats including Excel serial numbers,
- detected transcript-critical consolidation fields for financial mapping, workflow governance, intervention mix, and reporting status,
- anomalies and warnings.

### ingest

```bash
python -m ingestion.main ingest --source all
python -m ingestion.main ingest --source planner
python -m ingestion.main ingest --source consolidation
python -m ingestion.main ingest --source execution
python -m ingestion.main ingest --source rcpa
```

Behavior:

- creates an ingestion run,
- registers source files,
- validates and loads selected source types,
- records validation errors,
- parses RCPA month strings and Excel serial-number dates through the same canonical month normalizer,
- upserts RCPA aggregates through the explicit aggregate unique key,
- maps consolidation financial fields into estimated, confirmed/contracted, direct HCP/BTU, overhead/BTC, total actual, and association amount fields,
- maps request approval, request confirmation, post/report approval, and post/report confirmation statuses from consolidation lifecycle columns,
- produces a run summary.

### reconcile

```bash
python -m ingestion.main reconcile --run-id <uuid>
```

Behavior:

- creates `event_matches`,
- derives Sri Lanka May execution evidence from consolidation requests when no monthly execution tab exists and marks those snapshot rows as `derived_from_consolidation`,
- records weak/unmatched records,
- computes match coverage.

### refresh-views

```bash
python -m ingestion.main refresh-views
```

Behavior:

- refreshes materialized KPI and data-quality views in dependency order.

### report

```bash
python -m ingestion.main report --run-id <uuid> --output data/reports/latest-ingestion.md
```

Output:

- file participation summary,
- rows seen/loaded/skipped,
- validation issues by severity,
- reconciliation coverage,
- Pcode coverage,
- RCPA coverage,
- missing-FX warnings.
- provisional-FX warnings,
- confirmed-vs-estimated variance summary,
- BTU/BTC reconciliation warning summary,
- workflow governance status summary,
- intervention-type mix summary.
