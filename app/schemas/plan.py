"""Action plan and critic verdict — the final output shape."""
from pydantic import BaseModel
from app.schemas.scheme import Scheme


class ActionPlan(BaseModel):
    """Final action plan returned to the citizen."""
    eligible_schemes: list[Scheme]
    document_checklist: list[str]
    timeline: list[str]
    next_steps: list[str]
    estimated_annual_benefit: int


class CriticVerdict(BaseModel):
    """Result of critic validation."""
    passed: bool
    issues: list[str]