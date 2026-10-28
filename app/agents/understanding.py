
"""Understanding Agent — extracts structured profile from natural language."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

from langsmith import traceable
import json
import os
import re
import yaml
from groq import Groq, RateLimitError
from dotenv import load_dotenv
from pydantic import ValidationError

from app.schemas.citizen import CitizenProfile


load_dotenv()

PROMPT_PATH = Path(__file__).resolve().parents[1] / "prompts/understanding/v1.yaml"
MODEL = os.getenv("GROQ_MODEL", "openai/gpt-oss-20b")

VALID_CATEGORIES = {"general", "obc", "sc", "st", "ews"}

GENDER_KEYWORDS = {
    "widower": "male",
    "widow": "female",
    "വിധവ": "female",
    "विधवा": "female",
    "விதவை": "female",
    "mother": "female",
    "അമ്മ": "female",
    "grandmother": "female",
    "അമ്മൂമ്മ": "female",
    "father": "male",
    "അച്ഛൻ": "male",
    "grandfather": "male",
}

GRIEF_KEYWORDS = [
    "widow", "widower", "died", "death", "passed away",
    "വിധവ", "മരിച്ചു", "മരണം",
    "विधवा", "मर गया", "मृत्यु",
    "விதவை", "இறந்தார்",
    "feel alone", "nobody cares", "helpless",
]

AGE_PATTERNS = [
    r"(\d+)\s*(?:years?\s*old|yrs?|years)",
    r"(?:age|aged)\s*(\d+)",
    r"(\d+)\s*(?:വയസ്സ്|വയസ്)",
    r"(\d+)\s*(?:साल|वर्ष)",
    r"(\d+)\s*(?:வயது)",
]

KNOWN_STATES = [
    "Andhra Pradesh", "Arunachal Pradesh", "Assam", "Bihar",
    "Chhattisgarh", "Goa", "Gujarat", "Haryana", "Himachal Pradesh",
    "Jharkhand", "Karnataka", "Kerala", "Madhya Pradesh",
    "Maharashtra", "Manipur", "Meghalaya", "Mizoram", "Nagaland",
    "Odisha", "Punjab", "Rajasthan", "Sikkim", "Tamil Nadu",
    "Telangana", "Tripura", "Uttar Pradesh", "Uttarakhand",
    "West Bengal", "Andaman and Nicobar Islands", "Chandigarh",
    "Dadra and Nagar Haveli and Daman and Diu", "Delhi",
    "Jammu and Kashmir", "Ladakh", "Lakshadweep", "Puducherry",
]

_cached_prompt = None
_cached_client = None


def _load_prompt() -> dict:
    """Load prompt once, cache it."""
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

        _cached_client = Groq(
            api_key=api_key,
            timeout=30.0,
            max_retries=1,
        )

    return _cached_client


def _postprocess(data: dict, raw_input: str) -> dict:
    """Correct common LLM extraction mistakes using deterministic rules."""

    # 1. Normalize list fields that the LLM returned as None.
    for field in (
        "life_events",
        "missing_fields",
        "interests",
        "strengths",
        "subjects",
    ):
        if data.get(field) is None:
            data[field] = []

    # 2. Normalize and validate category.
    category = data.get("category")

    if isinstance(category, str):
        category = category.strip().lower()
        if category not in VALID_CATEGORIES:
            category = None

    data["category"] = category

    # 3. Infer gender from the original message if missing.
    if not data.get("gender"):
        lower = raw_input.lower()

        for keyword, gender in GENDER_KEYWORDS.items():
            if keyword in lower:
                data["gender"] = gender
                break

    # 4. Extract age from the original message if the LLM missed it.
    if data.get("age") is None:
        for pattern in AGE_PATTERNS:
            match = re.search(pattern, raw_input, re.IGNORECASE)

            if match:
                age = int(match.group(1))

                if 1 <= age <= 120:
                    data["age"] = age
                    break

    # 5. Extract an explicitly mentioned Indian state if missing.
    if not data.get("state"):
        for state in KNOWN_STATES:
            if re.search(
                rf"(?<!\w){re.escape(state)}(?!\w)",
                raw_input,
                re.IGNORECASE,
            ):
                data["state"] = state
                break

    # 6. Detect grief from keywords if the LLM returned neutral.
    if data.get("emotion") == "neutral":
        lower = raw_input.lower()

        for keyword in GRIEF_KEYWORDS:
            if keyword.lower() in lower:
                data["emotion"] = "grief"
                break

    # 7. Infer spouse_death from widow/widower keywords.
    if not data.get("life_events"):
        lower = raw_input.lower()

        if any(
            keyword in lower
            for keyword in ["widow", "വിധവ", "विधवा", "விதவை", "widower"]
        ):
            data["life_events"] = ["spouse_death"]

    # 8. Remove successfully extracted fields from missing_fields.
    missing = data.get("missing_fields", [])

    for field in ["age", "gender", "category"]:
        if data.get(field) is not None and field in missing:
            missing.remove(field)

    data["missing_fields"] = missing

    # 9. Preserve the original user message.
    data["raw_input"] = raw_input

    return data


@traceable(run_type="chain", name="1. Understanding Agent")
def understand(
    user_input: str,
    max_retries: int = 5,
    requested_mode: str | None = None,
) -> CitizenProfile:
    """Extract a structured citizen profile from a single user message."""

    prompt = _load_prompt()
    client = _get_client()

    user_message = prompt["user"].format(raw_input=user_input)

    if requested_mode:
        user_message += "\nSelected mode (preserve this): " + requested_mode

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
                print(
                    f"  [Understand] Empty response "
                    f"(attempt {attempt + 1}) — retrying"
                )
                continue

            data = json.loads(raw_json)
            data = _postprocess(data, user_input)

            if requested_mode:
                data["mode"] = requested_mode

            try:
                return CitizenProfile(**data)

            except ValidationError as e:
                print(
                    f"  [Understand] Schema validation failed "
                    f"(attempt {attempt + 1}): {e}"
                )
                last_error = e
                continue

        except json.JSONDecodeError as e:
            print(
                f"  [Understand] Invalid JSON "
                f"(attempt {attempt + 1}): {e}"
            )
            last_error = e
            continue

        except RateLimitError as e:
            raise RuntimeError(
                "The language service is busy or its quota has been reached. "
                "Please retry later."
            ) from e

        except Exception as e:
            print(
                f"  [Understand] Groq error (attempt {attempt + 1}): "
                f"{type(e).__name__}: {e}"
            )
            last_error = e
            continue

    raise RuntimeError(
        f"Understanding failed after {max_retries} attempts. "
        f"Last error: {last_error}"
    )


if __name__ == "__main__":
    sample = "My grandmother is 68, widow, lives in Kerala. No income."
    profile = understand(sample)
    print(profile.model_dump_json(indent=2))
