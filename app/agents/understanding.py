"""Understanding Agent — extracts structured profile from natural language."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

import json
import os
from pathlib import Path

import yaml
from groq import Groq
from dotenv import load_dotenv
from pydantic import ValidationError

from app.schemas.citizen import CitizenProfile


load_dotenv()

PROMPT_PATH = Path("app/prompts/understanding/v1.yaml")
MODEL = os.getenv("GROQ_MODEL", "openai/gpt-oss-120b")


def _load_prompt() -> dict:
    """Load the versioned YAML prompt."""
    with open(PROMPT_PATH, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def _get_client() -> Groq:
    """Create a Groq API client."""
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        raise RuntimeError("GROQ_API_KEY not set in .env")
    return Groq(api_key=api_key)


def understand(user_input: str) -> CitizenProfile:
    """
    Read a citizen's message and return a structured CitizenProfile.

    Args:
        user_input: natural-language text in any supported language

    Returns:
        CitizenProfile with extracted fields, mode, emotion, and missing fields.
    """
    prompt = _load_prompt()
    client = _get_client()

    user_message = prompt["user"].format(raw_input=user_input)

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

    # Ensure raw_input is set
    data["raw_input"] = user_input

    try:
        return CitizenProfile(**data)
    except ValidationError as e:
        raise ValueError(f"LLM output failed schema validation: {e}")


if __name__ == "__main__":
    sample = "My grandmother is 68, widow, lives in Kerala. No income."
    profile = understand(sample)
    print(profile.model_dump_json(indent=2))