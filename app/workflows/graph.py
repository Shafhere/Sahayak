"""The Sahayak LangGraph workflow — 5 agents in a stateful loop."""
from langgraph.graph import StateGraph, START, END

from app.workflows.state import SahayakState
from app.workflows.nodes import (
    understand_node,
    research_node,
    plan_node,
    critic_node,
    replan_node,
)


MAX_ITERATIONS = 3


def should_replan(state: SahayakState) -> str:
    """Conditional edge: after critic, decide whether to replan or finish."""
    verdict = state.get("verdict")
    iterations = state.get("iterations", 0)

    # No verdict = something failed upstream
    if verdict is None:
        return "end"

    # Critic passed → done
    if verdict.passed:
        return "end"

    # Max iterations reached → done (best effort)
    if iterations >= MAX_ITERATIONS:
        print(f"  [Graph] Max iterations ({MAX_ITERATIONS}) reached — returning best-effort plan")
        return "end"

    # Failed but iterations left → replan
    return "replan"


def build_graph():
    """Build the workflow graph."""
    graph = StateGraph(SahayakState)

    # Add nodes
    graph.add_node("understand", understand_node)
    graph.add_node("research", research_node)
    graph.add_node("plan", plan_node)
    graph.add_node("critic", critic_node)
    graph.add_node("replan", replan_node)

    # Linear flow: understand → research → plan → critic
    graph.add_edge(START, "understand")
    graph.add_edge("understand", "research")
    graph.add_edge("research", "plan")
    graph.add_edge("plan", "critic")

    # Conditional: after critic, either replan or end
    graph.add_conditional_edges(
        "critic",
        should_replan,
        {
            "replan": "replan",
            "end": END,
        },
    )

    # After replan, go back to critic
    graph.add_edge("replan", "critic")

    return graph.compile()


# Singleton compiled graph
_graph = None


def get_graph():
    """Get or create the compiled graph."""
    global _graph
    if _graph is None:
        _graph = build_graph()
    return _graph


def run_pipeline(raw_input: str) -> dict:
    """Run the full pipeline on a raw input string."""
    graph = get_graph()
    initial_state = {"raw_input": raw_input}
    return graph.invoke(initial_state)


if __name__ == "__main__":
    sample = "My grandmother is 68, widow, lives in Kerala, no income"
    result = run_pipeline(sample)

    profile = result.get("profile")
    plan = result.get("plan")
    verdict = result.get("verdict")

    print(f"\n{'='*60}")
    print(f"Mode: {profile.mode if profile else 'N/A'}")
    print(f"Iterations: {result.get('iterations', 0)}")
    print(f"Verdict: {'PASSED' if verdict and verdict.passed else 'FAILED'}")
    print(f"{'='*60}")

    if plan:
        print(f"\nSchemes: {len(plan.eligible_schemes)}")
        for s in plan.eligible_schemes:
            print(f"  - {s.name}")
        print(f"Documents: {len(plan.document_checklist)}")
        print(f"Timeline: {len(plan.timeline)} steps")
        print(f"Est. benefit: Rs {plan.estimated_annual_benefit:,}")