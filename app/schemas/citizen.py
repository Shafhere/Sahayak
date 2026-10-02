"""Citizen profile — extracted from natural language input."""
from pydantic import BaseModel
from typing import Literal


class CitizenProfile(BaseModel):
    """Structured representation of a citizen's eligibility-relevant details."""
    age: int
    gender: Literal["male", "female", "other"]
    annual_income: int
    state: str
    occupation: str
    category: Literal["general", "obc", "sc", "st", "ews"]
    family_size: int
    language: Literal["en", "hi", "ml", "ta"]
    life_events: list[str] = []
    raw_input: str