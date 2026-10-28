
"""Citizen profile extracted from natural language input."""

from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator


class CitizenProfile(BaseModel):
    """Structured representation of a citizen's request."""

    model_config = ConfigDict(validate_assignment=True)

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

    interests: list[str] = Field(default_factory=list)
    strengths: list[str] = Field(default_factory=list)
    subjects: list[str] = Field(default_factory=list)

    career_goal: str | None = None
    education_level: str | None = None
    retrieval_query: str = ""

    life_events: list[str] = Field(default_factory=list)
    missing_fields: list[str] = Field(default_factory=list)

    raw_input: str = ""

    @field_validator(
        "life_events",
        "missing_fields",
        "interests",
        "strengths",
        "subjects",
        mode="before",
    )
    @classmethod
    def none_to_empty_list(cls, value):
        """Convert None to an empty list for list fields."""
        if value is None:
            return []
        return value
