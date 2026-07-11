from backend.app.services.ai.query_planner import plan_query


def test_query_planner_routes_sponsorship_and_contract_questions_to_doctor_context() -> None:
    plan = plan_query(
        (
            "Explain this doctor's sponsorship history, no-fee work, FMV, "
            "contracted value, and RCPA trend"
        ),
        "doctor_roi",
        40,
    )

    assert "doctor" in plan.topics
    assert {"doctorRoi", "budget", "dataQuality"}.issubset(plan.sections)


def test_query_planner_routes_territory_questions_to_territory_context() -> None:
    plan = plan_query("Which territories are underserved or overserved?", "territory", 40)

    assert "territory" in plan.topics
    assert "territory" in plan.sections
    assert "doctorRoi" in plan.sections


def test_query_planner_handles_spelling_errors_and_bad_phrasing() -> None:
    plan = plan_query("show me sponserd docter qadrant and rcpa problms", None, 40)

    assert "doctor" in plan.topics
    assert {"doctorRoi", "budget", "dataQuality"}.issubset(plan.sections)


def test_query_planner_uses_context_for_ambiguous_follow_up() -> None:
    plan = plan_query("why does this look wrong?", "territory", 40)

    assert "territory" in plan.topics
    assert "quality" in plan.topics
    assert "territory" in plan.sections


def test_query_planner_treats_loose_business_language_as_supported() -> None:
    plan = plan_query("debug bad money issues by area and doctors", None, 40)

    assert {"budget", "territory", "doctor", "quality"}.issubset(set(plan.topics))
    assert {"budget", "territory", "doctorRoi", "dataQuality"}.issubset(plan.sections)
