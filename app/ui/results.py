"""Accessible result cards; generated text is never interpolated into HTML."""
import hashlib
import streamlit as st
from app.ui.labels import labels
from app.ui.report import generate_html_report


def render_results(result):
    profile, plan, verdict = (result.get(k) for k in ("profile", "plan", "verdict"))
    if not profile or not plan:
        st.error("Please try again with a little more detail.")
        return
    text = labels(profile.language)
    if not verdict or not verdict.passed:
        st.warning(text["failed"])
        return
    if not plan.eligible_schemes and not plan.timeline:
        st.subheader(text["empty"])
        for step in plan.next_steps:
            st.info(step)
        return
    st.divider()
    st.subheader(text["title"])
    if plan.greeting:
        st.write(plan.greeting)
    st.caption(text["verify"])
    if plan.next_steps:
        with st.container(border=True):
            st.markdown("### " + text["next"])
            for step in plan.next_steps[:3]:
                st.write("→ " + step)
    st.markdown("### " + text[profile.mode if profile.mode in ("scheme", "mentor") else "scheme"])
    for index, option in enumerate(plan.eligible_schemes, 1):
        with st.container(border=True):
            st.markdown(f"#### {index}. {option.name}")
            st.write(option.benefits)
            if option.why_relevant:
                st.markdown("**" + text["why"] + "**")
                st.write(option.why_relevant)
            if option.eligibility_note:
                st.markdown("**" + text["checks"] + "**")
                st.write(option.eligibility_note)
            if option.deadline:
                st.caption(text["deadline"] + ": " + option.deadline)
            with st.expander(text["evidence"]):
                if option.evidence_quote:
                    st.write(option.evidence_quote)
                st.caption(option.source_name + (f" · p. {option.source_page}" if option.source_page else ""))
                st.caption(option.source_edition)
                if option.source_url.startswith(("https://", "http://")):
                    url = option.source_url + (f"#page={option.source_page}" if option.source_page and ".pdf" in option.source_url else "")
                    st.link_button(text["source"], url)
                else:
                    st.caption(text["missing"])
    if plan.timeline:
        st.markdown("### " + text["timeline"])
        for index, step in enumerate(plan.timeline, 1):
            st.write(f"{index}. {step.step}")
            if step.time_estimate:
                st.caption(step.time_estimate)
    if plan.document_checklist:
        st.markdown("### " + text["docs"])
        plan_key = hashlib.sha256(plan.model_dump_json().encode()).hexdigest()[:12]
        for index, document in enumerate(plan.document_checklist):
            st.checkbox(document, key=f"doc_{plan_key}_{index}")
    st.download_button(text["save"], generate_html_report(profile, plan),
                       file_name=f"sahayak_{profile.mode}.html", mime="text/html",
                       use_container_width=True)
