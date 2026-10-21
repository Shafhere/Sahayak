"""Action plan and critic verdict — the final output shape."""
from pydantic import BaseModel


class PlannedScheme(BaseModel):
    """One scheme included in the action plan."""
    scheme_id: str = ""
    name: str
    benefits: str = ""
    deadline: str = ""


class TimelineStep(BaseModel):
    """One step in the action timeline."""
    step: str
    time_estimate: str = ""


class ActionPlan(BaseModel):
    """Final action plan returned to the citizen."""
    eligible_schemes: list[PlannedScheme] = []
    document_checklist: list[str] = []
    timeline: list[TimelineStep] = []
    next_steps: list[str] = []
    estimated_annual_benefit: int = 0


class CriticVerdict(BaseModel):
    """Result of critic validation."""
    passed: bool
    issues: list[str] = []