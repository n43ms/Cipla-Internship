from backend.app.services.ai.answer_policy import (
    association_only_text,
    confidence_for_context,
    dashboard_pointers_for_topics,
    deterministic_answer,
    evidence_refs_for_context,
    route_question,
)


def test_supported_topic_routing_and_unsupported_refusal() -> None:
    assert route_question("Where is execution risk highest?").supported is True

    unsupported = route_question("Who won the cricket match yesterday?")

    assert unsupported.supported is False
    assert "execution" in (unsupported.refusal or "").lower()


def test_answer_policy_is_lenient_for_typos_and_bad_phrasing() -> None:
    decision = route_question(
        "plz explain docotr sponserd hstory and qadrant roi problms",
    )

    assert decision.supported is True
    assert "doctor" in decision.topics


def test_answer_policy_uses_page_context_for_ambiguous_dashboard_questions() -> None:
    decision = route_question("why is this looking bad?", page_context="doctor_roi")

    assert decision.supported is True
    assert "doctor" in decision.topics
    assert "quality" in decision.topics


def test_answer_policy_allows_general_dashboard_questions_without_exact_keywords() -> None:
    decision = route_question("what should i look at in this dashboard?")

    assert decision.supported is True
    assert {"execution", "doctor", "quality"}.issubset(set(decision.topics))


def test_answer_policy_allows_messy_business_question_with_generic_external_word() -> None:
    decision = route_question("which doctors are winning roi and sponserhip?")

    assert decision.supported is True
    assert "doctor" in decision.topics


def test_confidence_downgrades_for_missing_or_weak_data() -> None:
    assert confidence_for_context({"limitations": [], "dataQualityFlags": []}) == "high"
    assert (
        confidence_for_context({"limitations": [], "dataQualityFlags": ["weak_match_coverage"]})
        == "medium"
    )
    assert (
        confidence_for_context(
            {"limitations": ["No rows match the selected filters."], "dataQualityFlags": []}
        )
        == "low"
    )


def test_deterministic_fallback_mentions_key_risk_metrics() -> None:
    response = deterministic_answer(
        "Summarize risk",
        {
            "execution": {"weakOrUnmatchedEvents": 7},
            "workflow": {"pendingReportCount": 3},
            "budget": {"spendWithoutPlanCount": 2},
            "doctorRoi": {"darkHorseCount": 4},
            "dataQuality": {"validationWarningCount": 1},
            "limitations": ["RCPA is historical baseline."],
            "dataQualityFlags": ["weak_match_coverage"],
        },
        reason="quota exhausted",
    )

    assert response["providerUsed"] == "deterministic"
    assert response["fallbackUsed"] is True
    assert "7 weak/unmatched" in response["answer"]
    assert response["confidence"] == "medium"
    assert response["limitations"][0].startswith("Gemini was not used")
    assert response["dashboardPointers"]
    assert any(pointer["page"] == "Data Quality" for pointer in response["dashboardPointers"])


def test_dashboard_pointers_follow_query_topics() -> None:
    pointers = dashboard_pointers_for_topics(["budget", "doctor"], {})

    assert any(pointer["page"] == "Budget" for pointer in pointers)
    assert any(pointer["page"] == "Doctor ROI" for pointer in pointers)
    assert all("value" not in pointer for pointer in pointers)


def test_answer_policy_rewrites_causal_uplift_language() -> None:
    safe = association_only_text("Sponsorship caused causal uplift in prescriptions.")

    assert "caused" not in safe.lower()
    assert "uplift" not in safe.lower()
    assert "associated" in safe.lower()
    assert "movement" in safe.lower()


def test_evidence_refs_include_territory_rows() -> None:
    refs = evidence_refs_for_context(
        {
            "territory": {
                "topTerritoryRows": [
                    {
                        "territoryName": "Colombo",
                        "opportunityLabel": "underserved",
                    }
                ]
            }
        }
    )

    assert refs[0]["section"] == "territory"
    assert refs[0]["label"] == "Colombo"
