from __future__ import annotations

import json
from typing import Any

from fastapi.encoders import jsonable_encoder
from sqlalchemy.orm import Session

from backend.app.repositories.doctor_repository import DoctorRepository
from backend.app.services.ai.query_planner import QueryPlan
from backend.app.services.budget_service import BudgetService
from backend.app.services.data_quality_service import DataQualityService
from backend.app.services.doctor_service import DoctorService
from backend.app.services.execution_service import ExecutionService
from backend.app.services.intervention_service import InterventionService
from backend.app.services.workflow_service import WorkflowService

DEFAULT_MAX_CONTEXT_CHARS = 24000
DEFAULT_ROW_LIMIT = 40
MAX_ROW_LIMIT = 100
TRIMMED_ROW_LIMIT = 10


def build_compact_context(
    session: Session,
    *,
    question: str,
    page_context: str | None = None,
    filters: dict[str, Any] | None = None,
    max_chars: int = DEFAULT_MAX_CONTEXT_CHARS,
    row_limit: int = DEFAULT_ROW_LIMIT,
    query_plan: QueryPlan | None = None,
) -> dict[str, Any]:
    """Build a detailed but bounded AI context from existing dashboard services."""

    safe_filters = _normalize_filters(filters or {})
    effective_row_limit = _bounded_row_limit(row_limit)
    detail_row_limit = _bounded_row_limit(
        query_plan.detail_limit if query_plan else effective_row_limit
    )
    broad_row_limit = _bounded_row_limit(
        query_plan.broad_limit if query_plan else effective_row_limit
    )
    sections = (
        query_plan.sections
        if query_plan
        else {"execution", "workflow", "interventions", "budget", "doctorRoi", "dataQuality"}
    )
    country = _string_or_none(safe_filters.get("country"))
    month = _string_or_none(safe_filters.get("month"))
    include_out_of_scope = bool(
        safe_filters.get("includeOutOfScope") or safe_filters.get("include_out_of_scope")
    )

    execution: dict[str, Any] = {}
    execution_events: dict[str, Any] = {}
    workflow: dict[str, Any] = {}
    workflow_requests: dict[str, Any] = {}
    interventions: dict[str, Any] = {}
    budget: dict[str, Any] = {}
    doctor: dict[str, Any] = {}
    quality: dict[str, Any] = {}
    doctor_details: list[dict[str, Any]] = []

    if "execution" in sections:
        execution_service = ExecutionService(session)
        execution = _dump(execution_service.summary(country, month, include_out_of_scope))
        execution_events = _dump(
            execution_service.events(
                country=country,
                month=month,
                page=1,
                page_size=detail_row_limit,
                include_out_of_scope=include_out_of_scope,
            )
        )
    if "workflow" in sections:
        workflow_service = WorkflowService(session)
        workflow = _dump(workflow_service.summary(country, month, None, include_out_of_scope))
        workflow_requests = _dump(
            workflow_service.requests(
                country=country,
                month=month,
                intervention_type=None,
                workflow_status=None,
                page=1,
                page_size=detail_row_limit,
                include_out_of_scope=include_out_of_scope,
            )
        )
    if "interventions" in sections:
        interventions = _dump(
            InterventionService(session).mix(country, month, include_out_of_scope)
        )
    if "budget" in sections:
        budget = _dump(
            BudgetService(session).summary(
                country=country,
                month=month,
                include_out_of_scope=include_out_of_scope,
                page=1,
                page_size=detail_row_limit,
            )
        )
    if "doctorRoi" in sections:
        doctor = _dump(
            DoctorService(session).roi(
                country=country,
                roi_segment=_string_or_none(safe_filters.get("roiSegment")),
                quadrant=None,
                month_start=month,
                month_end=month,
                brand=_string_or_none(safe_filters.get("brand")),
                speciality=_string_or_none(safe_filters.get("speciality")),
                doctor_class=_string_or_none(safe_filters.get("doctorClass")),
                include_out_of_scope=include_out_of_scope,
                page=1,
                page_size=detail_row_limit,
            )
        )
        if query_plan and query_plan.doctor_search_terms:
            doctor_details = _doctor_detail_evidence(
                session,
                country=country,
                terms=query_plan.doctor_search_terms,
            )
    if "dataQuality" in sections:
        quality = _dump(DataQualityService(session).summary())

    context = {
        "question": question,
        "questionTopicHint": page_context or "dashboard",
        "filters": safe_filters,
        "contextPolicy": {
            "rawWorkbookRowsIncluded": False,
            "fullTablesIncluded": False,
            "rowLimit": detail_row_limit,
            "broadRowLimit": broad_row_limit,
            "topN": detail_row_limit,
            "maxCharacters": max_chars,
            "specificNamesAmountsPcodesAndCurrenciesIncluded": True,
            "detailStrategy": (
                "query_planned_bounded_service_rows_plus_summaries"
                if query_plan
                else "bounded_service_rows_plus_summaries"
            ),
            "queryTopics": query_plan.topics if query_plan else [],
            "requestedSections": sorted(sections),
            "doctorSearchTerms": query_plan.doctor_search_terms if query_plan else [],
        },
    }
    if execution:
        context["execution"] = (
            _pick(
                execution,
                [
                    "plannedEvents",
                    "matchedEvents",
                    "weakOrUnmatchedEvents",
                    "executedEvents",
                    "actionDueEvents",
                    "plannedEventsWithExecutedEvidence",
                    "plannedEventsWithActionDueEvidence",
                    "executedSnapshotCount",
                    "actionDueSnapshotCount",
                    "plannedHcps",
                    "engagedHcps",
                    "matchedEngagedHcps",
                    "rawEngagedHcps",
                    "matchCoverage",
                    "eventExecutionRate",
                    "hcpExecutionRate",
                    "snapshotSourceCounts",
                    "primaryScope",
                    "scopeStatuses",
                    "scopeReasons",
                ],
            )
            | {
            "eventRows": _top_rows(
                execution_events.get("rows", []),
                [
                    "sourceType",
                    "eventName",
                    "eventType",
                    "country",
                    "month",
                    "matchStatus",
                    "confidence",
                    "candidateMatch",
                    "plannedHcps",
                    "engagedHcps",
                    "executionStatus",
                    "snapshotSource",
                    "sourceDerivationNote",
                    "unmatchedReasonCode",
                    "unmatchedReasonDetail",
                    "isPrimaryPhase4Scope",
                    "scopeStatus",
                    "scopeReason",
                    "matchGrain",
                    "sourceReferences",
                ],
                detail_row_limit,
            ),
            "eventRowTotal": execution_events.get("total"),
            }
        )
    if workflow:
        context["workflow"] = (
            _pick(
                workflow,
                [
                    "pendingRequestCount",
                    "pendingReportCount",
                    "reportsSentForCorrection",
                    "reportsApproved",
                    "expenseSubmittedCoverage",
                    "expenseConfirmedCoverage",
                    "requestApprovalCounts",
                    "requestConfirmationCounts",
                    "postApprovalCounts",
                    "postConfirmationCounts",
                    "ownerStageCounts",
                    "primaryScope",
                    "scopeStatuses",
                    "scopeReasons",
                ],
            )
            | {
            "requestRows": _top_rows(
                workflow_requests.get("rows", []),
                [
                    "reqId",
                    "country",
                    "month",
                    "repName",
                    "interventionType",
                    "requestApprovalStatus",
                    "requestConfirmationStatus",
                    "postApprovalStatus",
                    "postConfirmationStatus",
                    "currentOwnerStage",
                    "expenseSubmittedDate",
                    "expenseConfirmedDate",
                    "isPrimaryPhase4Scope",
                    "scopeStatus",
                    "scopeReason",
                ],
                detail_row_limit,
            ),
            "requestRowTotal": workflow_requests.get("total"),
            }
        )
    if interventions:
        context["interventions"] = {
            "topRows": _top_rows(
                interventions.get("rows", []),
                [
                    "interventionType",
                    "interventionSubType",
                    "requestCount",
                    "executedCount",
                    "executedRequestCount",
                    "matchedRequestCount",
                    "executedSnapshotCount",
                    "actionDueCount",
                    "actionDueRequestCount",
                    "actionDueSnapshotCount",
                    "matchedWithoutExecutionCount",
                    "approvedCount",
                    "reportPendingCount",
                    "confirmedContractedAmount",
                    "directHcpBtuSpend",
                    "overheadBtcSpend",
                    "totalActualSpend",
                    "fxRateStatus",
                ],
                detail_row_limit,
            )
        }
    if budget:
        context["budget"] = (
            _pick(
                budget,
                [
                    "plannedBudgetUsd",
                    "estimatedInterventionLocal",
                    "estimatedInterventionUsd",
                    "confirmedContractedAmountLocal",
                    "confirmedContractedAmountUsd",
                    "confirmedVsEstimatedVarianceLocal",
                    "confirmedVsEstimatedVarianceUsd",
                    "directHcpBtuSpendLocal",
                    "directHcpBtuSpendUsd",
                    "overheadBtcSpendLocal",
                    "overheadBtcSpendUsd",
                    "actualTotalSpendLocal",
                    "actualTotalSpendUsd",
                    "associationAmountLocal",
                    "unspentGapUsd",
                    "overrunAmountUsd",
                    "planWithoutSpendCount",
                    "spendWithoutPlanCount",
                    "missingFxCount",
                    "provisionalFxCount",
                    "btuBtcReconciliationIssueCount",
                    "currencyCodes",
                    "fxRateStatuses",
                    "localTotalsByCurrency",
                ],
            )
            | {
            "topGapRows": _top_rows(
                budget.get("rows", []),
                [
                    "eventName",
                    "eventType",
                    "country",
                    "month",
                    "matchStatus",
                    "plannedBudgetUsd",
                    "estimatedInterventionLocal",
                    "confirmedContractedAmountLocal",
                    "actualTotalExpenseLocal",
                    "directHcpBtuSpendLocal",
                    "overheadBtcSpendLocal",
                    "actualTotalExpenseUsd",
                    "unspentGapUsd",
                    "overrunAmountUsd",
                    "currencyCode",
                    "fxRateStatus",
                    "btuBtcReconciliationStatus",
                    "spendWithoutPlan",
                    "planWithoutSpend",
                    "rowKind",
                    "scopeStatus",
                ],
                detail_row_limit,
            ),
            "gapRowTotal": budget.get("total"),
            }
        )
    if doctor:
        context["doctorRoi"] = (
            _pick(
                doctor,
                [
                    "total",
                    "darkHorseCount",
                    "noRcpaCount",
                    "missingFxCount",
                    "provisionalFxCount",
                    "quadrantCounts",
                    "segmentCounts",
                    "brandFilterMode",
                    "periodFilterMode",
                ],
            )
            | {
            "topDoctorOpportunityRows": _doctor_rows(doctor.get("rows", []), detail_row_limit),
            "matchedDoctorDetails": doctor_details,
            }
        )
    if quality:
        context["dataQuality"] = (
            _pick(
                quality,
                [
                    "loadedFileCount",
                    "sourceFileCount",
                    "rowsLoaded",
                    "rowsSkipped",
                    "validationErrorCount",
                    "validationWarningCount",
                    "matchCoverage",
                    "pcodeCoverage",
                    "rcpaCoverage",
                    "missingFxCount",
                    "provisionalFxCount",
                    "unmatchedEventCount",
                    "staleIngestion",
                    "officialLkrRateToUsd",
                ],
            )
            | {
            "unmatchedBySource": _top_rows(
                quality.get("unmatchedBySource", []),
                ["sourceType", "reasonCode", "recordCount"],
                broad_row_limit,
            ),
            "fxQuality": _top_rows(
                quality.get("fxQuality", []),
                ["currencyCode", "rateStatus", "rateToUsd", "source", "rowCount"],
                broad_row_limit,
            ),
            }
        )
    context["limitations"] = _topic_limitations(
        _collect_limitations(
            execution,
            execution_events,
            workflow,
            workflow_requests,
            interventions,
            budget,
            doctor,
            quality,
        ),
        query_plan.topics if query_plan else [],
    )
    context["dataQualityFlags"] = _collect_flags(
            execution,
            execution_events,
            workflow,
            workflow_requests,
            interventions,
            budget,
            doctor,
            quality,
        )
    return _fit_context(context, max_chars=max_chars)


def context_scope(context: dict[str, Any]) -> dict[str, Any]:
    return {
        "pageContext": context.get("questionTopicHint", "dashboard"),
        "filters": context.get("filters", {}),
        "topN": context.get("contextPolicy", {}).get("rowLimit", DEFAULT_ROW_LIMIT),
        "maxCharacters": context.get("contextPolicy", {}).get(
            "maxCharacters",
            DEFAULT_MAX_CONTEXT_CHARS,
        ),
        "sections": [
            key
            for key in (
                "execution",
                "workflow",
                "interventions",
                "budget",
                "doctorRoi",
                "dataQuality",
            )
            if key in context
        ],
    }


def _dump(value: Any) -> dict[str, Any]:
    if hasattr(value, "model_dump"):
        return jsonable_encoder(value, by_alias=True)
    return jsonable_encoder(value)


def _normalize_filters(filters: dict[str, Any]) -> dict[str, Any]:
    allowed = {
        "country",
        "month",
        "includeOutOfScope",
        "include_out_of_scope",
        "brand",
        "speciality",
        "doctorClass",
        "roiSegment",
    }
    return {
        key: value
        for key, value in filters.items()
        if key in allowed and value not in (None, "")
    }


def _string_or_none(value: Any) -> str | None:
    return str(value) if value not in (None, "") else None


def _pick(data: dict[str, Any], keys: list[str]) -> dict[str, Any]:
    return {key: data.get(key) for key in keys if key in data}


def _top_rows(
    rows: Any,
    keys: list[str],
    limit: int = DEFAULT_ROW_LIMIT,
) -> list[dict[str, Any]]:
    if not isinstance(rows, list):
        return []
    return [_pick(row, keys) for row in rows[:limit] if isinstance(row, dict)]


def _doctor_rows(rows: Any, limit: int = DEFAULT_ROW_LIMIT) -> list[dict[str, Any]]:
    if not isinstance(rows, list):
        return []
    result = []
    for row in rows[:limit]:
        if not isinstance(row, dict):
            continue
        result.append(
            {
                "doctorName": row.get("doctorName"),
                "pcodeNormalized": row.get("pcodeNormalized"),
                "countryName": row.get("countryName"),
                "speciality": row.get("speciality"),
                "doctorClass": row.get("doctorClass"),
                "activeStatus": row.get("activeStatus"),
                "engagementCount": row.get("engagementCount"),
                "firstEngagementDate": row.get("firstEngagementDate"),
                "lastEngagementDate": row.get("lastEngagementDate"),
                "directHcpBtuSpendUsd": row.get("directHcpBtuSpendUsd"),
                "overheadBtcSpendUsd": row.get("overheadBtcSpendUsd"),
                "totalRoiSpendUsd": row.get("totalRoiSpendUsd"),
                "ciplaPrescriptionQty": row.get("ciplaPrescriptionQty"),
                "competitorPrescriptionQty": row.get("competitorPrescriptionQty"),
                "totalPrescriptionQty": row.get("totalPrescriptionQty"),
                "ciplaShareQty": row.get("ciplaShareQty"),
                "spendPerCiplaPrescriptionUsd": row.get("spendPerCiplaPrescriptionUsd"),
                "roiSegment": row.get("roiSegment"),
                "quadrantX": row.get("quadrantX"),
                "quadrantY": row.get("quadrantY"),
                "quadrantLabel": row.get("quadrantLabel"),
                "darkHorseFlag": row.get("darkHorseFlag"),
                "darkHorseUnengagedFlag": row.get("darkHorseUnengagedFlag"),
                "highValueEngagedFlag": row.get("highValueEngagedFlag"),
                "hasRcpa": row.get("hasRcpa"),
                "hasMissingFx": row.get("hasMissingFx"),
                "hasProvisionalFx": row.get("hasProvisionalFx"),
                "rcpaFirstMonth": row.get("rcpaFirstMonth"),
                "rcpaLastMonth": row.get("rcpaLastMonth"),
                "rcpaMonthCount": row.get("rcpaMonthCount"),
            }
        )
    return result


def _doctor_detail_evidence(
    session: Session,
    *,
    country: str | None,
    terms: list[str],
) -> list[dict[str, Any]]:
    repository = DoctorRepository(session)
    result: list[dict[str, Any]] = []
    seen: set[tuple[str, str]] = set()
    for term in terms[:4]:
        for row in repository.search_doctors(country=country, search=term, limit=3):
            country_code = str(row.get("country_code") or "")
            pcode = str(row.get("pcode_normalized") or "")
            if not country_code or not pcode or (country_code.lower(), pcode) in seen:
                continue
            seen.add((country_code.lower(), pcode))
            result.append(
                {
                    "matchedTerm": term,
                    "profile": _doctor_profile_evidence(row),
                    "engagementHistory": _top_rows(
                        _dump(repository.engagement_history(country_code, pcode)),
                        [
                            "request_id",
                            "intervention_name",
                            "intervention_type",
                            "month",
                            "actual_intervention_date",
                            "total_roi_spend_usd",
                            "fx_rate_status",
                        ],
                        8,
                    ),
                    "prescriptionTrend": _top_rows(
                        _dump(repository.prescription_trend(country_code, pcode))[-12:],
                        [
                            "month",
                            "cipla_prescription_qty",
                            "competitor_prescription_qty",
                            "total_prescription_qty",
                        ],
                        12,
                    ),
                    "brandMix": _top_rows(
                        _dump(repository.brand_mix(country_code, pcode)),
                        [
                            "brand_group",
                            "own_or_competitor",
                            "prescription_qty",
                            "prescription_value_local",
                        ],
                        8,
                    ),
                }
            )
    return result[:5]


def _doctor_profile_evidence(row: dict[str, Any]) -> dict[str, Any]:
    return {
        "countryCode": row.get("country_code"),
        "countryName": row.get("country_name"),
        "pcodeNormalized": row.get("pcode_normalized"),
        "doctorName": row.get("doctor_name"),
        "speciality": row.get("speciality"),
        "doctorClass": row.get("doctor_class"),
        "activeStatus": row.get("active_status"),
        "engagementCount": row.get("engagement_count"),
        "firstEngagementDate": row.get("first_engagement_date"),
        "lastEngagementDate": row.get("last_engagement_date"),
        "directHcpBtuSpendUsd": row.get("direct_hcp_btu_spend_usd"),
        "overheadBtcSpendUsd": row.get("overhead_btc_spend_usd"),
        "totalRoiSpendUsd": row.get("total_roi_spend_usd"),
        "ciplaPrescriptionQty": row.get("cipla_prescription_qty"),
        "competitorPrescriptionQty": row.get("competitor_prescription_qty"),
        "totalPrescriptionQty": row.get("total_prescription_qty"),
        "ciplaShareQty": row.get("cipla_share_qty"),
        "spendPerCiplaPrescriptionUsd": row.get("spend_per_cipla_prescription_usd"),
        "roiSegment": row.get("roi_segment"),
        "quadrantLabel": row.get("quadrant_label"),
        "darkHorseFlag": row.get("dark_horse_flag"),
        "darkHorseUnengagedFlag": row.get("dark_horse_unengaged_flag"),
        "highValueEngagedFlag": row.get("high_value_engaged_flag"),
        "hasRcpa": row.get("has_rcpa"),
        "hasMissingFx": row.get("has_missing_fx"),
        "hasProvisionalFx": row.get("has_provisional_fx"),
        "rcpaFirstMonth": row.get("rcpa_first_month"),
        "rcpaLastMonth": row.get("rcpa_last_month"),
        "rcpaMonthCount": row.get("rcpa_month_count"),
    }


def _bounded_row_limit(row_limit: int) -> int:
    return max(5, min(int(row_limit or DEFAULT_ROW_LIMIT), MAX_ROW_LIMIT))


def _topic_limitations(limitations: list[str], topics: list[str]) -> list[str]:
    if not topics:
        return limitations[:8]
    keywords_by_topic = {
        "execution": ("execution", "match", "planner", "snapshot", "scope", "event"),
        "workflow": ("workflow", "approval", "confirmation", "report", "request"),
        "intervention": ("intervention", "program", "type", "request", "report"),
        "budget": ("budget", "spend", "expense", "fx", "currency", "btu", "btc", "amount"),
        "doctor": ("doctor", "hcp", "pcode", "rcpa", "prescription", "roi", "fx", "spend"),
        "quality": (
            "quality",
            "validation",
            "ingestion",
            "source",
            "coverage",
            "missing",
            "unmatched",
        ),
    }
    selected_keywords: set[str] = set()
    for topic in topics:
        selected_keywords.update(keywords_by_topic.get(topic, ()))
    filtered = [
        limitation
        for limitation in limitations
        if any(keyword in limitation.lower() for keyword in selected_keywords)
    ]
    return (filtered or limitations[:3])[:6]


def _collect_limitations(*payloads: dict[str, Any]) -> list[str]:
    limitations: list[str] = []
    for payload in payloads:
        meta = payload.get("meta") if isinstance(payload, dict) else {}
        if isinstance(meta, dict):
            limitations.extend(str(item) for item in meta.get("limitations", []) if item)
            limitations.extend(str(item) for item in meta.get("sourceDerivationNotes", []) if item)
    return list(dict.fromkeys(limitations))


def _collect_flags(*payloads: dict[str, Any]) -> list[str]:
    flags: list[str] = []
    for payload in payloads:
        meta = payload.get("meta") if isinstance(payload, dict) else {}
        if isinstance(meta, dict):
            flags.extend(str(item) for item in meta.get("dataQualityFlags", []) if item)
    return list(dict.fromkeys(flags))


def _fit_context(context: dict[str, Any], max_chars: int) -> dict[str, Any]:
    if _encoded_len(context) <= max_chars:
        return context

    trimmed = dict(context)
    if "execution" in context:
        trimmed["execution"] = dict(context.get("execution", {})) | {
            "eventRows": context.get("execution", {}).get("eventRows", [])[:TRIMMED_ROW_LIMIT]
        }
    if "workflow" in context:
        trimmed["workflow"] = dict(context.get("workflow", {})) | {
            "requestRows": context.get("workflow", {}).get("requestRows", [])[:TRIMMED_ROW_LIMIT]
        }
    if "budget" in context:
        trimmed["budget"] = dict(context.get("budget", {})) | {
            "topGapRows": context.get("budget", {}).get("topGapRows", [])[:TRIMMED_ROW_LIMIT]
        }
    if "doctorRoi" in context:
        trimmed["doctorRoi"] = dict(context.get("doctorRoi", {})) | {
            "topDoctorOpportunityRows": context.get("doctorRoi", {}).get(
                "topDoctorOpportunityRows",
                [],
            )[:TRIMMED_ROW_LIMIT],
            "matchedDoctorDetails": context.get("doctorRoi", {}).get(
                "matchedDoctorDetails",
                [],
            )[:2],
        }
    if "interventions" in context:
        trimmed["interventions"] = {
            "topRows": context.get("interventions", {}).get("topRows", [])[:TRIMMED_ROW_LIMIT]
        }
    trimmed["limitations"] = context.get("limitations", [])[:8]
    trimmed["contextPolicy"] = dict(context.get("contextPolicy", {})) | {
        "truncated": True,
        "trimmedRowLimit": TRIMMED_ROW_LIMIT,
    }
    if _encoded_len(trimmed) <= max_chars:
        return trimmed

    compact = {
        key: value
        for key, value in trimmed.items()
        if key
        in {
            "question",
            "questionTopicHint",
            "filters",
            "execution",
            "workflow",
            "interventions",
            "budget",
            "doctorRoi",
            "dataQuality",
            "limitations",
            "dataQualityFlags",
            "contextPolicy",
        }
    }
    if "execution" in compact:
        compact["execution"].pop("eventRows", None)
    if "workflow" in compact:
        compact["workflow"].pop("requestRows", None)
    if "budget" in compact:
        compact["budget"].pop("topGapRows", None)
    if "doctorRoi" in compact:
        compact["doctorRoi"].pop("topDoctorOpportunityRows", None)
        compact["doctorRoi"].pop("matchedDoctorDetails", None)
    compact["contextPolicy"] = dict(compact["contextPolicy"]) | {
        "truncatedToSummariesOnly": True
    }
    return compact


def _encoded_len(payload: dict[str, Any]) -> int:
    return len(json.dumps(payload, sort_keys=True, default=str))
