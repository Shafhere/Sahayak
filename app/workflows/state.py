
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
    followup_answers: dict[str, str]

    profile: CitizenProfile | None
    research: ResearchResult | None
    plan: ActionPlan | None
    verdict: CriticVerdict | None

    iterations: int
    final_response: str | None
    needs_followup: bool
    followup_questions: list[str]
