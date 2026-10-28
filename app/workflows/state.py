
"""Sahayak LangGraph state shared between workflow nodes."""

from typing import TypedDict

from app.schemas.citizen import CitizenProfile
from app.schemas.research import ResearchResult
from app.schemas.plan import ActionPlan, CriticVerdict


class SahayakState(TypedDict, total=False):
    """State passed between Sahayak workflow nodes."""

    raw_input: str
    mode: str
    requested_mode: str | None

    profile: CitizenProfile | None
    research: ResearchResult | None
    plan: ActionPlan | None
    verdict: CriticVerdict | None

    iterations: int
    final_response: str | None
