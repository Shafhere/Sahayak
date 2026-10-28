
"""Attach source metadata to recommendations using retrieved evidence."""

from app.schemas.citizen import CitizenProfile
from app.schemas.plan import ActionPlan
from app.schemas.research import ResearchResult


def bind_sources(
    plan: ActionPlan,
    research: ResearchResult,
    profile: CitizenProfile | None = None,
) -> ActionPlan:
    """Attach metadata from the matching retrieved source."""
    sources = {}

    for chunk in research.chunks:
        if chunk.chunk_id:
            sources[chunk.chunk_id] = chunk
        if chunk.doc_id:
            sources[chunk.doc_id] = chunk

    for option in plan.eligible_schemes:
        source = sources.get(option.scheme_id)

        if source is None:
            option.source_url = ""
            option.source_name = ""
            option.source_page = 0
            option.source_edition = ""
            continue

        option.source_url = source.source_url or ""
        option.source_name = source.name or ""
        option.source_page = source.page or 0
        option.source_edition = source.edition or ""

        # Remove web-search wording when the source is not a web result.
        is_web = (source.doc_id or "").startswith("web_")
        note = option.eligibility_note or ""
        web_phrase = (
            "This information came from a web search result; confirm on "
            "the official portal before applying."
        )
        if not is_web and web_phrase in note:
            option.eligibility_note = note.replace(web_phrase, "").strip()

    if profile is not None and profile.mode == "mentor":
        for option in plan.eligible_schemes:
            # Learning resources should not inherit government-scheme
            # eligibility language or unsupported admission requirements.
            option.eligibility_note = (
                "This career guidance does not establish your eligibility "
                "for admission. Confirm current requirements with the "
                "official institution before applying."
            )

            # Remove explicit guarantees that cannot be established
            # by the recommendation alone.
            if option.benefits and any(
                phrase in option.benefits.lower()
                for phrase in (
                    "guaranteed admission",
                    "guaranteed job",
                    "guaranteed employment",
                )
            ):
                option.benefits = ""

            # Preserve relevant explanations unless they claim eligibility.
            if (
                option.why_relevant
                and "you are eligible" in option.why_relevant.lower()
            ):
                option.why_relevant = (
                    "Review this resource to see how it supports your "
                    "learning goals."
                )

    # Never infer a monetary benefit from unverified information.
    plan.estimated_annual_benefit = 0

    return plan
