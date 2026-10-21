"""Test the full LangGraph workflow with 3 scenarios."""
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.workflows.graph import run_pipeline


TESTS = [
    "My grandmother is 68, widow, lives in Kerala, no income",
    "I'm 17, finished 12th, OBC category, need scholarship",
    "I need help with government schemes for my family",
]


def main():
    start = time.time()

    for text in TESTS:
        print(f"\n{'='*70}")
        print(f"INPUT: {text}")
        print(f"{'='*70}")

        result = run_pipeline(text)

        profile = result.get("profile")
        research = result.get("research")
        plan = result.get("plan")
        verdict = result.get("verdict")
        iterations = result.get("iterations", 0)

        print(f"\nMode: {profile.mode if profile else 'N/A'}")
        print(f"Research: {research.num_results if research else 0} chunks "
              f"(source: {research.source if research else 'N/A'})")
        print(f"Iterations: {iterations}")
        print(f"Verdict: {'PASSED' if verdict and verdict.passed else 'FAILED'}")

        if verdict and verdict.errors:
            print(f"Remaining errors:")
            for e in verdict.errors:
                print(f"  - {e}")

        if plan:
            print(f"\nFinal plan:")
            print(f"  Schemes: {len(plan.eligible_schemes)}")
            for s in plan.eligible_schemes:
                print(f"    - {s.name}")
            print(f"  Documents: {len(plan.document_checklist)}")
            print(f"  Timeline: {len(plan.timeline)} steps")
            print(f"  Est. benefit: Rs {plan.estimated_annual_benefit:,}")

    print(f"\n\nTotal time: {time.time() - start:.1f}s")


if __name__ == "__main__":
    main()