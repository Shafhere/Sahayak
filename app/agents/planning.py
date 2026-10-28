
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
    if profile.mode == "mentor" and profile.career_goal:
        career_goal = profile.career_goal or "your chosen career"
        education = profile.education_level or "your current education level"

        return ActionPlan(
            greeting=(
                f"Let's build a practical path toward {career_goal}. "
                f"Based on your background ({education}), this roadmap "
                "starts with fundamentals and progresses toward projects "
                "and job preparation. Research sources were unavailable, "
                "so verify specific courses and credentials before enrolling."
            ),
            eligible_schemes=[
                {
                    "name": "Programming fundamentals",
                    "benefits": (
                        "Learn variables, data types, conditions, loops, "
                        "functions, and basic problem-solving."
                    ),
                    "why_relevant": (
                        "Builds the foundation needed for software development."
                    ),
                },
                {
                    "name": "Git and GitHub",
                    "benefits": (
                        "Learn version control, repositories, commits, "
                        "and how to publish projects."
                    ),
                    "why_relevant": (
                        "Helps organize your work and build a visible portfolio."
                    ),
                },
                {
                    "name": "Web development and databases",
                    "benefits": (
                        "Progress through HTML, CSS, JavaScript, a suitable "
                        "backend, and SQL."
                    ),
                    "why_relevant": (
                        "Provides practical skills for building complete applications."
                    ),
                },
            ],
            document_checklist=[
                "A computer and a code editor",
                "A GitHub account for storing projects",
                "A consistent daily practice schedule",
                "A portfolio to document projects and progress",
            ],
            timeline=[
                {
                    "step": (
                        "Month 1: Learn Python fundamentals and solve "
                        "small coding problems. Outcome: complete at least "
                        "20 beginner exercises."
                    ),
                    "time_estimate": "Month 1",
                },
                {
                    "step": (
                        "Month 2: Practise functions, data structures, "
                        "debugging, Git, and GitHub. Outcome: publish "
                        "two small projects."
                    ),
                    "time_estimate": "Month 2",
                },
                {
                    "step": (
                        "Month 3: Learn HTML, CSS, and JavaScript. "
                        "Outcome: build and publish a responsive website."
                    ),
                    "time_estimate": "Month 3",
                },
                {
                    "step": (
                        "Month 4: Learn backend fundamentals and SQL. "
                        "Outcome: build an application that stores and "
                        "retrieves data."
                    ),
                    "time_estimate": "Month 4",
                },
                {
                    "step": (
                        "Month 5: Build a complete project, test it, "
                        "debug it, and deploy it. Outcome: one documented "
                        "portfolio-ready project."
                    ),
                    "time_estimate": "Month 5",
                },
                {
                    "step": (
                        "Month 6: Improve your portfolio, practise coding "
                        "and technical interviews, prepare your resume, "
                        "and apply to suitable entry-level roles. Outcome: "
                        "a finished portfolio and a regular application routine."
                    ),
                    "time_estimate": "Month 6",
                },
            ],
            next_steps=[
                "Install Python and VS Code if they are not already installed.",
                "Create a GitHub account and a repository for your practice.",
                "Begin with Python fundamentals and build something small every week.",
                "Treat this as a general roadmap, not a guarantee of job readiness or placement within six months.",
            ],
            estimated_annual_benefit=0,
        )

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
    """Build a mode-specific prompt with explicit source IDs."""
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

    if profile.mode == "mentor" and profile.career_goal:

        instructions = (
            "Create a practical, personalized career development plan "
            "based on the user's background and career goal. "
            "Use the existing ActionPlan JSON structure exactly. "
            "For each requested timeline month, include skills to learn, "
            "practical work, and a measurable outcome. "
            "Make next_steps consistent with Month 1; do not recommend a "
            "different starting course or language. "
            "Choose one coherent beginner-friendly technology path and avoid "
            "introducing too many new technologies at once. "
            "For software development, sequence fundamentals, Git, frontend "
            "basics, backend and databases, testing, deployment, and job "
            "preparation realistically. "
            "In eligible_schemes, recommend only a small number of relevant "
            "learning resources, courses, projects, or education pathways. "
            "For each recommendation, write a specific why_relevant explanation "
            "connected to the user's stated goal. "
            "Do not use generic government-scheme eligibility language in Mentor "
            "mode. Explain prerequisites only when known; otherwise use an "
            "empty eligibility_note. "
            "Describe the actual learning benefit when supported; do not leave "
            "benefits empty if the source clearly explains what is taught. "
            "Use retrieved evidence for factual claims about specific resources, "
            "providers, credentials, fees, and opportunities. "
            "Copy the exact Source ID into scheme_id and copy evidence_quote "
            "verbatim when a recommendation is source-backed. "
            "For general advice without a matching source, use empty scheme_id, "
            "evidence_quote, and unavailable source metadata. "
            "Never invent facts, URLs, credentials, fees, or employment guarantees. "
            "Return one valid JSON object matching the ActionPlan structure, "
            "without Markdown fences or commentary."
        )

    else:
        instructions = (
            "Create an action plan using only the supplied evidence. "
            "For each recommendation, copy its exact Source ID into scheme_id. "
            "Evidence quotes must be verbatim text from the matching source. "
            "Do not invent eligibility, benefits, deadlines, or contact details. "
            "Return one valid JSON object matching the ActionPlan structure. "
            "Do not include Markdown fences or explanatory text."
        )

    return (
        f"Today in India: {today}\n\n"
        f"{user_situation_summary}\n\n"
        f"Citizen profile:\n{profile.model_dump_json(indent=2)}\n\n"
        f"Language: {profile.language}\n\n"
        f"Retrieved evidence:\n{evidence_text}\n\n"
        f"{instructions}"
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

    if profile.mode == "mentor" and profile.career_goal:
        with (ROOT / "app" / "prompts" / "planning" / "mentor.yaml").open(
            "r", encoding="utf-8"
        ) as file:
            prompt = yaml.safe_load(file)
    else:
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
