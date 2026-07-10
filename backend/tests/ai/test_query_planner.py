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
    plan = plan_query("Which territories are underserved or self-serving?", "territory", 40)

    assert "territory" in plan.topics
    assert "territory" in plan.sections
    assert "doctorRoi" in plan.sections
