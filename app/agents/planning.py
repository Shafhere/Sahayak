"""Planning Agent — builds action plan from research + profile."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

from langsmith import traceable
import json
import os
import yaml
from groq import Groq
from dotenv import load_dotenv
from pydantic import ValidationError

from app.schemas.citizen import CitizenProfile
from app.schemas.research import ResearchResult
from app.schemas.plan import ActionPlan


load_dotenv()

PROMPT_PATH = Path("app/prompts/planning/v1.yaml")
MODEL = os.getenv("GROQ_MODEL", "openai/gpt-oss-20b")

_cached_prompt = None
_cached_client = None


def _load_prompt() -> dict:
    """Load planning prompt once, cache it."""
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

@traceable(run_type="chain", name="3. Planning Agent")
def plan(profile: CitizenProfile, research: ResearchResult, max_chunks: int = 5) -> ActionPlan:
    """
    Build an action plan from the citizen profile and research chunks.
    """
    if not research or not research.chunks:
        return ActionPlan(
            eligible_schemes=[],
            document_checklist=[],
            timeline=[],
            next_steps=[
                "No information found for your query. "
                "Please provide more details or visit your local panchayat office."
            ],
            estimated_annual_benefit=0,
        )

    prompt = _load_prompt()
    client = _get_client()

    chunk_text = "\n\n---\n\n".join([
        f"[Source: {c.name}]\n{c.text}"
        for c in research.chunks[:max_chunks]
    ])

    user_message = prompt["user"].format(
        profile=profile.model_dump_json(indent=2),
        language=profile.language,
        research=chunk_text,
    )

    # Retry logic for Groq JSON failures
    last_error = None
    for attempt in range(5):
        try:
            response = client.chat.completions.create(
                model=MODEL,
                messages=[
                    {"role": "system", "content": prompt["system"]},
                    {"role": "user", "content": user_message},
                ],
                temperature=0.2,
                response_format={"type": "json_object"},
            )

            raw_json = response.choices[0].message.content

            if not raw_json or not raw_json.strip():
                print(f"  [Plan] Empty response (attempt {attempt + 1}) — retrying")
                continue

            data = json.loads(raw_json)

            try:
                return ActionPlan(**data)
            except ValidationError as e:
                print(f"  [Plan] Schema validation failed (attempt {attempt + 1}): {e}")
                last_error = e
                continue

        except json.JSONDecodeError as e:
            print(f"  [Plan] Invalid JSON (attempt {attempt + 1}): {e}")
            last_error = e
            continue

        except Exception as e:
            print(f"  [Plan] Groq error (attempt {attempt + 1}): {type(e).__name__}")
            last_error = e
            import time
            time.sleep(1)
            continue

    raise RuntimeError(
        f"Planning failed after 3 attempts. Last error: {last_error}"
    )


if __name__ == "__main__":
    from app.agents.understanding import understand
    from app.agents.research import research

    sample = "My grandmother is 68, widow, lives in Kerala, no income"
    profile = understand(sample)
    research_result = research(profile)
    action_plan = plan(profile, research_result)

    print(f"\nProfile mode: {profile.mode}")
    print(f"Research source: {research_result.source}")
    print(f"Research chunks: {research_result.num_results}")
    print(f"\nAction Plan:")
    print(action_plan.model_dump_json(indent=2))