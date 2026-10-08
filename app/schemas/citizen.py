"""Citizen profile — extracted from natural language input."""
from pydantic import BaseModel, field_validator
from typing import Literal


class CitizenProfile(BaseModel):
    """Structured representation of a citizen's request."""
    language: Literal["en", "hi", "ml", "ta"] = "en"
    mode: Literal["scheme", "mentor", "journey", "companion", "care"] = "scheme"
    emotion: Literal["neutral", "grief", "confusion", "hope", "urgency"] = "neutral"

    age: int | None = None
    gender: Literal["male", "female", "other"] | None = None
    annual_income: int | None = None
    state: str | None = None
    occupation: str | None = None
    category: Literal["general", "obc", "sc", "st", "ews"] | None = None
    family_size: int | None = None

    life_events: list[str] = []
    missing_fields: list[str] = []

    raw_input: str = ""

    @field_validator("life_events", "missing_fields", mode="before")
    @classmethod
    def none_to_empty_list(cls, v):
        """Convert None to empty list for list fields."""
        if v is None:
            return []
        return v