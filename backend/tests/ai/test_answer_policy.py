from backend.app.services.ai.answer_policy import (
    confidence_for_context,
    dashboard_pointers_for_topics,
    deterministic_answer,
    route_question,
)


def test_supported_topic_routing_and_unsupported_refusal() -> None:
    assert route_question("Where is execution risk highest?").supported is True

    unsupported = route_question("Who won the cricket match yesterday?")

    assert unsupported.supported is False
    assert "execution" in (unsupported.refusal or "").lower()


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
