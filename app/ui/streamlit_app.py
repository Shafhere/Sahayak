"""Sahayak Streamlit UI — Premium layout with Voice & OCR."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

import requests
import streamlit as st

from app.tools.voice import transcribe_audio
from app.tools.ocr import extract_text_from_image
from app.workflows.graph import run_pipeline
from app.agents.understanding import understand
from app.ui.report import generate_html_report

API_URL = "http://localhost:8000"

st.set_page_config(
    page_title="Sahayak",
    page_icon="🤝",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─── Session defaults ───────────────────────────────────────
defaults = {
    "user": None, "token": None, "theme": "light", "page": "scheme", 
    "results": None, "followup": None, "voice_query": "", "voice_text": ""
}
for k, v in defaults.items():
    if k not in st.session_state:
        st.session_state[k] = v

DARK = st.session_state.theme == "dark"

# ─── Palettes ───────────────────────────────────────────────
if DARK:
    BG, SIDEBAR_BG, CARD_BG, HERO_BG = "#0C1317", "#111A1E", "#1A2328", "#173333"
    TEXT, MUTED, ACCENT, BORDER = "#E2E8F0", "#94A3B8", "#E07856", "#2D3748"
else:
    BG, SIDEBAR_BG, CARD_BG, HERO_BG = "#FDFBF7", "#194C4A", "#FFFFFF", "#194C4A"
    TEXT, MUTED, ACCENT, BORDER = "#1A202C", "#718096", "#D97757", "#E2E8F0"

# ─── CSS Overrides ──────────────────────────────────────────
st.markdown(f"""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Lora:wght@500;600&family=Inter:wght@400;500;600&display=swap');

    .stApp {{ background-color: {BG} !important; }}
    html, body, [class*="css"] {{ font-family: 'Inter', sans-serif; color: {TEXT} !important; }}
    
    header[data-testid="stHeader"] {{ background: transparent !important; }}
    #MainMenu, footer {{ visibility: hidden; }}
    .block-container {{ padding-top: 2rem !important; max-width: 1100px !important; }}

    [data-testid="stSidebar"] {{ background-color: {SIDEBAR_BG} !important; }}
    [data-testid="stSidebar"] * {{ color: #FFFFFF !important; }}
    [data-testid="stSidebar"] .stButton > button {{
        background: transparent !important; border: none !important; text-align: left !important;
        padding: 10px 16px !important; font-size: 15px !important; border-radius: 8px !important;
        justify-content: flex-start !important;
    }}
    [data-testid="stSidebar"] .stButton > button:hover {{ background: rgba(255,255,255,0.1) !important; }}
    [data-testid="stSidebar"] button[kind="primary"] {{ background: rgba(255,255,255,0.15) !important; font-weight: 600 !important; }}

    h1, h2, h3 {{ font-family: 'Lora', serif !important; color: {TEXT} !important; }}

    .stTextInput input, .stTextArea textarea {{
        background: {BG} !important; color: {TEXT} !important;
        border: 1px solid {BORDER} !important; border-radius: 10px !important; font-size: 15px !important;
    }}
    .stButton > button {{
        background: {ACCENT} !important; color: #FFFFFF !important;
        border: none !important; border-radius: 10px !important; font-weight: 500 !important;
    }}

    [data-testid="stVerticalBlockBorderWrapper"] {{
        background-color: {CARD_BG} !important; border: 1px solid {BORDER} !important;
        border-radius: 16px !important; padding: 24px !important; box-shadow: 0 2px 10px rgba(0,0,0,0.02);
    }}

    .stTabs [data-baseweb="tab-list"] {{ background: transparent !important; border-bottom: 1px solid {BORDER}; gap: 24px; }}
    .stTabs [data-baseweb="tab"] {{ color: {MUTED} !important; padding: 10px 0 !important; font-weight: 500 !important; }}
    .stTabs [aria-selected="true"] {{ color: {TEXT} !important; border-bottom: 2px solid {ACCENT} !important; }}
    .stTabs [data-baseweb="tab-highlight"], .stTabs [data-baseweb="tab-border"] {{ display: none; }}

    .hero-container {{ background-color: {HERO_BG}; border-radius: 20px; padding: 40px; margin-bottom: 30px; }}
    .hero-title {{ font-family: 'Lora', serif; font-size: 32px; font-weight: 600; color: #FFFFFF !important; margin: 0 0 12px 0; }}
    .hero-sub {{ font-size: 16px; color: #D1D5DB !important; margin: 0; }}
    
    .greeting {{
        font-family: 'Lora', serif; font-size: 20px; line-height: 1.6; color: {TEXT};
        margin-bottom: 32px; padding-left: 20px; border-left: 4px solid {ACCENT};
    }}
    .section-label {{ font-size: 12px; font-weight: 600; color: {ACCENT} !important; text-transform: uppercase; letter-spacing: 1.5px; margin-bottom: 16px; }}
    .stat-box {{ text-align: center; padding: 10px; }}
    .stat-value {{ font-family: 'Lora', serif; font-size: 32px; font-weight: 600; color: {ACCENT} !important; margin: 0; }}
    .stat-label {{ font-size: 13px; color: {MUTED} !important; margin-top: 4px; }}
    
    .benefit-box {{ background: {HERO_BG}; border-radius: 16px; padding: 24px; text-align: center; margin-bottom: 24px; }}
    .benefit-value {{ font-family: 'Lora', serif; font-size: 42px; font-weight: 600; color: #FFFFFF !important; margin: 0; }}
    .benefit-label {{ font-size: 13px; color: #D1D5DB !important; text-transform: uppercase; letter-spacing: 1px; margin-top: 4px; }}

    .timeline-item {{ display: flex; gap: 16px; padding: 16px 0; border-bottom: 1px solid {BORDER}; }}
    .timeline-item:last-child {{ border-bottom: none; }}
    .timeline-num {{ background: {BG}; color: {TEXT}; width: 30px; height: 30px; border-radius: 50%; display: flex; align-items: center; justify-content: center; font-size: 13px; font-weight: 600; flex-shrink: 0; border: 1px solid {BORDER}; }}
    .timeline-text {{ font-weight: 500; font-size: 15px; color: {TEXT}; margin: 0; }}
    .timeline-time {{ font-size: 13px; color: {MUTED}; margin-top: 4px; }}
</style>
""", unsafe_allow_html=True)


# ─── Helper Components ──────────────────────────────────────
def render_sidebar():
    with st.sidebar:
        st.markdown(f'''
        <div style="display:flex; align-items:center; gap:12px; padding:10px 0 30px 10px;">
            <div style="background:{ACCENT}; width:40px; height:40px; border-radius:12px; display:flex; align-items:center; justify-content:center; font-size:20px;">🤝</div>
            <div>
                <div style="font-family:'Lora', serif; font-size:18px; font-weight:600; line-height:1.1;">Sahayak</div>
                <div style="font-size:11px; color:rgba(255,255,255,0.7); margin-top:2px;">Citizen Companion</div>
            </div>
        </div>
        ''', unsafe_allow_html=True)

        if st.button("🏠  Scheme", use_container_width=True, type="primary" if st.session_state.page == "scheme" else "secondary"):
            st.session_state.page = "scheme"
            st.session_state.results = None
            st.session_state.followup = None
            st.rerun()

        if st.button("🎓  Mentor", use_container_width=True, type="primary" if st.session_state.page == "mentor" else "secondary"):
            st.session_state.page = "mentor"
            st.session_state.results = None
            st.session_state.followup = None
            st.rerun()

        st.markdown("<hr style='border-color:rgba(255,255,255,0.1)'>", unsafe_allow_html=True)
        
        st.markdown(f'''
        <div style="padding:10px; background:rgba(0,0,0,0.1); border-radius:8px; margin-bottom:10px;">
            <div style="font-size:14px; font-weight:500;">👤 {st.session_state.user.get('full_name', 'Guest')}</div>
        </div>
        ''', unsafe_allow_html=True)

        c1, c2 = st.columns(2)
        with c1:
            icon = "☀️" if DARK else "🌙"
            if st.button(icon, key="theme_btn", help="Toggle theme", use_container_width=True):
                st.session_state.theme = "light" if DARK else "dark"
                st.rerun()
        with c2:
            if st.button("🚪 Exit", key="logout_btn", use_container_width=True):
                st.session_state.user = None
                st.session_state.token = None
                st.session_state.results = None
                st.session_state.followup = None
                st.rerun()

def render_hero():
    st.markdown(f'''
    <div class="hero-container">
        <div class="hero-title">Namaskaram, welcome.</div>
        <div class="hero-sub">Take a calm moment today. Let's find the government schemes and support you deserve.</div>
    </div>
    ''', unsafe_allow_html=True)


# ─── Auth Page ──────────────────────────────────────────────
def render_auth():
    c1, c2, c3 = st.columns([1, 1.2, 1])
    with c2:
        st.markdown("<div style='height: 5vh'></div>", unsafe_allow_html=True)
        
        with st.container(border=True):
            st.markdown(f'''
            <div style="text-align:center; margin-bottom:30px;">
                <div style="background:{ACCENT}; width:56px; height:56px; border-radius:16px; display:inline-flex; align-items:center; justify-content:center; font-size:28px; margin-bottom:16px;">🤝</div>
                <h1 style="font-family:'Lora', serif; font-size:32px; font-weight:600; color:{TEXT}; margin:0;">Sahayak</h1>
                <p style="color:{MUTED}; margin-top:8px; font-size:15px;">A companion for every Indian citizen.</p>
            </div>
            ''', unsafe_allow_html=True)

            tab_login, tab_signup = st.tabs(["Log in", "Create account"])

            with tab_login:
                email = st.text_input("Email", key="li_email", placeholder="you@example.com")
                pw = st.text_input("Password", type="password", key="li_pw", placeholder="Your password")
                if st.button("Log in", key="li_btn", use_container_width=True):
                    if not email or not pw:
                        st.warning("Enter email and password.")
                    else:
                        try:
                            r = requests.post(f"{API_URL}/auth/login", json={"email": email, "password": pw}, timeout=10)
                            if r.status_code == 200:
                                d = r.json()
                                st.session_state.user = d["user"]
                                st.session_state.token = d["access_token"]
                                st.rerun()
                            else:
                                st.error(r.json().get("detail", "Login failed"))
                        except Exception as e:
                            st.error(f"Error: {e}")

            with tab_signup:
                name = st.text_input("Full name", key="su_name", placeholder="Lakshmi")
                email = st.text_input("Email", key="su_email", placeholder="lakshmi@example.com")
                pw = st.text_input("Password", type="password", key="su_pw", placeholder="Min 6 characters")
                if st.button("Create account", key="su_btn", use_container_width=True):
                    if not name or not email or not pw:
                        st.warning("Fill all fields.")
                    elif len(pw) < 6:
                        st.warning("Password must be at least 6 characters.")
                    else:
                        try:
                            r = requests.post(f"{API_URL}/auth/signup", json={"email": email, "password": pw, "full_name": name}, timeout=10)
                            if r.status_code == 201:
                                st.success("Account created. Switch to Log in.")
                            else:
                                st.error(r.json().get("detail", "Email already registered"))
                        except Exception as e:
                            st.error(f"Error: {e}")
            
            st.markdown("<hr style='border-color:" + BORDER + ";'>", unsafe_allow_html=True)
            if st.button("Continue as guest", use_container_width=True):
                st.session_state.user = {"full_name": "Guest", "role": "citizen"}
                st.rerun()


# ─── Results Renderer ───────────────────────────────────────
def render_results(result: dict):
    profile = result.get("profile")
    research = result.get("research")
    plan = result.get("plan")
    verdict = result.get("verdict")

    if not profile or not plan:
        st.error("No result. Try rephrasing your query.")
        return

    st.markdown("<hr style='border-color:" + BORDER + "; margin:30px 0;'>", unsafe_allow_html=True)

    greeting = getattr(plan, "greeting", "") or "Here is your personalized plan."
    st.markdown(f'<div class="greeting">{greeting}</div>', unsafe_allow_html=True)

    c1, c2, c3 = st.columns(3)
    with c1:
        with st.container(border=True):
            st.markdown(f'<div class="stat-box"><p class="stat-value">{len(plan.eligible_schemes)}</p><p class="stat-label">Schemes / Courses</p></div>', unsafe_allow_html=True)
    with c2:
        with st.container(border=True):
            st.markdown(f'<div class="stat-box"><p class="stat-value">{len(plan.document_checklist)}</p><p class="stat-label">Documents Needed</p></div>', unsafe_allow_html=True)
    with c3:
        with st.container(border=True):
            st.markdown(f'<div class="stat-box"><p class="stat-value">{len(plan.timeline)}</p><p class="stat-label">Timeline Steps</p></div>', unsafe_allow_html=True)

    st.markdown("<div style='height: 20px;'></div>", unsafe_allow_html=True)

    if plan.estimated_annual_benefit > 0:
        st.markdown(f'''
        <div class="benefit-box">
            <p class="benefit-value">₹{plan.estimated_annual_benefit:,}</p>
            <p class="benefit-label">Estimated Annual Benefit</p>
        </div>
        ''', unsafe_allow_html=True)

    col_left, col_right = st.columns([1.3, 1], gap="large")

    with col_left:
        st.markdown('<div class="section-label">Opportunities & Pathways</div>', unsafe_allow_html=True)
        for s in plan.eligible_schemes:
            with st.container(border=True):
                st.markdown(f'''
                <div style="font-family:'Lora', serif; font-size:20px; font-weight:600; color:{TEXT}; margin-bottom:8px;">{s.name}</div>
                <div style="font-size:14px; color:{MUTED}; margin:4px 0;"><strong>Details:</strong> {s.benefits or "See source"}</div>
                <div style="font-size:14px; color:{MUTED};"><strong>Deadline:</strong> {s.deadline or "Rolling"}</div>
                ''', unsafe_allow_html=True)

        st.markdown('<div class="section-label" style="margin-top:30px;">Roadmap / Timeline</div>', unsafe_allow_html=True)
        with st.container(border=True):
            for i, s in enumerate(plan.timeline, 1):
                st.markdown(f'''
                <div class="timeline-item">
                    <div class="timeline-num">{i}</div>
                    <div>
                        <p class="timeline-text">{s.step}</p>
                        <div class="timeline-time">{s.time_estimate}</div>
                    </div>
                </div>
                ''', unsafe_allow_html=True)

    with col_right:
        st.markdown('<div class="section-label">Documents Needed</div>', unsafe_allow_html=True)
        with st.container(border=True):
            for i, d in enumerate(plan.document_checklist):
                st.checkbox(d, key=f"doc_{i}")

        st.markdown('<div class="section-label" style="margin-top:20px;">Next Steps</div>', unsafe_allow_html=True)
        with st.container(border=True):
            for step in plan.next_steps:
                st.markdown(f"<div style='margin-bottom:12px; font-size:14px; line-height:1.4;'>→ {step}</div>", unsafe_allow_html=True)

        st.markdown("<div style='height: 16px'></div>", unsafe_allow_html=True)
        html = generate_html_report(profile, plan)
        st.download_button("Download Full Report", data=html, file_name=f"sahayak_{profile.mode}.html", mime="text/html", use_container_width=True)


# ─── Query Runner ──────────────────────────────────────────
def run_query(query: str, is_followup: bool = False):
    if not query.strip():
        st.warning("Please describe your situation.")
        return
    
    st.markdown("<div style='height: 10px;'></div>", unsafe_allow_html=True)
    p = st.progress(0)
    s = st.empty()
    
    try:
        if not is_followup:
            s.info("Understanding your request...")
            p.progress(20)
            
            profile = understand(query)
            
            if getattr(profile, "needs_followup", False):
                p.empty()
                s.empty()
                st.session_state.followup = {
                    "questions": profile.followup_questions,
                    "original_query": query
                }
                return 
                
        s.info("Researching and building your plan (10–30s)...")
        p.progress(50)
        
        result = run_pipeline(query)
        
        p.progress(100)
        p.empty()
        s.empty()
        
        st.session_state.results = result
    except Exception as e:
        p.empty()
        s.empty()
        st.error(str(e))

# ─── Main App ──────────────────────────────────────────────
def render_app():
    render_sidebar()
    render_hero()

    # --- VOICE & OCR EXPANDER ---
    with st.expander("🎤 Voice Input & 📄 Document Upload (Optional)"):
        col_v, col_o = st.columns(2)
        
        with col_v:
            st.markdown("**Record a voice message (Malayalam, Hindi, English)**")
            audio_value = st.audio_input("Record a message", label_visibility="collapsed")
            if audio_value:
                if st.button("Transcribe Audio"):
                    with st.spinner("Transcribing..."):
                        text = transcribe_audio(audio_value.read())
                        if "Error" in text:
                            st.error(text)
                        else:
                            st.session_state.voice_query = text
                            st.session_state.voice_text = text
                            st.rerun()
                        
            # SHOW THE EXTRACTED TEXT
            if st.session_state.voice_text and "Error" not in st.session_state.voice_text:
                st.success("✅ Extracted Text:")
                st.info(st.session_state.voice_text)
        
        with col_o:
            st.markdown("**Upload a document (ID, Certificate)**")
            uploaded_file = st.file_uploader("Upload Image", type=["jpg", "jpeg", "png"], label_visibility="collapsed")
            if uploaded_file:
                if st.button("Read Document"):
                    with st.spinner("Reading document..."):
                        extracted = extract_text_from_image(uploaded_file.read())
                        if "Error" in extracted:
                            st.error(extracted)
                        else:
                            st.session_state.voice_query = extracted
                            st.session_state.voice_text = extracted
                            st.rerun()
    # ---------------------------
    # ---------------------------

    # --- FOLLOW-UP UI ---
    if st.session_state.followup:
        st.info("To give you the best guidance, I need a little more information:")
        
        answers = []
        for i, q in enumerate(st.session_state.followup["questions"]):
            ans = st.text_input(q, key=f"fu_q_{i}")
            answers.append(ans)
            
        if st.button("Submit Answers"):
            combined_query = st.session_state.followup["original_query"] + ". "
            for q, a in zip(st.session_state.followup["questions"], answers):
                if a:
                    combined_query += f"{q} {a}. "
            
            st.session_state.followup = None
            run_query(combined_query, is_followup=True) 
        return 

    # --- MAIN UI ---
    if st.session_state.page == "scheme":
        query = st.text_area(
            "Describe your situation", 
            value=st.session_state.get("voice_query", ""),
            height=120, 
            placeholder="Example: എന്റെ അമ്മൂമ്മ 68 വയസ്സ്, വിധവ, കേരളത്തിൽ", 
            label_visibility="collapsed", 
            key="scheme_q"
        )
        if st.button("Get Plan", key="scheme_btn"):
            st.session_state.results = None
            run_query(query)

    elif st.session_state.page == "mentor":
        query = st.text_area(
            "What guidance do you need?", 
            value=st.session_state.get("voice_query", ""),
            height=120, 
            placeholder="Example: I'm 17, finished 12th, want to work in Saudi Arabia", 
            label_visibility="collapsed", 
            key="mentor_q"
        )
        if st.button("Get Guidance", key="mentor_btn"):
            st.session_state.results = None
            run_query(query)

    if st.session_state.results:
        render_results(st.session_state.results)


# ─── Entry Point ───────────────────────────────────────────
if not st.session_state.user:
    render_auth()
else:
    render_app()