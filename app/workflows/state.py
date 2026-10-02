"""Sahayak LangGraph state — flows through all agents."""
from typing import TypedDict
from app.schemas.citizen import CitizenProfile
from app.schemas.scheme import Scheme, Eligibility
from app.schemas.plan import ActionPlan, CriticVerdict


class SahayakState(TypedDict):
    """The single object passed between agents."""
    raw_input: str
    profile: CitizenProfile | None
    schemes: list[Scheme]
    eligibility: list[Eligibility]
    plan: ActionPlan | None
    verdict: CriticVerdict | None
    iterations: int
    final_response: str | None