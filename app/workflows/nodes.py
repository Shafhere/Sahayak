
"""Node functions for the Sahayak LangGraph workflow.

Each node reads from SahayakState, calls an agent, and returns a dict of updates.
"""

from app.workflows.state import SahayakState
from app.agents.understanding import understand
from app.agents.research import research
from app.agents.planning import plan
from app.agents.critic import critique
from app.agents.replanner import replan


def understand_node(state: SahayakState) -> dict:
    """Extract a structured citizen profile from natural language."""
    raw_input = state.get("raw_input", "").strip()

    if not raw_input:
        raise ValueError("User input cannot be empty.")

    profile = understand(
        raw_input,
        requested_mode=state.get("requested_mode"),
        followup_answers=state.get("followup_answers") or {},
    )

    return {
        "profile": profile,
        "mode": profile.mode,
        "iterations": 0,
        "needs_followup": getattr(profile, "needs_followup", False),
        "followup_questions": getattr(profile, "followup_questions", []),
    }


def research_node(state: SahayakState) -> dict:
    """Retrieve relevant evidence for the citizen's profile."""
    profile = state.get("profile")

    if profile is None:
        return {"research": None}

    research_result = research(profile)
    return {"research": research_result}


def plan_node(state: SahayakState) -> dict:
    """Generate the initial action plan."""
    profile = state.get("profile")
    research_result = state.get("research")

    if profile is None or research_result is None:
        return {"plan": None}

    action_plan = plan(profile, research_result)
    return {"plan": action_plan}


def critic_node(state: SahayakState) -> dict:
    """Validate the plan using deterministic quality checks."""
    profile = state.get("profile")
    action_plan = state.get("plan")

    if profile is None or action_plan is None:
        return {
            "verdict": None,
            "iterations": state.get("iterations", 0),
        }

    verdict = critique(
        profile,
        action_plan,
        state.get("research"),
    )

    return {
        "verdict": verdict,
        "iterations": state.get("iterations", 0) + 1,
    }


def replan_node(state: SahayakState) -> dict:
    """Revise the plan using critic feedback and retrieved evidence."""
    profile = state.get("profile")
    action_plan = state.get("plan")
    verdict = state.get("verdict")
    research_result = state.get("research")

    if (
        profile is None
        or action_plan is None
        or verdict is None
        or verdict.passed
        or not verdict.errors
    ):
        return {}

    revised_plan = replan(
        profile,
        action_plan,
        verdict.errors,
        research=research_result,
    )

    return {"plan": revised_plan}
