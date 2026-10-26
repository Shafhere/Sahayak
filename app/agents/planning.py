
"""Generate a grounded action plan from retrieved research."""

import json
import os
import sys
import time
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

import yaml
from dotenv import load_dotenv
from groq import Groq, RateLimitError
from langsmith import traceable
from pydantic import ValidationError

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

load_dotenv(ROOT / ".env")

from app.agents.evidence import bind_sources
from app.schemas.citizen import CitizenProfile
from app.schemas.plan import ActionPlan
from app.schemas.research import ResearchResult

PROMPT_PATH = ROOT / "app" / "prompts" / "planning" / "v1.yaml"
MODEL = os.getenv("GROQ_PLAN_MODEL", os.getenv("GROQ_MODEL", "openai/gpt-oss-20b"))

_prompt_cache = None
_client_cache = None


def _get_prompt():
    global _prompt_cache

    if _prompt_cache is None:
        with PROMPT_PATH.open("r", encoding="utf-8") as file:
            _prompt_cache = yaml.safe_load(file)

    return _prompt_cache


def _get_client():
    global _client_cache

    if _client_cache is None:
        api_key = os.getenv("GROQ_API_KEY")
        if not api_key:
            raise RuntimeError("GROQ_API_KEY is missing from your .env file.")

        _client_cache = Groq(
            api_key=api_key,
            timeout=30.0,
            max_retries=1,
        )

    return _client_cache


def _fallback_plan(profile: CitizenProfile) -> ActionPlan:
    greetings = {
        "en": (
            "I can help identify relevant options, but more verified "
            "information is needed before recommending schemes."
        ),
        "ml": (
            "അനുയോജ്യമായ ഓപ്ഷനുകൾ കണ്ടെത്താൻ ഞാൻ സഹായിക്കാം. "
            "പദ്ധതികൾ ശുപാർശ ചെയ്യാൻ കൂടുതൽ സ്ഥിരീകരിച്ച വിവരങ്ങൾ ആവശ്യമാണ്."
        ),
        "hi": (
            "मैं उपयुक्त विकल्प खोजने में मदद कर सकता हूँ। "
            "योजनाओं की सिफारिश के लिए अधिक सत्यापित जानकारी आवश्यक है।"
        ),
        "ta": (
            "பொருத்தமான விருப்பங்களைக் கண்டறிய உதவ முடியும். "
            "திட்டங்களைப் பரிந்துரைக்க மேலும் சரிபார்க்கப்பட்ட தகவல்கள் தேவை."
        ),
    }

    return ActionPlan(
        greeting=greetings.get(profile.language, greetings["en"]),
        eligible_schemes=[],
        document_checklist=[],
        timeline=[],
        next_steps=[
            "Check the relevant official government portal or local government office for verified information."
        ],
        estimated_annual_benefit=0,
    )


def _build_user_message(
    profile: CitizenProfile,
    research: ResearchResult,
    max_chunks: int,
) -> str:
    """Build a readable evidence prompt with explicit source IDs."""
    today = datetime.now(ZoneInfo("Asia/Kolkata")).date().isoformat()
    user_situation_summary = (
        "User situation summary:\n"
        f"- Education level: {profile.education_level or 'Not provided'}\n"
        f"- Interests: {', '.join(profile.interests) or 'Not provided'}\n"
        f"- Strengths: {', '.join(profile.strengths) or 'Not provided'}\n"
        f"- Career goal: {profile.career_goal or 'Not provided'}\n"
        f"- Raw input: {profile.raw_input or 'Not provided'}\n"
    )

    evidence_blocks = []

    for chunk in research.chunks[:max_chunks]:
        source_id = chunk.chunk_id or chunk.doc_id or "unknown"

        evidence_blocks.append(
            f"Source ID: {source_id}\n"
            f"Document ID: {chunk.doc_id or ''}\n"
            f"Name: {chunk.name or ''}\n"
            f"Page: {chunk.page}\n"
            f"Edition: {chunk.edition or ''}\n"
            f"Source URL: {chunk.source_url or ''}\n"
            f"Evidence text:\n{chunk.text}"
        )

    evidence_text = (
        "\n\n---\n\n".join(evidence_blocks)
        if evidence_blocks
        else "No retrieved evidence available."
    )

    return (
        f"Today in India: {today}\n\n"
        f"{user_situation_summary}\n\n"
        f"Citizen profile:\n{profile.model_dump_json(indent=2)}\n\n"
        f"Language: {profile.language}\n\n"
        f"Retrieved evidence:\n{evidence_text}\n\n"
        "Create an action plan using only the supplied evidence. "
        "For each recommendation, copy its exact Source ID into scheme_id. "
        "Evidence quotes must be verbatim text from the matching source. "
        "Do not invent eligibility, benefits, deadlines, or contact details. "
        "Return one valid JSON object matching the ActionPlan structure. "
        "Do not include Markdown fences or explanatory text."
    )


@traceable(name="sahayak_plan")
def plan(
    profile: CitizenProfile,
    research: ResearchResult,
    max_chunks: int = 5,
) -> ActionPlan:
    """Generate, validate, and ground an action plan."""
    if research is None or not research.chunks:
        return _fallback_plan(profile)

    prompt = _get_prompt()
    client = _get_client()

    system_prompt = (
        prompt["system"]
        + "\n\nReturn only one valid JSON object. Follow the ActionPlan "
        "structure. Use empty strings, empty lists, or zero where "
        "information is unavailable. Never invent evidence."
    )

    user_message = _build_user_message(profile, research, max_chunks)
    last_error = None

    for attempt in range(5):
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
                time.sleep(min(attempt + 1, 3))
                continue

            data = json.loads(raw_json)
            action_plan = ActionPlan.model_validate(data)

            return bind_sources(action_plan, research, profile)

        except RateLimitError as exc:
            raise RuntimeError(
                "Groq rate limit reached while generating the action plan. "
                "Please retry later."
            ) from exc

        except (json.JSONDecodeError, ValidationError, ValueError) as exc:
            last_error = exc
            print(
                f"[Plan] Invalid response on attempt {attempt + 1}/5: {exc}"
            )
            time.sleep(min(attempt + 1, 3))

        except Exception as exc:
            # Groq's server-side JSON parser sometimes rejects output that is
            # otherwise valid (e.g. when the model copies Unicode space
            # variants from source text). Recover the raw generation when
            # available and validate it ourselves.
            recovered = False
            if "json_validate_failed" in str(exc):
                try:
                    body = exc.response.json()
                    raw = body.get("error", {}).get("failed_generation")
                    if raw:
                        data = json.loads(raw)
                        action_plan = ActionPlan.model_validate(data)
                        return bind_sources(action_plan, research, profile)
                except Exception as recovery_error:
                    print(
                        f"[Plan] Recovery parse failed: "
                        f"{type(recovery_error).__name__}: {recovery_error}"
                    )
            last_error = exc
            print(
                f"[Plan] Groq error on attempt {attempt + 1}/5: "
                f"{type(exc).__name__}: {exc}"
            )
            time.sleep(min(attempt + 1, 3))

    raise RuntimeError(
        f"Failed to generate a valid action plan after 5 attempts. "
        f"Last error: {last_error}"
    ) from last_error


if __name__ == "__main__":
    profile = CitizenProfile(
        language="en",
        mode="scheme",
        raw_input="My grandmother is 68, widowed, lives in Kerala, and has no income.",
        age=68,
        gender="female",
        state="Kerala",
        occupation="Not specified",
        retrieval_query="Kerala elderly widow pension schemes eligibility",
        life_events=["widow"],
    )

    research_result = ResearchResult(
        query="Kerala elderly widow pension schemes",
        mode="scheme",
        chunks=[],
        num_results=0,
        source="rag",
    )

    print(plan(profile, research_result).model_dump_json(indent=2))
