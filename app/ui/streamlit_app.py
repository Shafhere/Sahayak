
"""Sahayak Streamlit UI — clean, warm light theme with Voice & OCR."""

import os
import sys
from pathlib import Path
from html import escape

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

import requests
import streamlit as st

from app.tools.voice import transcribe_audio
from app.tools.ocr import extract_text_from_image
from app.workflows.graph import run_pipeline
from app.ui.results import render_results


API_URL = os.getenv("API_URL", "http://localhost:8000")

st.set_page_config(
    page_title="Sahayak",
    page_icon="🌱",
    layout="wide",
    initial_sidebar_state="expanded",
)

# -------------------- Session defaults --------------------

defaults = {
    "user": None,
    "token": None,
    "theme": "light",
    "page": "scheme",
    "results": None,
    "followup": None,
    "voice_query": "",
    "voice_text": "",
}

for key, value in defaults.items():
    if key not in st.session_state:
        st.session_state[key] = value

# Light theme only
st.session_state.theme = "light"

# Warm, muted palette
BG = "#F5F3EE"
SIDEBAR_BG = "#244C49"
CARD_BG = "#FBFAF7"
TEXT = "#293735"
MUTED = "#697875"
ACCENT = "#C87559"
BORDER = "#E3E0D8"
INPUT_BG = "#FDFCFA"


# -------------------- CSS --------------------

st.markdown(
    f"""
    <style>
    @import url(
        'https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&family=Lora:wght@500;600&display=swap'
    );

    :root {{
        color-scheme: light;
    }}

    .stApp {{
        background: {BG} !important;
        color: {TEXT} !important;
        font-family: 'DM Sans', sans-serif;
    }}

    html, body, [class*="css"] {{
        font-family: 'DM Sans', sans-serif;
        color: {TEXT};
    }}

    header[data-testid="stHeader"] {{
        background: transparent !important;
    }}

    #MainMenu, footer {{
        visibility: hidden;
    }}

    .block-container {{
        max-width: 1080px !important;
        padding-top: 1.5rem !important;
        padding-bottom: 2.5rem !important;
        padding-left: 2rem !important;
        padding-right: 2rem !important;
    }}

    /* Sidebar */
    [data-testid="stSidebar"] {{
        background: {SIDEBAR_BG} !important;
    }}

    [data-testid="stSidebar"] * {{
        color: #F7F8F5;
    }}

    [data-testid="stSidebar"] .stButton > button {{
        width: 100%;
        min-height: 40px;
        padding: 0.55rem 0.8rem !important;
        border: 1px solid transparent !important;
        border-radius: 9px !important;
        background: transparent !important;
        color: #F7F8F5 !important;
        text-align: left !important;
        justify-content: flex-start !important;
        font-size: 14px !important;
        box-shadow: none !important;
    }}

    [data-testid="stSidebar"] .stButton > button:hover {{
        background: rgba(255,255,255,0.09) !important;
    }}

    [data-testid="stSidebar"] .stButton > button[kind="primary"] {{
        background: rgba(255,255,255,0.14) !important;
        border-color: rgba(255,255,255,0.12) !important;
        font-weight: 600 !important;
    }}

    /* Headings */
    h1, h2, h3 {{
        font-family: 'Lora', Georgia, serif !important;
        color: {TEXT} !important;
        letter-spacing: -0.3px;
    }}

    h1 {{
        font-size: 2rem !important;
    }}

    h2 {{
        font-size: 1.5rem !important;
    }}

    h3 {{
        font-size: 1.15rem !important;
    }}

    p, li, label {{
        color: {TEXT};
        line-height: 1.6;
    }}

    /* Inputs */
    .stTextInput input,
    .stTextArea textarea {{
        background: {INPUT_BG} !important;
        color: {TEXT} !important;
        border: 1px solid {BORDER} !important;
        border-radius: 9px !important;
        font-size: 14px !important;
        box-shadow: none !important;
    }}

    .stTextInput input::placeholder,
    .stTextArea textarea::placeholder {{
        color: #858D88 !important;
        opacity: 1 !important;
    }}

    .stTextInput input:focus,
    .stTextArea textarea:focus {{
        border-color: {ACCENT} !important;
        box-shadow: 0 0 0 1px {ACCENT} !important;
    }}

    /* Main buttons */
    .stButton > button,
    .stFormSubmitButton > button {{
        background: {ACCENT} !important;
        color: #FFFFFF !important;
        border: 1px solid {ACCENT} !important;
        border-radius: 9px !important;
        min-height: 39px;
        padding: 0.45rem 1rem !important;
        font-size: 14px !important;
        font-weight: 600 !important;
        box-shadow: none !important;
        transition: background 0.15s ease;
    }}

    .stButton > button:hover,
    .stFormSubmitButton > button:hover {{
        background: #AD624A !important;
        border-color: #AD624A !important;
    }}

    /* Bordered containers: subtle background and compact spacing.
       Do not style every nested Streamlit block as a card. */
    [data-testid="stVerticalBlockBorderWrapper"] {{
        background: {CARD_BG} !important;
        border: 1px solid {BORDER} !important;
        border-radius: 12px !important;
        box-shadow: 0 1px 4px rgba(38, 49, 43, 0.035);
    }}

    [data-testid="stVerticalBlockBorderWrapper"] > div {{
        gap: 0.75rem;
    }}

    /* Tabs */
    .stTabs [data-baseweb="tab-list"] {{
        gap: 1.2rem;
        border-bottom: 1px solid {BORDER};
        background: transparent !important;
    }}

    .stTabs [data-baseweb="tab"] {{
        color: {MUTED} !important;
        padding: 0.6rem 0.1rem !important;
        font-size: 14px !important;
    }}

    .stTabs [data-baseweb="tab"][aria-selected="true"] {{
        color: {TEXT} !important;
        border-bottom: 2px solid {ACCENT} !important;
    }}

    .stTabs [data-baseweb="tab-highlight"],
    .stTabs [data-baseweb="tab-border"] {{
        background: {ACCENT} !important;
    }}

    /* Expanders */
    [data-testid="stExpander"] {{
        background: {CARD_BG} !important;
        border: 1px solid {BORDER} !important;
        border-radius: 10px !important;
    }}

    [data-testid="stExpander"] summary {{
        color: {TEXT} !important;
        font-size: 14px !important;
    }}

    /* Hero banner */
    .hero-container {{
        background: {SIDEBAR_BG};
        border-radius: 15px;
        padding: 27px 30px;
        margin-bottom: 22px;
    }}

    .hero-title {{
        font-family: 'Lora', Georgia, serif;
        font-size: 29px;
        line-height: 1.3;
        font-weight: 600;
        color: #FFFFFF !important;
        margin: 0 0 8px 0;
    }}

    .hero-sub {{
        font-size: 14px;
        line-height: 1.65;
        color: #E0E9E5 !important;
        margin: 0;
    }}

    /* Result components used by the results renderer */
    .greeting {{
        font-family: 'Lora', Georgia, serif;
        font-size: 19px;
        line-height: 1.65;
        color: {TEXT};
        margin-bottom: 22px;
        padding-left: 15px;
        border-left: 3px solid {ACCENT};
    }}

    .section-label {{
        font-size: 11px;
        font-weight: 700;
        color: {ACCENT} !important;
        text-transform: uppercase;
        letter-spacing: 1.2px;
        margin-bottom: 10px;
    }}

    .stat-box {{
        text-align: center;
        padding: 8px;
    }}

    .stat-value {{
        font-family: 'Lora', Georgia, serif;
        font-size: 28px;
        font-weight: 600;
        color: {ACCENT} !important;
        margin: 0;
    }}

    .stat-label {{
        font-size: 12px;
        color: {MUTED} !important;
        margin-top: 4px;
    }}

    .benefit-box {{
        background: {SIDEBAR_BG};
        border-radius: 12px;
        padding: 18px;
        text-align: center;
        margin-bottom: 16px;
    }}

    .benefit-value {{
        font-family: 'Lora', Georgia, serif;
        font-size: 34px;
        font-weight: 600;
        color: #FFFFFF !important;
        margin: 0;
    }}

    .benefit-label {{
        font-size: 12px;
        color: #E0E9E5 !important;
        text-transform: uppercase;
        letter-spacing: 0.8px;
        margin-top: 5px;
    }}

    .timeline-item {{
        display: flex;
        gap: 12px;
        padding: 12px 0;
        border-bottom: 1px solid {BORDER};
    }}

    .timeline-item:last-child {{
        border-bottom: none;
    }}

    .timeline-num {{
        background: #EEEBE3;
        color: {TEXT};
        width: 28px;
        height: 28px;
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 12px;
        font-weight: 600;
        flex-shrink: 0;
    }}

    .timeline-text {{
        font-weight: 600;
        font-size: 14px;
        color: {TEXT};
        margin: 0;
    }}

    .timeline-time {{
        font-size: 12px;
        color: {MUTED};
        margin-top: 3px;
    }}

    /* Alerts */
    [data-testid="stAlert"] {{
        border-radius: 9px;
    }}

    /* Uploaded files and audio controls */
    [data-testid="stFileUploader"],
    [data-testid="stAudioInput"] {{
        font-size: 13px;
    }}

    /* Smaller screens */
    @media (max-width: 768px) {{
        .block-container {{
            padding: 1rem !important;
        }}

        .hero-container {{
            padding: 21px;
        }}

        .hero-title {{
            font-size: 25px;
        }}
    }}
    </style>
    """,
    unsafe_allow_html=True,
)


# -------------------- Sidebar --------------------

def render_sidebar():
    with st.sidebar:
        st.markdown(
            f"""
            <div style="
                display:flex;
                align-items:center;
                gap:11px;
                padding:8px 0 24px 6px;
            ">
                <div style="
                    background:{ACCENT};
                    width:36px;
                    height:36px;
                    border-radius:10px;
                    display:flex;
                    align-items:center;
                    justify-content:center;
                    font-size:18px;
                ">🌱</div>
                <div>
                    <div style="
                        font-family:'Lora',Georgia,serif;
                        font-size:18px;
                        font-weight:600;
                    ">Sahayak</div>
                    <div style="
                        font-size:11px;
                        color:#D5E2DE;
                        margin-top:2px;
                    ">Citizen Companion</div>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        if st.button(
            "🏡  Scheme",
            use_container_width=True,
            type=(
                "primary"
                if st.session_state.page == "scheme"
                else "secondary"
            ),
        ):
            st.session_state.page = "scheme"
            st.session_state.results = None
            st.session_state.followup = None
            st.rerun()

        if st.button(
            "🎓  Mentor",
            use_container_width=True,
            type=(
                "primary"
                if st.session_state.page == "mentor"
                else "secondary"
            ),
        ):
            st.session_state.page = "mentor"
            st.session_state.results = None
            st.session_state.followup = None
            st.rerun()

        st.markdown(
            "<hr style='border-color:rgba(255,255,255,0.15)'>",
            unsafe_allow_html=True,
        )

        full_name = escape(
            st.session_state.user.get("full_name", "Guest")
        )

        st.markdown(
            f"""
            <div style="
                padding:9px;
                background:rgba(255,255,255,0.07);
                border-radius:8px;
                margin-bottom:12px;
                font-size:13px;
            ">👤 {full_name}</div>
            """,
            unsafe_allow_html=True,
        )

        if st.button(
            "🚪  Exit",
            key="logout_btn",
            use_container_width=True,
        ):
            st.session_state.user = None
            st.session_state.token = None
            st.session_state.results = None
            st.session_state.followup = None
            st.rerun()


# -------------------- Hero --------------------

def render_hero():
    subtitle = (
        "Explore education and career paths that fit your interests."
        if st.session_state.page == "mentor"
        else "Find support, understand the requirements, and plan your next step."
    )

    st.markdown(
        f"""
        <div class="hero-container">
            <div class="hero-title">A clearer next step.</div>
            <div class="hero-sub">{subtitle}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


# -------------------- Authentication --------------------

def render_auth():
    left, center, right = st.columns([1, 1.15, 1])

    with center:
        with st.container(border=True):
            st.markdown(
                f"""
                <div style="text-align:center;margin:8px 0 22px;">
                    <div style="
                        background:{ACCENT};
                        width:48px;
                        height:48px;
                        border-radius:13px;
                        display:inline-flex;
                        align-items:center;
                        justify-content:center;
                        font-size:24px;
                        margin-bottom:12px;
                    ">🌱</div>
                    <h1 style="
                        font-family:'Lora',Georgia,serif;
                        font-size:30px;
                        font-weight:600;
                        color:{TEXT};
                        margin:0;
                    ">Sahayak</h1>
                    <p style="
                        color:{MUTED};
                        margin:6px 0 0;
                        font-size:14px;
                    ">A companion for every Indian citizen.</p>
                </div>
                """,
                unsafe_allow_html=True,
            )

            tab_login, tab_signup = st.tabs(
                ["Log in", "Create account"]
            )

            with tab_login:
                email = st.text_input(
                    "Email",
                    key="li_email",
                    placeholder="you@example.com",
                )
                password = st.text_input(
                    "Password",
                    type="password",
                    key="li_pw",
                    placeholder="Your password",
                )

                if st.button(
                    "Log in",
                    key="li_btn",
                    use_container_width=True,
                ):
                    if not email or not password:
                        st.warning("Enter email and password.")
                    else:
                        try:
                            response = requests.post(
                                f"{API_URL}/auth/login",
                                json={
                                    "email": email,
                                    "password": password,
                                },
                                timeout=10,
                            )

                            if response.status_code == 200:
                                data = response.json()
                                st.session_state.user = data["user"]
                                st.session_state.token = data["access_token"]
                                st.rerun()
                            else:
                                st.error(
                                    response.json().get(
                                        "detail", "Login failed"
                                    )
                                )
                        except Exception as exc:
                            st.error(f"Error: {exc}")

            with tab_signup:
                name = st.text_input(
                    "Full name",
                    key="su_name",
                    placeholder="Lakshmi",
                )
                email = st.text_input(
                    "Email",
                    key="su_email",
                    placeholder="lakshmi@example.com",
                )
                password = st.text_input(
                    "Password",
                    type="password",
                    key="su_pw",
                    placeholder="Min 8 characters",
                )

                if st.button(
                    "Create account",
                    key="su_btn",
                    use_container_width=True,
                ):
                    if not name or not email or not password:
                        st.warning("Fill all fields.")
                    elif len(password) < 8:
                        st.warning(
                            "Password must be at least 8 characters."
                        )
                    else:
                        try:
                            response = requests.post(
                                f"{API_URL}/auth/signup",
                                json={
                                    "email": email,
                                    "password": password,
                                    "full_name": name,
                                },
                                timeout=10,
                            )

                            if response.status_code == 201:
                                st.success(
                                    "Account created. Switch to Log in."
                                )
                            else:
                                st.error(
                                    response.json().get(
                                        "detail",
                                        "Email already registered",
                                    )
                                )
                        except Exception as exc:
                            st.error(f"Error: {exc}")

            st.markdown(
                f"<hr style='border-color:{BORDER};'>",
                unsafe_allow_html=True,
            )

            if st.button(
                "Continue as guest",
                use_container_width=True,
            ):
                st.session_state.user = {
                    "full_name": "Guest",
                    "role": "citizen",
                }
                st.rerun()


# -------------------- Query runner --------------------

def run_query(
    query: str,
    followup_answers: dict[str, str] | None = None,
):
    if not query.strip():
        st.warning("Please describe your situation.")
        return

    try:
        with st.spinner(
            "Understanding your request and preparing the next step..."
        ):
            result = run_pipeline(
                query,
                mode=st.session_state.page,
                followup_answers=followup_answers,
            )

    except Exception as exc:
        if (
            isinstance(exc, RuntimeError)
            and str(exc).startswith("The language service is busy")
        ):
            st.warning(
                "The language service is busy or its quota has been "
                "reached. Please retry later; your answers are still "
                "available."
            )
        else:
            st.error(
                "The request could not be completed. Please retry; "
                "your answers are still available."
            )
        return

    if result.get("needs_followup"):
        st.session_state.followup = {
            "questions": result.get("followup_questions", []),
            "original_query": query,
            "answers": followup_answers or {},
        }
        st.session_state.results = None
    else:
        st.session_state.followup = None
        st.session_state.results = result

    st.rerun()


# -------------------- Main application --------------------

def render_app():
    render_sidebar()
    render_hero()

    # Voice input and document upload
    with st.expander(
        "🎙️ Voice Input & 📄 Document Upload (Optional)"
    ):
        col_voice, col_ocr = st.columns(2)

        with col_voice:
            st.markdown(
                "**Record a voice message "
                "(Malayalam, Hindi, Tamil, English)**"
            )

            audio_value = st.audio_input(
                "Record a message",
                label_visibility="collapsed",
            )

            if audio_value:
                if st.button("Transcribe Audio"):
                    with st.spinner("Transcribing..."):
                        text = transcribe_audio(audio_value.read())

                    if text.lower().startswith(
                        ("error:", "voice error:")
                    ):
                        st.error(text)
                    else:
                        st.session_state[
                            st.session_state.page + "_q"
                        ] = text
                        st.session_state.voice_query = text
                        st.session_state.voice_text = text
                        st.rerun()

            if (
                st.session_state.voice_text
                and "Error" not in st.session_state.voice_text
            ):
                st.success("Extracted text")
                st.info(st.session_state.voice_text)

        with col_ocr:
            st.markdown("**Read printed English text from an image**")

            uploaded_file = st.file_uploader(
                "Upload Image",
                type=["jpg", "jpeg", "png"],
                label_visibility="collapsed",
            )

            if uploaded_file:
                if st.button("Read Document"):
                    with st.spinner("Reading document..."):
                        extracted = extract_text_from_image(
                            uploaded_file.read()
                        )

                    if extracted.lower().startswith("ocr error:"):
                        st.error(extracted)
                    else:
                        st.session_state[
                            st.session_state.page + "_q"
                        ] = extracted
                        st.session_state.voice_query = extracted
                        st.session_state.voice_text = extracted
                        st.rerun()

    # Follow-up questions
    if st.session_state.followup:
        st.info(
            "To give you the best guidance, "
            "I need a little more information:"
        )

        pending = st.session_state.followup
        answers = dict(pending.get("answers", {}))

        with st.form("followup_form"):
            current_answers = {}

            for question in pending["questions"]:
                current_answers[question] = st.text_input(
                    question,
                    value=answers.get(question, ""),
                    key=(
                        f"fu_{st.session_state.page}_"
                        f"{pending['original_query']}_{question}"
                    ),
                )

            submitted = st.form_submit_button("Submit Answers")

        if submitted:
            if not any(
                answer.strip()
                for answer in current_answers.values()
            ):
                st.warning(
                    "Please answer at least one question so I can continue."
                )
            else:
                answers.update({
                    question: answer.strip()
                    for question, answer in current_answers.items()
                    if answer.strip()
                })

                run_query(
                    pending["original_query"],
                    followup_answers=answers,
                )

        return

    # Main query
    if st.session_state.page == "scheme":
        query = st.text_area(
            "Describe your situation",
            value=st.session_state.get("voice_query", ""),
            height=110,
            placeholder=(
                "Example: I am 68 years old, my husband passed away, "
                "and I need financial support."
            ),
            label_visibility="collapsed",
            key="scheme_q",
        )

        if st.button("Get Plan", key="scheme_btn"):
            st.session_state.results = None
            run_query(query)

    elif st.session_state.page == "mentor":
        query = st.text_area(
            "What guidance do you need?",
            value=st.session_state.get("voice_query", ""),
            height=110,
            placeholder=(
                "Example: I'm 17, finished 12th, "
                "and want to work in Saudi Arabia."
            ),
            label_visibility="collapsed",
            key="mentor_q",
        )

        if st.button("Get Guidance", key="mentor_btn"):
            st.session_state.results = None
            run_query(query)

    if st.session_state.results:
        render_results(st.session_state.results)


# -------------------- Entry point --------------------

if not st.session_state.user:
    render_auth()
else:
    render_app()
