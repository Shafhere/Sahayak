
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

    if profile is not None and profile.mode == "mentor":
        notes = {
            "en": (
                "This career guidance information does not establish your "
                "eligibility for admission. Confirm the current requirements "
                "with the official institution before applying."
            ),
            "ml": (
                "ഈ കരിയർ മാർഗനിർദേശ വിവരങ്ങൾ പ്രവേശനത്തിനുള്ള നിങ്ങളുടെ "
                "യോഗ്യത സ്ഥിരീകരിക്കുന്നില്ല. അപേക്ഷിക്കുന്നതിന് മുമ്പ് "
                "ഔദ്യോഗിക സ്ഥാപനത്തിൽ നിലവിലെ യോഗ്യത ഉറപ്പാക്കുക."
            ),
            "hi": (
                "यह करियर मार्गदर्शन आपकी प्रवेश पात्रता स्थापित नहीं करता। "
                "आवेदन करने से पहले आधिकारिक संस्थान से वर्तमान आवश्यकताओं "
                "की पुष्टि करें।"
            ),
            "ta": (
                "இந்தத் தொழில் வழிகாட்டல் தகவல் உங்கள் சேர்க்கைத் தகுதியை "
                "உறுதிப்படுத்தாது. விண்ணப்பிக்கும் முன் அதிகாரப்பூர்வ "
                "நிறுவனத்திடம் தற்போதைய தகுதிகளை உறுதிப்படுத்தவும்."
            ),
        }

        note = notes.get(profile.language, notes["en"])

        for option in plan.eligible_schemes:
            option.eligibility_note = note
            option.benefits = ""
            option.why_relevant = (
                "This information may help you explore the education or career pathway. "
                "Confirm your personal eligibility with the official institution."
            )
            option.deadline = ""

    # Never infer a monetary benefit from unverified information.
    plan.estimated_annual_benefit = 0

    return plan
