"""Critic Agent — validates action plans with pure Python rules. No AI."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

from langsmith import traceable
from app.schemas.citizen import CitizenProfile
from app.schemas.plan import ActionPlan, CriticVerdict


# Schemes that are inappropriate for elderly widows
REMARRIAGE_KEYWORDS = ["remarriage", "mangalya"]
MATERNITY_KEYWORDS = ["maternity", "mother", "pregnancy", "matru"]

# Schemes that require old age
OLD_AGE_KEYWORDS = ["old age", "senior citizen", "vayos"]


def _check_remarriage_mismatch(profile: CitizenProfile, plan: ActionPlan) -> list[str]:
    """Elderly widow is seeking pension — remarriage schemes are inappropriate."""
    errors = []
    is_elderly_widow = (
        profile.life_events and "spouse_death" in profile.life_events
        and profile.age and profile.age >= 55
    )
    if not is_elderly_widow:
        return errors

    for scheme in plan.eligible_schemes:
        name_lower = (scheme.name or "").lower()
        if any(kw in name_lower for kw in REMARRIAGE_KEYWORDS):
            errors.append(
                f"Scheme '{scheme.name}' is for remarriage, "
                f"but user is {profile.age}-year-old widow seeking pension"
            )
    return errors


def _check_gender_mismatch(profile: CitizenProfile, plan: ActionPlan) -> list[str]:
    """Male user but scheme is female-only."""
    errors = []
    if profile.gender != "male":
        return errors

    for scheme in plan.eligible_schemes:
        name_lower = (scheme.name or "").lower()
        benefit_lower = (scheme.benefits or "").lower()
        text = name_lower + " " + benefit_lower
        if any(kw in text for kw in ["widow", "maternity", "mother", "women"]):
            errors.append(
                f"Scheme '{scheme.name}' is female-only, but user is male"
            )
    return errors


def _check_age_mismatch(profile: CitizenProfile, plan: ActionPlan) -> list[str]:
    """User under 60 but scheme requires old age."""
    errors = []
    if not profile.age or profile.age >= 60:
        return errors

    for scheme in plan.eligible_schemes:
        name_lower = (scheme.name or "").lower()
        if any(kw in name_lower for kw in OLD_AGE_KEYWORDS):
            errors.append(
                f"Scheme '{scheme.name}' requires age 60+, but user is {profile.age}"
            )
    return errors


def _check_completeness(plan: ActionPlan) -> tuple[list[str], list[str]]:
    """Check that plan has all required pieces."""
    errors = []
    warnings = []

    # Empty plan — no schemes and no useful next steps
    if not plan.eligible_schemes and not plan.next_steps:
        errors.append("Plan is empty: no schemes found and no next steps")

    # Schemes but no documents
    if plan.eligible_schemes and not plan.document_checklist:
        warnings.append(
            "Schemes listed but no document checklist provided "
            "(user may not know what to bring)"
        )

    # Schemes but no timeline
    if plan.eligible_schemes and not plan.timeline:
        warnings.append("Schemes listed but no timeline provided")

    # Schemes but benefit is zero
    if plan.eligible_schemes and plan.estimated_annual_benefit == 0:
        warnings.append(
            "Schemes listed but estimated benefit is Rs 0 "
            "(amount may not have been extractable from documents)"
        )

    return errors, warnings

@traceable(run_type="chain", name="4. Critic Agent")
def critique(profile: CitizenProfile, plan: ActionPlan) -> CriticVerdict:
    """
    Validate an ActionPlan using deterministic rules.

    Returns:
        CriticVerdict with passed=False if any errors (triggers replan).
        passed=True with warnings still shown to user.
    """
    errors = []
    warnings = []

    # Rule 1: Context mismatch — remarriage for elderly widow
    errors.extend(_check_remarriage_mismatch(profile, plan))

    # Rule 2: Gender mismatch
    errors.extend(_check_gender_mismatch(profile, plan))

    # Rule 3: Age mismatch
    errors.extend(_check_age_mismatch(profile, plan))

    # Rule 4-7: Completeness
    comp_errors, comp_warnings = _check_completeness(plan)
    errors.extend(comp_errors)
    warnings.extend(comp_warnings)

    passed = len(errors) == 0

    return CriticVerdict(
        passed=passed,
        errors=errors,
        warnings=warnings,
    )


if __name__ == "__main__":
    from app.agents.understanding import understand
    from app.agents.research import research
    from app.agents.planning import plan as build_plan

    sample = "My grandmother is 68, widow, lives in Kerala, no income"
    profile = understand(sample)
    research_result = research(profile)
    action_plan = build_plan(profile, research_result)
    verdict = critique(profile, action_plan)

    print(f"\nVerdict: {'PASSED' if verdict.passed else 'FAILED'}")
    print(f"Errors: {len(verdict.errors)}")
    for e in verdict.errors:
        print(f"  - {e}")
    print(f"Warnings: {len(verdict.warnings)}")
    for w in verdict.warnings:
        print(f"  - {w}")