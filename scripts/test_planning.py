"""Test the Planning Agent end-to-end."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.agents.understanding import understand
from app.agents.research import research
from app.agents.planning import plan


TESTS = [
    "My grandmother is 68, widow, lives in Kerala, no income",
    "I'm 17, finished 12th, OBC category, need scholarship",
]


def main():
    for text in TESTS:
        print(f"\n{'='*70}")
        print(f"INPUT: {text}")
        print(f"{'='*70}")

        profile = understand(text)
        print(f"Mode: {profile.mode}")

        research_result = research(profile)
        print(f"Research: {research_result.num_results} chunks "
              f"(source: {research_result.source})")

        action_plan = plan(profile, research_result)
        print(f"\nAction Plan Summary:")
        print(f"  Schemes found: {len(action_plan.eligible_schemes)}")
        for s in action_plan.eligible_schemes:
            print(f"    - {s.name} ({s.benefits}, {s.deadline})")
        print(f"  Documents needed: {len(action_plan.document_checklist)}")
        for d in action_plan.document_checklist[:5]:
            print(f"    - {d}")
        print(f"  Timeline steps: {len(action_plan.timeline)}")
        for step in action_plan.timeline[:3]:
            print(f"    - {step.step} ({step.time_estimate})")
        print(f"  Est. annual benefit: Rs {action_plan.estimated_annual_benefit:,}")
        if action_plan.next_steps:
            print(f"  Next step: {action_plan.next_steps[0][:120]}")


if __name__ == "__main__":
    main()