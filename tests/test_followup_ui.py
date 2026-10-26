"""Exercise actual Streamlit reruns, with the external pipeline replaced."""
from unittest.mock import Mock
from pathlib import Path

from streamlit.testing.v1 import AppTest

from app.schemas.citizen import CitizenProfile
from app.schemas.plan import ActionPlan, CriticVerdict, TimelineStep
from app.workflows import graph


def app():
    test = AppTest.from_file(Path(__file__).resolve().parents[1] / "app/ui/streamlit_app.py", default_timeout=15)
    test.session_state["user"] = {"full_name": "Test"}
    test.session_state["page"] = "mentor"
    return test.run()


def result(passed=True):
    return {"profile": CitizenProfile(mode="mentor"),
            "plan": ActionPlan(greeting="Your next step", next_steps=["Compare courses"],
                               timeline=[TimelineStep(step="Explore interests")]),
            "verdict": CriticVerdict(passed=passed, errors=[] if passed else ["Unsupported"])}


def test_followup_submission_renders_result_immediately(monkeypatch):
    pipeline = Mock(side_effect=[
        {"needs_followup": True, "followup_questions": ["What interests you?"]}, result()])
    monkeypatch.setattr(graph, "run_pipeline", pipeline)
    test = app()
    test.text_area(key="mentor_q").input("Finished school").run()
    test.button(key="mentor_btn").click().run()
    assert not test.exception
    assert test.session_state["followup"] is not None
    test.text_input[0].input("Mathematics")
    next(b for b in test.button if b.label == "Submit Answers").click().run()
    assert not test.exception
    assert test.session_state["followup"] is None
    assert pipeline.call_args.kwargs["followup_answers"] == {"What interests you?": "Mathematics"}
    assert pipeline.call_args.kwargs["mode"] == "mentor"
    assert any("Your next step" in m.value for m in test.markdown)


def test_empty_answer_does_not_advance(monkeypatch):
    pipeline = Mock(return_value={"needs_followup": True, "followup_questions": ["Interests?"]})
    monkeypatch.setattr(graph, "run_pipeline", pipeline)
    test = app()
    test.text_area(key="mentor_q").input("Help me").run()
    test.button(key="mentor_btn").click().run()
    next(b for b in test.button if b.label == "Submit Answers").click().run()
    assert pipeline.call_count == 1
    assert test.warning and not test.exception


def test_failed_plan_is_not_rendered(monkeypatch):
    monkeypatch.setattr(graph, "run_pipeline", Mock(return_value=result(False)))
    test = app()
    test.text_area(key="mentor_q").input("Help me").run()
    test.button(key="mentor_btn").click().run()
    assert test.warning and not test.exception
    assert not any("Your next step" in m.value for m in test.markdown)


def test_empty_mentor_result_has_no_zero_dashboard(monkeypatch):
    response = result()
    response["plan"] = ActionPlan(next_steps=["Tell me your subjects and interests."])
    monkeypatch.setattr(graph, "run_pipeline", Mock(return_value=response))
    test = app()
    test.text_area(key="mentor_q").input("I finished 12th, I am confused.").run()
    test.button(key="mentor_btn").click().run()
    assert not test.exception
    assert any("subjects and interests" in i.value for i in test.info)
    assert not any("stat-value" in m.value and '<p class="stat-value">0' in m.value for m in test.markdown)
    assert not any("Here is your personalized plan" in m.value for m in test.markdown)

def test_service_quota_failure_keeps_followup_answers(monkeypatch):
    pipeline=Mock(side_effect=[{'needs_followup':True,'followup_questions':['Interests?']},RuntimeError('The language service is busy or its quota has been reached. Please retry later.')])
    monkeypatch.setattr(graph,'run_pipeline',pipeline)
    test=app()
    test.text_area(key='mentor_q').input('Finished school').run()
    test.button(key='mentor_btn').click().run()
    test.text_input[0].input('Biology')
    next(b for b in test.button if b.label=='Submit Answers').click().run()
    assert not test.exception and test.warning
    assert test.session_state['followup'] is not None
    assert test.text_input[0].value=='Biology'
