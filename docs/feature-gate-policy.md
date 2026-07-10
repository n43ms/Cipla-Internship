# Feature Gate Policy

## Purpose

This policy prevents brittle sponsorship, contract, territory, RCPA, and AI implementation. The received files are sufficient to begin profiling, but source-specific code still requires profile evidence and synthetic fixtures.

## Always Out Of Scope For This Phase

- SFTP automation.
- SharePoint folder polling.
- Automatic discovery across the CRM/data-lake report universe.
- Direct Power BI productionization.
- AI answers over raw workbook rows.
- Fake sponsorship or territory frontend pages before deterministic backend data exists.
- Internet-sourced FX fallback.

## Required Gates Before Source-Specific Implementation

| Gate | Required Evidence |
|---|---|
| File identity | Source manifest entry with point number, path, source type, raw/cleaned status, country or BU scope, and cadence |
| Profile complete | Workbook/table profile with header row, row count, sheet/table names, mapped fields, unknown fields, and sample values |
| Synthetic fixture | Tiny non-confidential fixture matching observed structure |
| Tests first | Failing tests for loader, classifier, reconciliation, or view behavior |
| Stable joins | Request/intervention ID, country/P-code, contract ID where present, RCPA month grain, and territory grain |
| Storage check | Database size/headroom reviewed before historical RCPA persistence |

## Sponsorship Classification Gate

Allowed only after raw labels are observed:

- `National Conference` -> sponsorship.
- `International Conference` -> sponsorship.
- `ERS` -> International evidence, not a standalone sponsorship root.
- `No Fee Agreement` -> no-fee engagement evidence.
- speaker, consultancy, advisory, honorarium -> paid/service engagement evidence.

## Doctor ROI Evidence Gate

Do not extend the Doctor ROI detail API/UI until these deterministic outputs exist:

- doctor-wise engagement facts,
- FMV amount,
- contracted amount,
- contract ID when present,
- BTC/BTU/expense facts,
- sponsorship/engagement classification,
- compact RCPA summaries,
- confidence/caveat metadata.

## Territory Gate

Territory analysis can use:

- Smart Contract `FS HQ`,
- RCPA `Location` and `PATCHNAME`,
- MSL `Location`, `Territory Id`, `Patch`, and `Patchsname`.

A standalone territory page remains blocked until source-level reconciliations prove the territory grain is reliable. Territory context can be added to Doctor ROI first.

## ExecAI Gate

ExecAI can be extended only after deterministic backend services return compact evidence. It must:

- use evidence references,
- cap returned rows,
- avoid causal uplift claims,
- use association language,
- never send raw workbook rows to the model.

## Gate Review Checklist

- [ ] Source manifest exists.
- [ ] Profile report exists.
- [ ] Raw-vs-cleaned comparison exists when applicable.
- [ ] Synthetic fixture exists.
- [ ] Failing tests exist before implementation.
- [ ] Storage impact is reviewed for historical RCPA.
- [ ] FX uses company-provided rates only.
- [ ] No AI context is built before backend evidence exists.
