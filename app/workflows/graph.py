
"""The Sahayak LangGraph workflow: five agents in a stateful loop."""

import time

from langgraph.graph import StateGraph, START, END

from app.workflows.state import SahayakState
from app.workflows.nodes import (
    understand_node,
    research_node,
    plan_node,
    critic_node,
    replan_node,
)
from app.workflows.metrics import record_run


MAX_ITERATIONS = 3


def should_replan(state: SahayakState) -> str:
    """Decide whether to replan or finish after the critic runs."""
    verdict = state.get("verdict")
    iterations = state.get("iterations", 0)

    # An absent verdict means an upstream step did not produce one.
    if verdict is None:
        return "end"

    # A passing verdict means the plan is ready.
    if verdict.passed:
        return "end"

    # Return the best available plan when the iteration limit is reached.
    if iterations >= MAX_ITERATIONS:
        print(
            f"[Graph] Maximum iterations ({MAX_ITERATIONS}) reached. "
            "Returning the best available plan."
        )
        return "end"

    return "replan"


def build_graph():
    """Build and compile the Sahayak workflow."""
    graph = StateGraph(SahayakState)

    graph.add_node("understand", understand_node)
    graph.add_node("research", research_node)
    graph.add_node("plan", plan_node)
    graph.add_node("critic", critic_node)
    graph.add_node("replan", replan_node)

    graph.add_edge(START, "understand")

    graph.add_conditional_edges(
        "understand",
        lambda state: (
            "followup" if state.get("needs_followup") else "research"
        ),
        {
            "followup": END,
            "research": "research",
        },
    )

    graph.add_edge("research", "plan")
    graph.add_edge("plan", "critic")

    graph.add_conditional_edges(
        "critic",
        should_replan,
        {
            "replan": "replan",
            "end": END,
        },
    )

    # Recheck the revised plan with the critic.
    graph.add_edge("replan", "critic")

    return graph.compile()


_graph = None


def get_graph():
    """Return the cached compiled workflow."""
    global _graph

    if _graph is None:
        _graph = build_graph()

    return _graph


def run_pipeline(
    raw_input: str,
    mode: str | None = None,
    followup_answers: dict[str, str] | None = None,
) -> dict:
    """Run the workflow and record non-sensitive aggregate metrics."""
    if mode not in (None, "scheme", "mentor"):
        raise ValueError("Choose scheme or mentor mode")

    initial_state = {
        "raw_input": raw_input,
        "requested_mode": mode,
        "followup_answers": followup_answers or {},
    }

    graph = get_graph()
    start = time.perf_counter()

    try:
        result = graph.invoke(initial_state)
    except Exception:
        record_run({}, time.perf_counter() - start, failed=True)
        raise

    record_run(result, time.perf_counter() - start)
    return result


if __name__ == "__main__":
    sample = "My grandmother is 68, widow, lives in Kerala, no income"
    result = run_pipeline(sample)

    profile = result.get("profile")
    plan = result.get("plan")
    verdict = result.get("verdict")

    print("\n" + "=" * 60)
    print(f"Mode: {profile.mode if profile else 'N/A'}")
    print(f"Iterations: {result.get('iterations', 0)}")
    print(
        f"Verdict: "
        f"{'PASSED' if verdict and verdict.passed else 'FAILED'}"
    )
    print("=" * 60)

    if plan:
        print(f"\nSchemes: {len(plan.eligible_schemes)}")
        for scheme in plan.eligible_schemes:
            print(f"  - {scheme.name}")

        print(f"Documents: {len(plan.document_checklist)}")
        print(f"Timeline: {len(plan.timeline)} steps")
        print(f"Estimated benefit: Rs {plan.estimated_annual_benefit:,}")
