
"""Deterministic quality checks for Sahayak action plans."""

import re

from app.schemas.citizen import CitizenProfile
from app.schemas.plan import ActionPlan, CriticVerdict
from app.schemas.research import ResearchResult


def _normalize(text: str) -> str:
    return re.sub(r"\s+", " ", text or "").strip().casefold()


def _check_gender_mismatch(profile, plan):
    errors = []

    if profile.gender != "male":
        return errors

    terms = (
        "widow pension", "widow scheme", "maternity benefit",
        "pregnant woman", "pregnant women", "women-only", "women only",
    )

    for scheme in plan.eligible_schemes:
        text = _normalize(
            f"{scheme.name} {scheme.benefits} "
            f"{scheme.why_relevant} {scheme.eligibility_note}"
        )
        if any(term in text for term in terms):
            errors.append(f"Possible gender mismatch for recommendation: {scheme.name}")

    return errors


def _check_age_mismatch(profile, plan):
    errors = []

    if profile.age is None or profile.age >= 60:
        return errors

    terms = (
        "old age pension", "senior citizen pension",
        "senior citizens pension", "vayoshree", "vayovandana",
    )

    for scheme in plan.eligible_schemes:
        if any(term in _normalize(scheme.name) for term in terms):
            errors.append(f"Check age eligibility for recommendation: {scheme.name}")

    return errors


def _check_remarriage_mismatch(profile, plan):
    errors = []
    events = {str(event).casefold() for event in (profile.life_events or [])}

    if not (
        {"widow", "widower", "spouse_death"} & events
    ) or profile.age is None or profile.age < 50:
        return errors

    for scheme in plan.eligible_schemes:
        text = _normalize(
            f"{scheme.name} {scheme.benefits} {scheme.eligibility_note}"
        )
        if "remarriage" in text and ("widow" in text or "widower" in text):
            errors.append(f"Verify remarriage-related eligibility: {scheme.name}")

    return errors


def _check_completeness(plan):
    errors = []
    warnings = []

    if not plan.eligible_schemes and not plan.next_steps:
        errors.append("The plan has no recommendations and no next steps.")

    # These implementation/schema field names must never appear in
    # citizen-facing next-step text.
    internal_names = (
        "scheme_id",
        "evidence_quote",
        "source_page",
        "retrieved_chunks",
        "estimated_annual_benefit",
        "eligible_schemes",
        "document_checklist",
        "time_estimate",
        "source_edition",
        "source_name",
    )

    for index, step in enumerate(plan.next_steps, start=1):
        normalized = step.casefold()

        if len(step.strip()) < 8:
            warnings.append(f"Next step {index} may be too vague.")

        if any(name in normalized for name in internal_names):
            errors.append(
                f"Next step {index} contains an internal schema field name."
            )

    if plan.eligible_schemes:
        if not plan.document_checklist:
            warnings.append("Recommendations exist, but the document checklist is empty.")
        if not plan.timeline:
            warnings.append("Recommendations exist, but the timeline is empty.")

    return errors, warnings


def _check_evidence(plan, research):
    errors = []
    warnings = []
    sources = {}

    for chunk in research.chunks:
        if chunk.chunk_id:
            sources[chunk.chunk_id] = chunk
        if chunk.doc_id:
            sources[chunk.doc_id] = chunk

    for scheme in plan.eligible_schemes:
        source = sources.get(scheme.scheme_id)

        if source is None:
            errors.append(f"No matching retrieved source for: {scheme.name}")
            continue

        quote = _normalize(scheme.evidence_quote)
        source_text = _normalize(source.text)

        if len(quote) < 20:
            errors.append(f"Evidence quote is missing or too short for: {scheme.name}")
        elif quote not in source_text:
            errors.append(f"Evidence quote does not match retrieved text for: {scheme.name}")

        if not source.source_url:
            warnings.append(f"No source URL is available for: {scheme.name}")

    return errors, warnings


def critique(
    profile: CitizenProfile,
    plan: ActionPlan,
    research: ResearchResult | None = None,
) -> CriticVerdict:
    """Evaluate plan quality and evidence grounding."""
    errors = []
    warnings = []

    if profile.mode == "scheme":
        errors.extend(_check_gender_mismatch(profile, plan))
        errors.extend(_check_age_mismatch(profile, plan))
        errors.extend(_check_remarriage_mismatch(profile, plan))

    completeness_errors, completeness_warnings = _check_completeness(plan)
    errors.extend(completeness_errors)
    warnings.extend(completeness_warnings)

    if research is not None and research.chunks:
        evidence_errors, evidence_warnings = _check_evidence(plan, research)
        errors.extend(evidence_errors)
        warnings.extend(evidence_warnings)

    return CriticVerdict(
        passed=not errors,
        errors=errors,
        warnings=warnings,
    )
