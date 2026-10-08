"""Citizen profile — extracted from natural language input."""
from pydantic import BaseModel
from typing import Literal


class CitizenProfile(BaseModel):
    """Structured representation of a citizen's request."""
    # Core identity
    language: Literal["en", "hi", "ml", "ta"] = "en"
    mode: Literal["scheme", "mentor", "journey", "companion", "care"] = "scheme"
    emotion: Literal["neutral", "grief", "confusion", "hope", "urgency"] = "neutral"

    # Extracted profile (all optional — may need follow-up)
    age: int | None = None
    gender: Literal["male", "female", "other"] | None = None
    annual_income: int | None = None
    state: str | None = None
    occupation: str | None = None
    category: Literal["general", "obc", "sc", "st", "ews"] | None = None
    family_size: int | None = None

    # Life events (for proactive triggers)
    life_events: list[str] = []

    # Follow-up questions to ask
    missing_fields: list[str] = []

    # Original input preserved
    raw_input: str = ""