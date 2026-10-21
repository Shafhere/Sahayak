"""Sahayak LangGraph state — flows through all agents."""
from typing import TypedDict
from app.schemas.citizen import CitizenProfile
from app.schemas.research import ResearchResult
from app.schemas.plan import ActionPlan, CriticVerdict


class SahayakState(TypedDict, total=False):
    """The single object passed between agents."""
    raw_input: str
    mode: str
    profile: CitizenProfile | None
    research: ResearchResult | None
    plan: ActionPlan | None
    verdict: CriticVerdict | None
    iterations: int
    final_response: str | None