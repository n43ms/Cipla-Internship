# Feature Gate Policy

## Purpose

This policy prevents placeholder sponsorship, contract, accommodation, territory, and AI implementation before real source evidence exists.

## Forbidden Pre-Data Work

Do not build these until gates pass:

- sponsorship database tables,
- sponsorship normalizer with final business labels,
- doctor contract loader,
- territory assignment tables,
- accommodation model,
- sponsorship or territory materialized views,
- sponsorship or territory FastAPI routers,
- sponsorship or territory frontend pages,
- AI sponsorship or territory context,
- suggested prompts for unavailable sponsorship or territory data.

## Minimum Gates

### No Data Arrives

Allowed:

- data request package,
- source intake contract,
- generic profiler upgrades,
- raw-vs-cleaned comparison tooling,
- storage budget guard,
- onboarding playbook.

Blocked:

- all source-specific product features.

### Only Raw Consolidation Arrives

Allowed:

- profile file shape,
- check existing consolidation schema-map coverage,
- identify possible label columns,
- create a synthetic fixture from observed structure,
- write a post-data task file for proven loader/schema-map changes.

Blocked:

- final classifier rules,
- sponsorship persistence,
- sponsorship dashboard,
- AI sponsorship answers.

### Only Cleaned File Arrives

Allowed:

- profile as a presentation source,
- document business meaning,
- request raw recurring extract.

Blocked:

- recurring ingestion assumptions,
- database migrations based only on cleaned columns.

### Only RCPA Arrives

Allowed:

- profile RCPA shape,
- check P-code/month/brand coverage,
- estimate storage impact,
- verify whether current RCPA loader supports the shape.

Blocked:

- sponsorship outcome views without sponsorship facts.

### Only Doctor/Territory Mapping Arrives

Allowed:

- profile identity and hierarchy fields,
- document join keys,
- document missing identifiers.

Blocked:

- territory opportunity view,
- territory dashboard,
- AI territory context.

## Gate Review Checklist

- [ ] Real file is stored outside git.
- [ ] Source intake contract is filled.
- [ ] Profile report exists.
- [ ] Raw-vs-cleaned comparison exists when both variants are available.
- [ ] Stable keys are identified.
- [ ] Exact business labels are observed in source data.
- [ ] Storage impact is estimated.
- [ ] Synthetic fixture is created from observed shape.
- [ ] Failing tests exist before implementation.
- [ ] A new post-data task file exists for source-specific work.
