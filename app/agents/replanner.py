
"""Revise an action plan using critic feedback and retrieved evidence."""

import json
import os
import sys
import time
from pathlib import Path

import yaml
from dotenv import load_dotenv
from groq import Groq, RateLimitError
from pydantic import ValidationError
from langsmith import traceable

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

load_dotenv(ROOT / ".env")

from app.agents.evidence import bind_sources
from app.schemas.citizen import CitizenProfile
from app.schemas.plan import ActionPlan
from app.schemas.research import ResearchResult

PROMPT_PATH = ROOT / "app" / "prompts" / "replanner" / "v1.yaml"
MODEL = os.getenv("GROQ_MODEL", "openai/gpt-oss-20b")

_prompt_cache = None
_client_cache = None


def _get_prompt():
    """Load and cache the replanning prompt."""
    global _prompt_cache

    if _prompt_cache is None:
        with PROMPT_PATH.open("r", encoding="utf-8") as file:
            _prompt_cache = yaml.safe_load(file)

    return _prompt_cache


def _get_client():
    """Create and cache the Groq client."""
    global _client_cache

    if _client_cache is None:
        api_key = os.getenv("GROQ_API_KEY")
        if not api_key:
            raise RuntimeError(
                "GROQ_API_KEY is missing. Add it to your .env file."
            )
        _client_cache = Groq(api_key=api_key)

    return _client_cache


def _build_user_message(
    profile: CitizenProfile,
    plan: ActionPlan,
    issues: list[str],
    research: ResearchResult | None,
) -> str:
    """Build the replanning request with available evidence."""
    evidence = []

    if research and research.chunks:
        for chunk in research.chunks:
            evidence.append(
                {
                    "chunk_id": chunk.chunk_id,
                    "doc_id": chunk.doc_id,
                    "name": chunk.name,
                    "page": chunk.page,
                    "source_url": chunk.source_url,
                    "text": chunk.text,
                }
            )

    return (
        f"Citizen profile:\n{profile.model_dump_json(indent=2)}\n\n"
        f"Current action plan:\n{plan.model_dump_json(indent=2)}\n\n"
        f"Critic issues to fix:\n{json.dumps(issues, ensure_ascii=False)}\n\n"
        f"Retrieved evidence:\n"
        f"{json.dumps(evidence, ensure_ascii=False, indent=2)}\n\n"
        "Return one valid JSON object matching the ActionPlan structure. "
        "Fix the listed issues without inventing facts or evidence. "
        "If the evidence does not support a scheme, remove it rather than "
        "making unsupported claims. Preserve useful correct information."
    )


@traceable(name="sahayak_replan")
def replan(
    profile: CitizenProfile,
    plan: ActionPlan,
    issues: list[str],
    max_retries: int = 3,
    research: ResearchResult | None = None,
) -> ActionPlan:
    """Revise a plan and validate the result."""
    if not issues:
        return plan

    if research is None or not research.chunks:
        # Avoid asking the model to invent evidence when none is available.
        return plan

    prompt = _get_prompt()
    client = _get_client()

    system_prompt = (
        prompt["system"]
        + "\n\nReturn only a valid JSON object matching ActionPlan. "
        "Use the provided research as the only evidence for scheme claims."
    )

    user_message = _build_user_message(
        profile,
        plan,
        issues,
        research,
    )

    last_error = None

    for attempt in range(max_retries):
        try:
            response = client.chat.completions.create(
                model=MODEL,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_message},
                ],
                temperature=0.2,
                response_format={"type": "json_object"},
            )

            raw_json = response.choices[0].message.content

            if not raw_json or not raw_json.strip():
                last_error = ValueError("Groq returned an empty response.")
                time.sleep(min(attempt + 1, 2))
                continue

            data = json.loads(raw_json)
            revised_plan = ActionPlan.model_validate(data)

            return bind_sources(revised_plan, research, profile)

        except RateLimitError as exc:
            raise RuntimeError(
                "Groq rate limit reached while revising the action plan."
            ) from exc

        except (json.JSONDecodeError, ValidationError, ValueError) as exc:
            last_error = exc
            print(
                f"[Replan] Invalid response on attempt "
                f"{attempt + 1}/{max_retries}: {exc}"
            )
            time.sleep(min(attempt + 1, 2))

        except Exception as exc:
            last_error = exc
            print(
                f"[Replan] Error on attempt "
                f"{attempt + 1}/{max_retries}: "
                f"{type(exc).__name__}: {exc}"
            )
            time.sleep(min(attempt + 1, 2))

    raise RuntimeError(
        f"Failed to revise the action plan. Last error: {last_error}"
    ) from last_error
