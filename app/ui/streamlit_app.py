"""Sahayak Streamlit UI — Premium Noor-style layout."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

import requests
import streamlit as st

from app.workflows.graph import run_pipeline
from app.ui.report import generate_html_report

API_URL = "http://localhost:8000"

st.set_page_config(
    page_title="Sahayak",
    page_icon="🤝",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─── Session defaults ───────────────────────────────────────
defaults = {"user": None, "token": None, "theme": "light", "page": "scheme", "results": None}
for k, v in defaults.items():
    if k not in st.session_state:
        st.session_state[k] = v

DARK = st.session_state.theme == "dark"

# ─── Palettes (Extracted from reference) ────────────────────
if DARK:
    BG = "#0C1317"             # Deep dark slate
    SIDEBAR_BG = "#111A1E"     # Slightly lighter slate
    CARD_BG = "#111A1E"
    HERO_BG = "#173333"        # Dark Teal
    TEXT = "#E2E8F0"           # Soft white
    MUTED = "#94A3B8"          # Muted gray
    ACCENT = "#E07856"         # Terracotta
    ACCENT_GOLD = "#E5B978"    # Gold
    BORDER = "#1E293B"
    INPUT_BG = "#111A1E"
else:
    BG = "#FDFBF7"             # Warm cream
    SIDEBAR_BG = "#194C4A"     # Deep Teal (exact match)
    CARD_BG = "#FFFFFF"        # Pure white
    HERO_BG = "#194C4A"        # Deep Teal
    TEXT = "#1A202C"           # Dark slate
    MUTED = "#718096"          # Gray
    ACCENT = "#D97757"         # Terracotta
    ACCENT_GOLD = "#D4AF37"    # Gold
    BORDER = "#E2E8F0"
    INPUT_BG = "#FFFFFF"

# ─── CSS & Fonts ────────────────────────────────────────────
st.markdown(f"""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Lora:ital,wght@0,400;0,500;0,600;1,400&family=Inter:wght@400;500;600&display=swap');

    /* Base Setup */
    html, body, [class*="css"] {{
        font-family: 'Inter', sans-serif;
    }}
    .stApp {{
        background-color: {BG} !important;
        color: {TEXT} !important;
    }}
    .stApp * {{
        color: {TEXT};
    }}
    
    /* Hide Streamlit chrome */
    #MainMenu, footer, header[data-testid="stHeader"] {{ visibility: hidden; }}
    header[data-testid="stHeader"] {{ height: 0; }}
    
    /* Main Container Alignment */
    .block-container {{
        padding-top: 2rem !important;
        padding-bottom: 3rem !important;
        max-width: 1100px !important;
    }}

    /* Sidebar Styling */
    section[data-testid="stSidebar"] {{
        background-color: {SIDEBAR_BG} !important;
        border-right: none;
    }}
    section[data-testid="stSidebar"] * {{
        color: #FFFFFF !important;
    }}
    /* Sidebar Buttons */
    section[data-testid="stSidebar"] button {{
        background: transparent !important;
        border: none !important;
        text-align: left !important;
        padding: 12px 16px !important;
        font-size: 15px !important;
        border-radius: 10px !important;
        justify-content: flex-start !important;
        margin-bottom: 4px;
    }}
    section[data-testid="stSidebar"] button:hover {{
        background: rgba(255,255,255,0.08) !important;
    }}
    section[data-testid="stSidebar"] button[kind="primary"] {{
        background: rgba(255,255,255,0.15) !important;
        font-weight: 500 !important;
    }}

    /* Top Navigation Bar */
    .top-nav {{
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 2rem;
        padding: 0 10px;
    }}
    .top-nav-title {{
        font-family: 'Lora', serif;
        font-size: 18px;
        font-weight: 600;
        color: {TEXT};
        position: absolute;
        left: 50%;
        transform: translateX(-50%);
    }}

    /* Hero Banner (The large teal box) */
    .hero-container {{
        background-color: {HERO_BG};
        border-radius: 24px;
        padding: 40px;
        margin-bottom: 30px;
        position: relative;
        overflow: hidden;
        box-shadow: 0 4px 20px rgba(0,0,0,0.05);
    }}
    /* Subtle decorative circle in hero */
    .hero-container::after {{
        content: "";
        position: absolute;
        right: -50px;
        top: -50px;
        width: 250px;
        height: 250px;
        border-radius: 50%;
        background: rgba(255,255,255,0.03);
    }}
    .hero-container::before {{
        content: "";
        position: absolute;
        right: 50px;
        bottom: -80px;
        width: 300px;
        height: 300px;
        border-radius: 50%;
        border: 40px solid rgba(255,255,255,0.02);
    }}
    .hero-title {{
        font-family: 'Lora', serif;
        font-size: 34px;
        font-weight: 600;
        color: #FFFFFF !important;
        margin: 0 0 12px 0;
        position: relative;
        z-index: 2;
    }}
    .hero-sub {{
        font-size: 16px;
        color: #D1D5DB !important;
        margin: 0;
        max-width: 600px;
        line-height: 1.5;
        position: relative;
        z-index: 2;
    }}

    /* Form Inputs */
    .stTextInput input, .stTextArea textarea {{
        background: {INPUT_BG} !important;
        color: {TEXT} !important;
        border: 1px solid {BORDER} !important;
        border-radius: 12px !important;
        font-size: 15px !important;
        padding: 14px 16px !important;
        box-shadow: 0 1px 3px rgba(0,0,0,0.02);
    }}
    .stTextInput input:focus, .stTextArea textarea:focus {{
        border-color: {ACCENT} !important;
        box-shadow: 0 0 0 3px {ACCENT}22 !important;
    }}
    .stTextInput label, .stTextArea label {{ color: {TEXT} !important; font-weight: 500 !important; }}

    /* Primary Button */
    .stButton > button {{
        background: {ACCENT} !important;
        color: #FFFFFF !important;
        border: none !important;
        border-radius: 10px !important;
        padding: 10px 24px !important;
        font-weight: 500 !important;
        font-size: 15px !important;
        transition: all 0.2s;
    }}
    .stButton > button:hover {{
        background: #C66545 !important;
        color: #FFFFFF !important;
    }}
    .stButton > button[kind="secondary"] {{
        background: transparent !important;
        color: {TEXT} !important;
        border: 1px solid {BORDER} !important;
    }}
    .stButton > button[kind="secondary"]:hover {{
        background: {BORDER}44 !important;
    }}

    /* Tabs */
    .stTabs [data-baseweb="tab-list"] {{
        background: transparent !important;
        border-bottom: 2px solid {BORDER};
        gap: 32px;
        padding: 0;
    }}
    .stTabs [data-baseweb="tab"] {{
        color: {MUTED} !important;
        padding: 10px 0 !important;
        font-weight: 500 !important;
        background: transparent !important;
    }}
    .stTabs [aria-selected="true"] {{
        color: {TEXT} !important;
        border-bottom: 2px solid {ACCENT} !important;
    }}
    .stTabs [data-baseweb="tab-highlight"] {{ display: none; }}

    /* Custom Cards */
    .card {{
        background: {CARD_BG};
        border: 1px solid {BORDER};
        border-radius: 20px;
        padding: 24px;
        margin-bottom: 20px;
        box-shadow: 0 2px 12px rgba(0,0,0,0.02);
    }}
    
    /* Text utilities */
    .section-label {{
        font-size: 12px;
        font-weight: 600;
        color: {ACCENT_GOLD} !important;
        text-transform: uppercase;
        letter-spacing: 1.5px;
        margin-bottom: 16px;
    }}
    .serif-title {{
        font-family: 'Lora', serif;
        font-size: 22px;
        font-weight: 600;
        color: {TEXT} !important;
        margin: 0 0 8px 0;
    }}

    /* Stats Row (The 3 boxes) */
    .stat-box {{
        background: {CARD_BG};
        border: 1px solid {BORDER};
        border-radius: 16px;
        padding: 20px;
        text-align: center;
        box-shadow: 0 1px 4px rgba(0,0,0,0.02);
    }}
    .stat-value {{
        font-family: 'Lora', serif;
        font-size: 32px;
        font-weight: 600;
        color: {ACCENT} !important;
        margin: 0;
    }}
    .stat-label {{
        font-size: 13px;
        color: {MUTED} !important;
        margin-top: 4px;
    }}

    /* Benefit Box */
    .benefit-box {{
        background: {HERO_BG};
        border-radius: 16px;
        padding: 24px;
        text-align: center;
        margin-bottom: 24px;
    }}
    .benefit-value {{
        font-family: 'Lora', serif;
        font-size: 42px;
        font-weight: 600;
        color: #FFFFFF !important;
        margin: 0;
    }}
    .benefit-label {{
        font-size: 13px;
        color: #D1D5DB !important;
        text-transform: uppercase;
        letter-spacing: 1px;
        margin-top: 4px;
    }}

    /* Timeline */
    .timeline-item {{
        display: flex;
        gap: 16px;
        padding: 16px 0;
        border-bottom: 1px solid {BORDER};
    }}
    .timeline-item:last-child {{ border-bottom: none; }}
    .timeline-num {{
        background: {BG};
        color: {TEXT};
        width: 30px;
        height: 30px;
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 13px;
        font-weight: 600;
        flex-shrink: 0;
        border: 1px solid {BORDER};
    }}
    .timeline-text {{
        font-weight: 500;
        font-size: 15px;
        color: {TEXT};
        margin: 0;
    }}
    .timeline-time {{
        font-size: 13px;
        color: {MUTED};
        margin-top: 4px;
    }}

    /* Greeting */
    .greeting {{
        font-family: 'Lora', serif;
        font-size: 20px;
        line-height: 1.6;
        color: {TEXT};
        margin-bottom: 32px;
        padding-left: 20px;
        border-left: 4px solid {ACCENT};
    }}
    
    /* Expanders */
    .streamlit-expanderHeader {{
        background: {CARD_BG} !important;
        border: 1px solid {BORDER};
        border-radius: 12px !important;
        color: {TEXT} !important;
    }}
    .stCheckbox label {{ color: {TEXT} !important; }}
</style>
""", unsafe_allow_html=True)


# ─── Helper Renderers ───────────────────────────────────────
def render_sidebar():
    with st.sidebar:
        # Brand Logo
        st.markdown(f'''
        <div style="display:flex; align-items:center; gap:14px; padding:10px 0 40px 10px;">
            <div style="background:{ACCENT}; width:44px; height:44px; border-radius:14px; display:flex; align-items:center; justify-content:center; font-size:22px; box-shadow: 0 4px 10px rgba(0,0,0,0.1);">🤝</div>
            <div>
                <div style="font-family:'Lora', serif; font-size:20px; font-weight:600; line-height:1.1;">Sahayak</div>
                <div style="font-size:12px; color:rgba(255,255,255,0.7); margin-top:2px;">Citizen Companion</div>
            </div>
        </div>
        ''', unsafe_allow_html=True)

        # Nav Links
        if st.button("🏠  Scheme", use_container_width=True, type="primary" if st.session_state.page == "scheme" else "secondary"):
            st.session_state.page = "scheme"
            st.session_state.results = None
            st.rerun()

        if st.button("🎓  Mentor", use_container_width=True, type="primary" if st.session_state.page == "mentor" else "secondary"):
            st.session_state.page = "mentor"
            st.session_state.results = None
            st.rerun()

        if st.button("📜  History", use_container_width=True, type="secondary"):
            st.toast("History coming soon!")

        st.markdown("<div style='height: 30px;'></div>", unsafe_allow_html=True)
        
        # User Profile Block
        st.markdown(f'''
        <div style="padding:16px; background:rgba(0,0,0,0.1); border-radius:12px; margin-bottom:16px;">
            <div style="display:flex; align-items:center; gap:10px;">
                <div style="background:rgba(255,255,255,0.2); width:32px; height:32px; border-radius:50%; display:flex; align-items:center; justify-content:center;">👤</div>
                <div>
                    <div style="font-size:14px; font-weight:500;">{st.session_state.user.get('full_name', 'Guest')}</div>
                    <div style="font-size:11px; color:rgba(255,255,255,0.7);">{st.session_state.user.get('role', 'citizen').capitalize()}</div>
                </div>
            </div>
        </div>
        ''', unsafe_allow_html=True)
        
        if st.button("Log out", key="logout_btn", use_container_width=True, type="secondary"):
            st.session_state.user = None
            st.session_state.token = None
            st.session_state.results = None
            st.rerun()

def render_top_nav():
    c1, c2, c3 = st.columns([1, 2, 1])
    with c2:
        st.markdown('<div class="top-nav-title">Home</div>', unsafe_allow_html=True)
    with c3:
        # Theme toggle pushed to the right
        col_a, col_b = st.columns([4, 1])
        with col_b:
            icon = "☀️" if DARK else "🌙"
            if st.button(icon, key="theme_btn", help="Toggle theme"):
                st.session_state.theme = "light" if DARK else "dark"
                st.rerun()

def render_hero():
    st.markdown(f'''
    <div class="hero-container">
        <div class="hero-title">നമസ്കാരം, welcome.</div>
        <div class="hero-sub">Take a calm moment today. Let's find the government schemes and support you deserve.</div>
    </div>
    ''', unsafe_allow_html=True)


# ─── Auth Page ──────────────────────────────────────────────
def render_auth():
    st.markdown("<div style='height: 60px'></div>", unsafe_allow_html=True)
    c1, c2, c3 = st.columns([1, 1.2, 1])
    with c2:
        st.markdown(f'''
        <div style="text-align:center; margin-bottom:40px;">
            <div style="background:{ACCENT}; width:64px; height:64px; border-radius:20px; display:inline-flex; align-items:center; justify-content:center; font-size:32px; margin-bottom:20px; box-shadow: 0 10px 20px rgba(217,119,87,0.2);">🤝</div>
            <h1 style="font-family:'Lora', serif; font-size:36px; font-weight:600; color:{TEXT}; margin:0;">Sahayak</h1>
            <p style="color:{MUTED}; margin-top:8px; font-size:16px;">A companion for every Indian citizen.</p>
        </div>
        ''', unsafe_allow_html=True)

        st.markdown('<div class="card" style="padding:32px;">', unsafe_allow_html=True)
        tab_login, tab_signup = st.tabs(["Log in", "Create account"])

        with tab_login:
            email = st.text_input("Email", key="li_email", placeholder="you@example.com")
            pw = st.text_input("Password", type="password", key="li_pw", placeholder="Your password")
            st.markdown("<div style='height: 10px;'></div>", unsafe_allow_html=True)
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
            st.markdown("<div style='height: 10px;'></div>", unsafe_allow_html=True)
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
        st.markdown('</div>', unsafe_allow_html=True)

        st.markdown("<div style='height: 16px'></div>", unsafe_allow_html=True)
        if st.button("Continue as guest", use_container_width=True, type="secondary"):
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

    st.markdown("<hr style='border:1px solid " + BORDER + "; margin:30px 0;'>", unsafe_allow_html=True)

    # Greeting
    greeting = getattr(plan, "greeting", "") or "Here is your personalized plan."
    st.markdown(f'<div class="greeting">{greeting}</div>', unsafe_allow_html=True)

    # Stats Row
    c1, c2, c3 = st.columns(3)
    with c1:
        st.markdown(f'<div class="stat-box"><p class="stat-value">{len(plan.eligible_schemes)}</p><p class="stat-label">Schemes Found</p></div>', unsafe_allow_html=True)
    with c2:
        st.markdown(f'<div class="stat-box"><p class="stat-value">{len(plan.document_checklist)}</p><p class="stat-label">Documents Needed</p></div>', unsafe_allow_html=True)
    with c3:
        st.markdown(f'<div class="stat-box"><p class="stat-value">{len(plan.timeline)}</p><p class="stat-label">Timeline Steps</p></div>', unsafe_allow_html=True)

    st.markdown("<div style='height: 20px;'></div>", unsafe_allow_html=True)

    # Benefit Banner
    if plan.estimated_annual_benefit > 0:
        st.markdown(f'''
        <div class="benefit-box">
            <p class="benefit-value">₹{plan.estimated_annual_benefit:,}</p>
            <p class="benefit-label">Estimated Annual Benefit</p>
        </div>
        ''', unsafe_allow_html=True)

    # 2-column layout
    col_left, col_right = st.columns([1.3, 1], gap="large")

    with col_left:
        st.markdown('<div class="section-label">Eligible Schemes</div>', unsafe_allow_html=True)
        for s in plan.eligible_schemes:
            st.markdown(f'''
            <div class="card">
                <div class="serif-title">{s.name}</div>
                <div style="font-size:14px; color:{MUTED}; margin:4px 0;"><strong>Benefits:</strong> {s.benefits or "See source"}</div>
                <div style="font-size:14px; color:{MUTED};"><strong>Deadline:</strong> {s.deadline or "Rolling"}</div>
            </div>
            ''', unsafe_allow_html=True)

        st.markdown('<div class="section-label" style="margin-top:30px;">Timeline</div>', unsafe_allow_html=True)
        st.markdown('<div class="card" style="padding: 8px 24px;">', unsafe_allow_html=True)
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
        st.markdown('</div>', unsafe_allow_html=True)

    with col_right:
        st.markdown('<div class="section-label">Documents Needed</div>', unsafe_allow_html=True)
        st.markdown('<div class="card" style="padding:16px 24px;">', unsafe_allow_html=True)
        for i, d in enumerate(plan.document_checklist):
            st.checkbox(d, key=f"doc_{i}")
        st.markdown('</div>', unsafe_allow_html=True)

        st.markdown('<div class="section-label" style="margin-top:20px;">Next Steps</div>', unsafe_allow_html=True)
        st.markdown('<div class="card" style="padding:16px 24px;">', unsafe_allow_html=True)
        for step in plan.next_steps:
            st.markdown(f"<div style='margin-bottom:12px; font-size:14px; line-height:1.4;'>→ {step}</div>", unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

        # Download
        st.markdown("<div style='height: 16px'></div>", unsafe_allow_html=True)
        html = generate_html_report(profile, plan)
        st.download_button("Download Full Report", data=html, file_name=f"sahayak_{profile.mode}.html", mime="text/html", use_container_width=True)


# ─── Query Runner ──────────────────────────────────────────
def run_query(query: str):
    if not query.strip():
        st.warning("Please describe your situation.")
        return
    
    st.markdown("<div style='height: 10px;'></div>", unsafe_allow_html=True)
    p = st.progress(0)
    s = st.empty()
    
    try:
        s.info("Understanding your request...")
        p.progress(20)
        
        s.info("Researching documents (10–30s)...")
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
    render_top_nav()
    render_hero()

    if st.session_state.page == "scheme":
        query = st.text_area("Describe your situation", height=120, placeholder="Example: എന്റെ അമ്മൂമ്മ 68 വയസ്സ്, വിധവ, കേരളത്തിൽ", label_visibility="collapsed", key="scheme_q")
        if st.button("Get Plan", key="scheme_btn"):
            st.session_state.results = None
            run_query(query)

    elif st.session_state.page == "mentor":
        query = st.text_area("What guidance do you need?", height=120, placeholder="Example: I'm 17, finished 12th, want to work in Saudi Arabia", label_visibility="collapsed", key="mentor_q")
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