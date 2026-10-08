"""Understanding Agent — extracts structured profile from natural language."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

import json
import os
import re
import yaml
from groq import Groq
from dotenv import load_dotenv
from pydantic import ValidationError

from app.schemas.citizen import CitizenProfile


load_dotenv()

PROMPT_PATH = Path("app/prompts/understanding/v1.yaml")
MODEL = os.getenv("GROQ_MODEL", "openai/gpt-oss-120b")

VALID_CATEGORIES = {"general", "obc", "sc", "st", "ews"}

GENDER_KEYWORDS = {
    "widow": "female",
    "വിധവ": "female",
    "विधवा": "female",
    "விதவை": "female",
    "widower": "male",
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
    r"\b(\d{2})\b",
]


_cached_prompt = None
_cached_client = None


def _load_prompt() -> dict:
    """Load prompt once, cache for reuse."""
    global _cached_prompt
    if _cached_prompt is None:
        with open(PROMPT_PATH, "r", encoding="utf-8") as f:
            _cached_prompt = yaml.safe_load(f)
    return _cached_prompt


def _get_client() -> Groq:
    """Get or create a singleton Groq client."""
    global _cached_client
    if _cached_client is None:
        api_key = os.getenv("GROQ_API_KEY")
        if not api_key:
            raise RuntimeError("GROQ_API_KEY not set in .env")
        _cached_client = Groq(api_key=api_key)
    return _cached_client


def _postprocess(data: dict, raw_input: str) -> dict:
    """Fix common LLM mistakes using deterministic rules."""
    # 0. Fix None values for list fields
    if data.get("life_events") is None:
        data["life_events"] = []
    if data.get("missing_fields") is None:
        data["missing_fields"] = []

    # 1. Category: lowercase + validate
    cat = data.get("category")
    if isinstance(cat, str):
        cat = cat.strip().lower()
        if cat not in VALID_CATEGORIES:
            cat = None
    data["category"] = cat

    # 2. Gender: infer from keywords if missing
    if not data.get("gender"):
        lower = raw_input.lower()
        for keyword, gender in GENDER_KEYWORDS.items():
            if keyword in lower:
                data["gender"] = gender
                break

    # 3. Age: regex extraction if missing
    if not data.get("age"):
        for pattern in AGE_PATTERNS:
            match = re.search(pattern, raw_input, re.IGNORECASE)
            if match:
                age = int(match.group(1))
                if 1 <= age <= 120:
                    data["age"] = age
                    break

    # 4. Emotion: detect grief from keywords if LLM said neutral
    if data.get("emotion") == "neutral":
        lower = raw_input.lower()
        for keyword in GRIEF_KEYWORDS:
            if keyword.lower() in lower:
                data["emotion"] = "grief"
                break

    # 5. Life events: infer spouse_death from widow/widower
    if not data.get("life_events"):
        lower = raw_input.lower()
        if any(kw in lower for kw in ["widow", "വിധവ", "विधवा", "விதவை", "widower"]):
            data["life_events"] = ["spouse_death"]

    # 6. Remove inferred fields from missing_fields
    missing = data.get("missing_fields", [])
    for field in ["age", "gender", "category"]:
        if data.get(field) is not None and field in missing:
            missing.remove(field)
    data["missing_fields"] = missing

    # 7. Ensure raw_input is set
    data["raw_input"] = raw_input

    return data


def understand(user_input: str) -> CitizenProfile:
    """Read a citizen's message and return a structured CitizenProfile."""
    from app.agents.cache import get as cache_get, set as cache_set

    prompt = _load_prompt()
    client = _get_client()
    user_message = prompt["user"].format(raw_input=user_input)

    # Try cache first
    data = cache_get(user_input)
    if data is None:
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
        try:
            data = json.loads(raw_json)
        except json.JSONDecodeError as e:
            raise ValueError(f"LLM returned invalid JSON: {e}\nRaw: {raw_json}")
        cache_set(user_input, data)

    data = _postprocess(data, user_input)

    try:
        return CitizenProfile(**data)
    except ValidationError as e:
        raise ValueError(f"LLM output failed schema validation: {e}")


if __name__ == "__main__":
    sample = "My grandmother is 68, widow, lives in Kerala. No income."
    profile = understand(sample)
    print(profile.model_dump_json(indent=2))