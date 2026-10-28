
"""Build and run the Sahayak five-agent workflow."""

import time

from langgraph.graph import END, START, StateGraph

from app.workflows.state import SahayakState
from app.workflows.nodes import (
    understand_node,
    research_node,
    plan_node,
    critic_node,
    replan_node,
)
from app.workflows.metrics import record_run


MAX_CRITIC_ATTEMPTS = 3


def should_replan(state: SahayakState) -> str:
    """Stop on success or at the limit; otherwise revise the plan."""
    verdict = state.get("verdict")
    attempts = state.get("iterations", 0)

    if verdict is None:
        raise RuntimeError(
            "Workflow validation failed: the critic produced no verdict."
        )

    if verdict.passed:
        return "end"

    if attempts >= MAX_CRITIC_ATTEMPTS:
        return "end"

    if not verdict.errors:
        raise RuntimeError(
            "The critic rejected the plan but provided no correction details."
        )

    return "replan"


def build_graph():
    """Construct and compile the Sahayak workflow."""
    workflow = StateGraph(SahayakState)

    workflow.add_node("understand", understand_node)
    workflow.add_node("research", research_node)
    workflow.add_node("plan", plan_node)
    workflow.add_node("critic", critic_node)
    workflow.add_node("replan", replan_node)

    workflow.add_edge(START, "understand")
    workflow.add_edge("understand", "research")
    workflow.add_edge("research", "plan")
    workflow.add_edge("plan", "critic")

    workflow.add_conditional_edges(
        "critic",
        should_replan,
        {
            "replan": "replan",
            "end": END,
        },
    )

    workflow.add_edge("replan", "critic")

    return workflow.compile()


_graph = None


def get_graph():
    """Build the compiled graph once per process."""
    global _graph

    if _graph is None:
        _graph = build_graph()

    return _graph


def run_pipeline(raw_input: str, mode: str | None = None) -> dict:
    """Run Sahayak and record non-sensitive aggregate metrics."""
    if not isinstance(raw_input, str) or not raw_input.strip():
        raise ValueError("Please enter a non-empty message.")

    if mode not in (None, "scheme", "mentor"):
        raise ValueError("Mode must be 'scheme', 'mentor', or None.")

    initial_state = {
        "raw_input": raw_input.strip(),
        "requested_mode": mode,
    }

    start = time.perf_counter()

    try:
        result = get_graph().invoke(initial_state)

        required_fields = ("profile", "research", "plan", "verdict")
        missing = [
            field for field in required_fields
            if result.get(field) is None
        ]

        if missing:
            raise RuntimeError(
                "Workflow ended without required results: "
                + ", ".join(missing)
            )

    except Exception:
        record_run({}, time.perf_counter() - start, failed=True)
        raise

    record_run(result, time.perf_counter() - start)
    return result



if __name__ == "__main__":
    sample = "My grandmother is 68, widow, lives in Kerala, no income"
    result = run_pipeline(sample, mode="scheme")

    profile = result["profile"]
    plan = result["plan"]
    verdict = result["verdict"]

    print(f"\nMode: {profile.mode}")
    print(f"Critic attempts: {result.get('iterations', 0)}")
    print(f"Validation: {'PASSED' if verdict.passed else 'NOT PASSED'}")

    print(f"\nSchemes: {len(plan.eligible_schemes)}")
    for scheme in plan.eligible_schemes:
        print(f" - {scheme.name}")

    print(f"Documents: {len(plan.document_checklist)}")
    print(f"Timeline steps: {len(plan.timeline)}")
    print(f"Estimated annual benefit: Rs {plan.estimated_annual_benefit:,}")
