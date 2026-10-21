"""Replanner Agent — fixes only the parts of a plan that the Critic flagged."""
import sys
from pathlib import Path
from langsmith import traceable

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

import json
import os
import yaml
from groq import Groq
from dotenv import load_dotenv
from pydantic import ValidationError


from app.schemas.citizen import CitizenProfile
from app.schemas.plan import ActionPlan


load_dotenv()

PROMPT_PATH = Path("app/prompts/replanner/v1.yaml")
MODEL = os.getenv("GROQ_MODEL", "openai/gpt-oss-20b")

_cached_prompt = None
_cached_client = None


def _load_prompt() -> dict:
    """Load replanner prompt once, cache it."""
    global _cached_prompt
    if _cached_prompt is None:
        with open(PROMPT_PATH, "r", encoding="utf-8") as f:
            _cached_prompt = yaml.safe_load(f)
    return _cached_prompt


def _get_client() -> Groq:
    """Get or create the singleton Groq client."""
    global _cached_client
    if _cached_client is None:
        api_key = os.getenv("GROQ_API_KEY")
        if not api_key:
            raise RuntimeError("GROQ_API_KEY not set")
        _cached_client = Groq(api_key=api_key, timeout=30.0, max_retries=2)
    return _cached_client

@traceable(run_type="chain", name="5. Replanner Agent")
def replan(
    profile: CitizenProfile,
    plan: ActionPlan,
    issues: list[str],
    max_retries: int = 5,
) -> ActionPlan:
    """
    Fix only the flagged parts of the plan.

    Args:
        profile: the citizen profile
        plan: the current (failed) plan
        issues: list of critic errors to fix
        max_retries: LLM retry attempts

    Returns:
        A revised ActionPlan with the issues addressed.
    """
    if not issues:
        return plan  # nothing to fix

    prompt = _load_prompt()
    client = _get_client()

    user_message = prompt["user"].format(
        profile=profile.model_dump_json(indent=2),
        plan=plan.model_dump_json(indent=2),
        issues="\n".join(f"- {i}" for i in issues),
    )

    last_error = None
    for attempt in range(max_retries):
        try:
            response = client.chat.completions.create(
                model=MODEL,
                messages=[
                    {"role": "system", "content": prompt["system"]},
                    {"role": "user", "content": user_message},
                ],
                temperature=0.1,
                response_format={"type": "json_object"},
            )

            raw_json = response.choices[0].message.content

            if not raw_json or not raw_json.strip():
                print(f"  [Replan] Empty response (attempt {attempt + 1}) — retrying")
                import time
                time.sleep(1)
                continue

            data = json.loads(raw_json)

            try:
                return ActionPlan(**data)
            except ValidationError as e:
                print(f"  [Replan] Schema validation failed (attempt {attempt + 1}): {e}")
                last_error = e
                import time
                time.sleep(1)
                continue

        except json.JSONDecodeError as e:
            print(f"  [Replan] Invalid JSON (attempt {attempt + 1}): {e}")
            last_error = e
            import time
            time.sleep(1)
            continue

        except Exception as e:
            print(f"  [Replan] Groq error (attempt {attempt + 1}): {type(e).__name__}")
            last_error = e
            import time
            time.sleep(1)
            continue

    raise RuntimeError(
        f"Replanning failed after {max_retries} attempts. Last error: {last_error}"
    )


if __name__ == "__main__":
    from app.agents.understanding import understand
    from app.agents.research import research
    from app.agents.planning import plan as build_plan
    from app.agents.critic import critique

    sample = "My grandmother is 68, widow, lives in Kerala, no income"
    profile = understand(sample)
    research_result = research(profile)
    action_plan = build_plan(profile, research_result)
    verdict = critique(profile, action_plan)

    print(f"\nOriginal plan: {len(action_plan.eligible_schemes)} schemes")
    print(f"Verdict: {'PASSED' if verdict.passed else 'FAILED'}")
    print(f"Errors: {verdict.errors}")

    if not verdict.passed:
        print("\nRunning Replanner...")
        fixed_plan = replan(profile, action_plan, verdict.errors)
        print(f"\nFixed plan: {len(fixed_plan.eligible_schemes)} schemes")
        for s in fixed_plan.eligible_schemes:
            print(f"  - {s.name}")

        new_verdict = critique(profile, fixed_plan)
        print(f"\nNew verdict: {'PASSED' if new_verdict.passed else 'FAILED'}")
        print(f"Errors: {new_verdict.errors}")