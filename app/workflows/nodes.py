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
    """Extract structured profile from natural language."""
    profile = understand(state["raw_input"])
    return {
        "profile": profile,
        "mode": profile.mode,
        "iterations": 0,
        "needs_followup": getattr(profile, "needs_followup", False),
        "followup_questions": getattr(profile, "followup_questions", []),
    }

def research_node(state: SahayakState) -> dict:
    """Find grounded chunks with citations."""
    profile = state["profile"]
    if profile is None:
        return {"research": None}
    result = research(profile)
    return {"research": result}


def plan_node(state: SahayakState) -> dict:
    """Build initial action plan."""
    profile = state["profile"]
    research_result = state.get("research")
    if profile is None or research_result is None:
        return {"plan": None}
    action_plan = plan(profile, research_result)
    return {"plan": action_plan}


def critic_node(state: SahayakState) -> dict:
    """Validate the plan with deterministic rules."""
    profile = state["profile"]
    action_plan = state.get("plan")
    if profile is None or action_plan is None:
        return {"verdict": None}

    verdict = critique(profile, action_plan)
    current_iterations = state.get("iterations", 0)
    return {
        "verdict": verdict,
        "iterations": current_iterations + 1,
    }


def replan_node(state: SahayakState) -> dict:
    """Fix only the flagged issues in the plan."""
    profile = state["profile"]
    action_plan = state.get("plan")
    verdict = state.get("verdict")

    if profile is None or action_plan is None or verdict is None:
        return {}

    fixed_plan = replan(profile, action_plan, verdict.errors)
    return {"plan": fixed_plan}