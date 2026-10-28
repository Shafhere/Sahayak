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
        st.caption(
            "Your question is valid, but our verified knowledge base does not "
            "yet contain the specific schemes for this case. The steps below "
            "help you find them through official sources."
        )
        for step in plan.next_steps:
            st.info(step)
        return

    st.divider()

    # Title + greeting
    st.markdown(
        f"<h2 style='font-family:Lora,serif;font-weight:600;margin-bottom:6px;'>"
        f"{text['title']}</h2>",
        unsafe_allow_html=True,
    )
    if plan.greeting:
        st.markdown(
            f"<div style='border-left:3px solid #C87559;padding-left:14px;"
            f"font-size:16px;line-height:1.65;margin-bottom:18px;'>"
            f"{plan.greeting}</div>",
            unsafe_allow_html=True,
        )
    st.caption(text["verify"])

    # Start here
    if plan.next_steps:
        with st.container(border=True):
            st.markdown(
                f"<div style='font-size:11px;font-weight:700;color:#C87559;"
                f"text-transform:uppercase;letter-spacing:1.2px;"
                f"margin-bottom:8px;'>{text['next']}</div>",
                unsafe_allow_html=True,
            )
            for step in plan.next_steps[:4]:
                st.markdown(f"**→** {step}")

    # Scheme / pathway cards
    section_label = text[profile.mode if profile.mode in ("scheme", "mentor") else "scheme"]
    st.markdown(f"### {section_label}")

    for index, option in enumerate(plan.eligible_schemes, 1):
        with st.container(border=True):
            st.markdown(
                f"<div style='display:flex;align-items:center;gap:12px;"
                f"margin-bottom:8px;'>"
                f"<span style='background:#C87559;color:#FFF;border-radius:8px;"
                f"padding:3px 10px;font-size:12px;font-weight:700;'>"
                f"{index:02d}</span>"
                f"<span style='font-family:Lora,serif;font-size:19px;"
                f"font-weight:600;'>{option.name}</span></div>",
                unsafe_allow_html=True,
            )

            if option.benefits:
                st.write(option.benefits)

            if option.why_relevant:
                st.markdown(f"**{text['why']}**")
                st.write(option.why_relevant)

            if option.eligibility_note:
                st.markdown(f"**{text['checks']}**")
                st.write(option.eligibility_note)

            if option.deadline:
                st.caption(f"{text['deadline']}: {option.deadline}")

            with st.expander(text["evidence"]):
                if option.evidence_quote:
                    st.markdown(
                        f"<blockquote style='border-left:3px solid #C87559;"
                        f"padding-left:12px;color:#4D625C;font-size:14px;"
                        f"margin:0 0 10px;'>{option.evidence_quote}</blockquote>",
                        unsafe_allow_html=True,
                    )
                meta_bits = [option.source_name or text["source"]]
                if option.source_page:
                    meta_bits.append(f"p. {option.source_page}")
                if option.source_edition:
                    meta_bits.append(option.source_edition)
                st.caption(" · ".join(meta_bits))

                if option.source_url.startswith(("https://", "http://")):
                    url = option.source_url
                    if option.source_page and ".pdf" in option.source_url:
                        url += f"#page={option.source_page}"
                    st.link_button(text["source"], url)
                else:
                    st.caption(text["missing"])

    # Timeline
    if plan.timeline:
        st.markdown(f"### {text['timeline']}")
        for index, step in enumerate(plan.timeline, 1):
            col1, col2 = st.columns([1, 20])
            with col1:
                st.markdown(
                    f"<div style='background:#EEE9DD;color:#174D49;"
                    f"width:30px;height:30px;border-radius:50%;"
                    f"display:flex;align-items:center;justify-content:center;"
                    f"font-weight:700;font-size:13px;'>{index}</div>",
                    unsafe_allow_html=True,
                )
            with col2:
                st.markdown(f"**{step.step}**")
                if step.time_estimate:
                    st.caption(step.time_estimate)

    # Document checklist
    if plan.document_checklist:
        st.markdown(f"### {text['docs']}")
        plan_key = hashlib.sha256(plan.model_dump_json().encode()).hexdigest()[:12]
        for index, document in enumerate(plan.document_checklist):
            st.checkbox(document, key=f"doc_{plan_key}_{index}")

    # Download
    st.download_button(
        text["save"],
        generate_html_report(profile, plan),
        file_name=f"sahayak_{profile.mode}.html",
        mime="text/html",
        use_container_width=True,
    )