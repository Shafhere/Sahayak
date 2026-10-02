"""Scheme and eligibility — what the research agent produces."""
from pydantic import BaseModel


class Scheme(BaseModel):
    """A single government scheme with metadata."""
    scheme_id: str
    name: str
    description: str
    category: str
    state: str | None
    benefits: str
    documents_required: list[str]
    source_url: str
    citation: str
    deadline_date: str | None = None
    deadline_type: str = "rolling"


class Eligibility(BaseModel):
    """Eligibility verdict for one scheme for one citizen."""
    scheme_id: str
    eligible: bool
    reason: str
    confidence: float
    missing_requirements: list[str] = []