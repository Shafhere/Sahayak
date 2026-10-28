
"""LangGraph nodes for the Sahayak workflow."""

from app.workflows.state import SahayakState
from app.agents.understanding import understand
from app.agents.research import research
from app.agents.planning import plan
from app.agents.critic import critique
from app.agents.replanner import replan


def understand_node(state: SahayakState) -> dict:
    """Convert the citizen's message into a structured profile."""
    raw_input = state.get("raw_input", "")

    if not isinstance(raw_input, str) or not raw_input.strip():
        raise ValueError("User input cannot be empty.")

    profile = understand(
        raw_input.strip(),
        requested_mode=state.get("requested_mode"),
    )

    return {
        "profile": profile,
        "mode": profile.mode,
        "iterations": 0,
    }


def research_node(state: SahayakState) -> dict:
    """Retrieve evidence relevant to the citizen's profile."""
    profile = state.get("profile")

    if profile is None:
        raise RuntimeError(
            "Cannot research because the understanding step produced no profile."
        )

    return {"research": research(profile)}


def plan_node(state: SahayakState) -> dict:
    """Generate an action plan from the profile and retrieved evidence."""
    profile = state.get("profile")
    research_result = state.get("research")

    if profile is None:
        raise RuntimeError("Cannot plan without a citizen profile.")

    if research_result is None:
        raise RuntimeError("Cannot plan without a research result.")

    return {"plan": plan(profile, research_result)}


def critic_node(state: SahayakState) -> dict:
    """Validate the plan and count each critic attempt."""
    profile = state.get("profile")
    action_plan = state.get("plan")
    research_result = state.get("research")

    if profile is None:
        raise RuntimeError("Cannot validate a plan without a profile.")

    if action_plan is None:
        raise RuntimeError("Cannot validate because no plan was generated.")

    verdict = critique(profile, action_plan, research_result)

    return {
        "verdict": verdict,
        "iterations": state.get("iterations", 0) + 1,
    }


def replan_node(state: SahayakState) -> dict:
    """Revise a rejected plan using critic feedback."""
    profile = state.get("profile")
    action_plan = state.get("plan")
    verdict = state.get("verdict")

    if profile is None or action_plan is None:
        raise RuntimeError("Cannot replan without a profile and plan.")

    if verdict is None:
        raise RuntimeError("Cannot replan without a critic verdict.")

    if verdict.passed:
        raise RuntimeError("Replanning was requested for an approved plan.")

    if not verdict.errors:
        raise RuntimeError(
            "Cannot replan because the critic provided no correction details."
        )

    revised_plan = replan(
        profile,
        action_plan,
        verdict.errors,
        research=state.get("research"),
    )

    if revised_plan is None:
        raise RuntimeError("The replanner did not produce a revised plan.")

    return {"plan": revised_plan}
