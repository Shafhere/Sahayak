
"""Exercise actual Streamlit reruns, with the external pipeline replaced."""
from unittest.mock import Mock
from pathlib import Path

from streamlit.testing.v1 import AppTest

from app.schemas.citizen import CitizenProfile
from app.schemas.plan import ActionPlan, CriticVerdict, TimelineStep
from app.workflows import graph


def app():
    test = AppTest.from_file(
        Path(__file__).resolve().parents[1] / "app/ui/streamlit_app.py",
        default_timeout=15,
    )
    test.session_state["user"] = {"full_name": "Test"}
    test.session_state["page"] = "mentor"
    return test.run()


def result(passed=True):
    return {
        "profile": CitizenProfile(mode="mentor"),
        "plan": ActionPlan(
            greeting="Your next step",
            next_steps=["Compare courses"],
            timeline=[TimelineStep(step="Explore interests")],
        ),
        "verdict": CriticVerdict(
            passed=passed,
            errors=[] if passed else ["Unsupported"],
        ),
    }


def test_mentor_request_renders_result_without_followup(monkeypatch):
    pipeline = Mock(return_value=result())
    monkeypatch.setattr(graph, "run_pipeline", pipeline)

    test = app()
    test.text_area(key="mentor_q").input("Finished school").run()
    test.button(key="mentor_btn").click().run()

    assert not test.exception
    pipeline.assert_called_once()
    assert pipeline.call_args.args[0] == "Finished school"
    assert pipeline.call_args.kwargs["mode"] == "mentor"
    assert "followup_answers" not in pipeline.call_args.kwargs
    assert not any(b.label == "Submit Answers" for b in test.button)
    assert any("Your next step" in m.value for m in test.markdown)


def test_failed_plan_is_not_rendered(monkeypatch):
    monkeypatch.setattr(graph, "run_pipeline", Mock(return_value=result(False)))

    test = app()
    test.text_area(key="mentor_q").input("Help me").run()
    test.button(key="mentor_btn").click().run()

    assert test.warning
    assert not test.exception
    assert not any("Your next step" in m.value for m in test.markdown)


def test_empty_mentor_result_has_no_zero_dashboard(monkeypatch):
    response = result()
    response["plan"] = ActionPlan(
        next_steps=["Tell me your subjects and interests."]
    )
    monkeypatch.setattr(graph, "run_pipeline", Mock(return_value=response))

    test = app()
    test.text_area(key="mentor_q").input(
        "I finished 12th, I am confused."
    ).run()
    test.button(key="mentor_btn").click().run()

    assert not test.exception
    assert any("subjects and interests" in i.value for i in test.info)
    assert not any(
        "stat-value" in m.value and '<p class="stat-value">0' in m.value
        for m in test.markdown
    )
    assert not any(
        "Here is your personalized plan" in m.value
        for m in test.markdown
    )


def test_service_quota_failure_shows_warning(monkeypatch):
    pipeline = Mock(
        side_effect=RuntimeError(
            "The language service is busy or its quota has been reached. "
            "Please retry later."
        )
    )
    monkeypatch.setattr(graph, "run_pipeline", pipeline)

    test = app()
    test.text_area(key="mentor_q").input("Finished school").run()
    test.button(key="mentor_btn").click().run()

    assert not test.exception
    assert test.warning
    pipeline.assert_called_once()
    assert pipeline.call_args.args[0] == "Finished school"
    assert pipeline.call_args.kwargs["mode"] == "mentor"
