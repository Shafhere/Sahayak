
"""Action plan and critic verdict — the final output shape."""

from pydantic import BaseModel, Field, field_validator


class PlannedScheme(BaseModel):
    """One scheme included in the action plan."""

    scheme_id: str = ""
    name: str
    benefits: str = ""
    deadline: str = ""
    why_relevant: str = ""
    eligibility_note: str = ""
    evidence_quote: str = ""
    source_url: str = ""
    source_name: str = ""
    source_page: int = 0
    source_edition: str = ""

    @field_validator(
        "benefits",
        "why_relevant",
        "eligibility_note",
        mode="before",
    )
    @classmethod
    def readable_text(cls, value):
        if value is None:
            return ""
        if isinstance(value, list) and all(
            isinstance(item, str) for item in value
        ):
            return "; ".join(value)
        return value


class TimelineStep(BaseModel):
    """One step in the action timeline."""

    step: str
    time_estimate: str = ""


class CriticVerdict(BaseModel):
    """Result of critic validation."""

    passed: bool
    errors: list[str] = Field(default_factory=list)
    warnings: list[str] = Field(default_factory=list)


class ActionPlan(BaseModel):
    """Final action plan returned to the citizen."""

    greeting: str = ""
    eligible_schemes: list[PlannedScheme] = Field(default_factory=list)
    document_checklist: list[str] = Field(default_factory=list)
    timeline: list[TimelineStep] = Field(default_factory=list)
    next_steps: list[str] = Field(default_factory=list)
    estimated_annual_benefit: int = 0
