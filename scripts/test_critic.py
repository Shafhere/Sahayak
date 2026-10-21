"""Test Critic Agent with 3 scenarios."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.agents.understanding import understand
from app.agents.research import research
from app.agents.planning import plan
from app.agents.critic import critique


TESTS = [
    ("Normal widow pension", 
     "My grandmother is 68, widow, lives in Kerala, no income"),
    ("Young scholarship seeker",
     "I'm 17, finished 12th, OBC category, need scholarship"),
    ("Male user seeking schemes",
     "I'm a 30-year-old man from Kerala, need financial help"),
]


def main():
    for label, text in TESTS:
        print(f"\n{'='*70}")
        print(f"TEST: {label}")
        print(f"INPUT: {text}")
        print(f"{'='*70}")

        profile = understand(text)
        print(f"Profile: mode={profile.mode}, age={profile.age}, gender={profile.gender}")

        research_result = research(profile)
        print(f"Research: {research_result.num_results} chunks (source: {research_result.source})")

        action_plan = plan(profile, research_result)
        print(f"Plan: {len(action_plan.eligible_schemes)} schemes, "
              f"{len(action_plan.document_checklist)} docs, "
              f"Rs {action_plan.estimated_annual_benefit}")

        verdict = critique(profile, action_plan)
        print(f"\nVERDICT: {'✅ PASSED' if verdict.passed else '❌ FAILED'}")
        if verdict.errors:
            print(f"Errors ({len(verdict.errors)}):")
            for e in verdict.errors:
                print(f"  - {e}")
        if verdict.warnings:
            print(f"Warnings ({len(verdict.warnings)}):")
            for w in verdict.warnings:
                print(f"  - {w}")


if __name__ == "__main__":
    main()