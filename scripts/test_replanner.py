"""Test the full pipeline: Plan → Critic → Replan → Critic, max 3 loops."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.agents.understanding import understand
from app.agents.research import research
from app.agents.planning import plan as build_plan
from app.agents.critic import critique
from app.agents.replanner import replan


MAX_ITERATIONS = 3


def run_full_pipeline(text: str) -> dict:
    """Run the full 5-agent loop."""
    print(f"\n{'='*70}")
    print(f"INPUT: {text}")
    print(f"{'='*70}")

    # Step 1: Understanding
    profile = understand(text)
    print(f"Mode: {profile.mode}, Age: {profile.age}, Gender: {profile.gender}")

    # Step 2: Research
    research_result = research(profile)
    print(f"Research: {research_result.num_results} chunks (source: {research_result.source})")

    # Step 3: Initial plan
    action_plan = build_plan(profile, research_result)
    print(f"Initial plan: {len(action_plan.eligible_schemes)} schemes")

    # Step 4-5: Critic + Replanner loop
    iteration = 0
    final_verdict = None

    while iteration < MAX_ITERATIONS:
        iteration += 1
        verdict = critique(profile, action_plan)
        print(f"\n  Iteration {iteration}: {'PASSED' if verdict.passed else 'FAILED'}")

        if verdict.errors:
            for e in verdict.errors:
                print(f"    Error: {e}")

        if verdict.passed:
            final_verdict = verdict
            break

        if iteration >= MAX_ITERATIONS:
            print(f"    Max iterations reached — returning best-effort plan")
            final_verdict = verdict
            break

        # Replan
        print(f"    Replanning...")
        action_plan = replan(profile, action_plan, verdict.errors)

    # Final report
    print(f"\n{'='*70}")
    print(f"FINAL RESULT (after {iteration} iteration(s))")
    print(f"{'='*70}")
    print(f"Status: {'PASSED' if final_verdict.passed else 'FAILED (best-effort)'}")
    print(f"Schemes: {len(action_plan.eligible_schemes)}")
    for s in action_plan.eligible_schemes:
        print(f"  - {s.name}")
    print(f"Documents: {len(action_plan.document_checklist)}")
    print(f"Timeline steps: {len(action_plan.timeline)}")
    print(f"Est. annual benefit: Rs {action_plan.estimated_annual_benefit:,}")

    if final_verdict.warnings:
        print(f"\nWarnings:")
        for w in final_verdict.warnings:
            print(f"  - {w}")

    return {
        "profile": profile,
        "research": research_result,
        "plan": action_plan,
        "verdict": final_verdict,
        "iterations": iteration,
    }


def main():
    tests = [
        "My grandmother is 68, widow, lives in Kerala, no income",
        "I'm 17, finished 12th, OBC category, need scholarship",
    ]
    for text in tests:
        run_full_pipeline(text)


if __name__ == "__main__":
    main()