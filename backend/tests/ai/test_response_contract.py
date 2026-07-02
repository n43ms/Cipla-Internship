import json

import pytest

from backend.app.services.ai.response_contract import (
    AiResponseContractError,
    parse_structured_answer,
)


def test_parse_structured_answer_validates_evidence_paths() -> None:
    context = {
        "execution": {"weakOrUnmatchedEvents": 4},
        "limitations": [],
        "dataQualityFlags": [],
    }

    parsed = parse_structured_answer(
        json.dumps(
            {
                "markdownAnswer": "**Risk** is weak matching.",
                "evidenceRefs": [
                    {
                        "section": "execution",
                        "label": "Weak rows",
                    "value": 4,
                    "sourcePath": "execution.weakOrUnmatchedEvents",
                },
                {
                    "section": "execution",
                    "label": "Bad row",
                        "value": 999,
                        "sourcePath": "execution.missing",
                    },
                ],
                "assumptions": [],
                "limitations": [],
                "confidence": "medium",
            }
        ),
        context,
    )

    assert parsed["answer"] == "Risk is weak matching."
    assert parsed["answerMarkdown"] == "**Risk** is weak matching."
    assert parsed["evidenceRefs"] == [
        {
            "section": "Execution",
            "label": "Weak rows",
            "value": 4,
            "sourcePath": "execution.weakOrUnmatchedEvents",
        }
    ]
    assert "1 Gemini evidence reference" in parsed["limitations"][0]


def test_parse_structured_answer_rewrites_internal_paths_to_dashboard_copy() -> None:
    context = {
        "workflow": {"ownerStageCounts": {"manager": 2}},
        "execution": {"eventRows": [{"eventName": "CME"}], "weakOrUnmatchedEvents": 4},
        "limitations": [],
        "dataQualityFlags": [],
    }

    parsed = parse_structured_answer(
        json.dumps(
            {
                "markdownAnswer": (
                    "Workflow Bottlenecks: Review workflow.ownerStageCounts. "
                    "Execution Gaps: Refer to execution.eventRows and "
                    "execution.weakOrUnmatchedEvents."
                ),
                "evidenceRefs": [],
                "assumptions": [],
                "limitations": ["Checked workflow.ownerStageCounts only."],
                "confidence": "medium",
            }
        ),
        context,
    )

    assert "workflow.ownerStageCounts" not in parsed["answerMarkdown"]
    assert "execution.eventRows" not in parsed["answerMarkdown"]
    assert "execution.weakOrUnmatchedEvents" not in parsed["answerMarkdown"]
    assert "Workflow status cards" in parsed["answerMarkdown"]
    assert "Execution event matrix table" in parsed["answerMarkdown"]
    assert "Execution KPI cards" in parsed["answerMarkdown"]
    assert "Workflow status cards" in parsed["limitations"][0]


def test_parse_structured_answer_rejects_malformed_json() -> None:
    with pytest.raises(AiResponseContractError):
        parse_structured_answer("not json", {"limitations": [], "dataQualityFlags": []})
