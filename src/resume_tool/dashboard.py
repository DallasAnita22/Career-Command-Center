import streamlit as st
import sys
import os
import time
from services.ai_service import AIService
from services.file_handlers import generate_pdf, generate_docx
from services.expert_knowledge import get_career_paths, get_coach_advice
from services.auth import login_user, create_user, save_user_draft
from database import SessionLocal, engine
from models import Base

# --- CONFIG ---
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
Base.metadata.create_all(bind=engine)
st.set_page_config(page_title="Career Command Center", page_icon="🚀", layout="wide", initial_sidebar_state="expanded")

# --- CSS FOR SPLIT SCREEN ---
def local_css():
    st.markdown("""
    <style>
        .main-header { font-size: 2.5rem; color: #4CAF50; text-align: center; font-weight: 700; }
        .coach-box { 
            background-color: #262730; 
            padding: 20px; 
            border-radius: 10px; 
            border-left: 5px solid #FFC107;
            margin-bottom: 20px;
        }
        .coach-title { color: #FFC107; font-weight: bold; font-size: 1.2rem; margin-bottom: 10px; }
        .stTextArea textarea { font-family: 'Courier New', monospace; }
        .floating-button { margin-top: 10px; }
    </style>
    """, unsafe_allow_html=True)

if 'logged_in' not in st.session_state: st.session_state['logged_in'] = False
if 'gemini_key' not in st.session_state: st.session_state['gemini_key'] = ""
if 'coach_feedback' not in st.session_state: st.session_state['coach_feedback'] = "👋 I'm ready to review your work! Paste your resume on the left and click 'Analyze'."

def get_db(): return SessionLocal()

# --- LOGIN ---
def login_page():
    local_css()
    st.markdown("<div class='main-header'>🔐 Career Command Center</div>", unsafe_allow_html=True)
    c1, c2, c3 = st.columns([1,2,1])
    with c2:
        tab1, tab2 = st.tabs(["Login", "Sign Up"])
        with tab1:
            with st.form("login"):
                u = st.text_input("Username"); p = st.text_input("Password", type="password")
                if st.form_submit_button("Login", use_container_width=True):
                    db = get_db(); user = login_user(db, u, p); db.close()
                    if user:
                        st.session_state['logged_in'] = True
                        st.session_state['user_id'] = user.id
                        st.session_state['username'] = user.username
                        st.session_state['saved_role'] = user.saved_role
                        st.rerun()
                    else: st.error("Invalid credentials")
        with tab2:
            with st.form("signup"):
                nu = st.text_input("New Username"); np = st.text_input("New Password", type="password")
                if st.form_submit_button("Create Account", use_container_width=True):
                    db = get_db(); create_user(db, nu, np); db.close()
                    st.success("Account created! Please log in.")

# --- MAIN APP ---
def main_app():
    local_css()
    
    # --- SIDEBAR ---
    with st.sidebar:
        st.title(f"👤 {st.session_state['username']}")
        with st.expander("🔑 AI Access Key", expanded=True):
            key = st.text_input("Gemini API Key", type="password", value=st.session_state['gemini_key'])
            if key: st.session_state['gemini_key'] = key
        
        st.divider()
        st.markdown("### 🎯 Your Target")
        
        # NEW TOP 20 CAREER PATHS
        role = st.selectbox("Industry / Path", get_career_paths(), index=0)
        
        # DYNAMIC COACH ADVICE IN SIDEBAR
        advice = get_coach_advice(role)
        st.info(f"**Coach's Tip for {role}:**\n\n{advice['tip']}\n\n_{advice['book_ref']}_")

        if st.button("Logout"): st.session_state['logged_in'] = False; st.rerun()

    # --- TOP NAV ---
    st.markdown("<div class='main-header'>🚀 Career Command Center</div>", unsafe_allow_html=True)
    
    # --- SPLIT SCREEN LAYOUT ---
    col_editor, col_coach = st.columns([1.2, 1])
    
    # === LEFT COLUMN: THE WORKBENCH ===
    with col_editor:
        st.subheader("📝 Resume Editor")
        with st.form("resume_form"):
            name = st.text_input("Full Name")
            contact = st.text_input("Contact Info (Phone | Email | LinkedIn)")
            summary = st.text_area("Professional Summary", height=100, help="The 7-Second Hook")
            
            st.markdown("### Experience")
            experience = st.text_area("Work History (Paste bullets here)", height=300)
            
            skills = st.text_area("Skills & Tech Stack", height=100)
            
            # ACTION BUTTONS
            c_btn1, c_btn2 = st.columns(2)
            save = c_btn1.form_submit_button("💾 Save Progress", use_container_width=True)
            analyze = c_btn2.form_submit_button("🔍 Analyze with Coach", use_container_width=True)
            
            if save:
                st.success("Draft Saved!")
                # (Add save logic here similar to previous version)
    
    # === RIGHT COLUMN: THE AI COACH ===
    with col_coach:
        st.subheader("🤖 Live Coach Feedback")
        
        # 1. JOB DESCRIPTION INPUT
        jd = st.text_area("Paste Job Description Here (for targeting)", height=150, placeholder="Paste the job posting you want to apply for...")
        
        # 2. COACH FEEDBACK BOX
        st.markdown(f"""
        <div class="coach-box">
            <div class="coach-title">💬 AI Analysis</div>
            {st.session_state['coach_feedback']}
        </div>
        """, unsafe_allow_html=True)
        
        # AI LOGIC
        if analyze:
            ai = AIService(st.session_state['gemini_key'])
            if not jd:
                st.warning("⚠️ Paste a Job Description above so I can compare!")
            elif not experience:
                st.warning("⚠️ Your resume is empty.")
            else:
                with st.spinner("Analyzing against 2026 Industry Standards..."):
                    # We ask AI to compare Resume vs JD
                    prompt = f"""
                    Act as a tough Career Coach for a candidate in {role}.
                    
                    RESUME EXPERIENCE:
                    {experience}
                    
                    JOB DESCRIPTION:
                    {jd}
                    
                    TASK:
                    1. Give a Match Score (0-100%).
                    2. List 3 Missing Keywords.
                    3. Rewrite ONE bullet point from the resume to better match the job.
                    
                    Format: Use bolding and emojis. Keep it encouraging but direct.
                    """
                    try:
                        # Call AI (Using the new client if updated, or old one)
                        # Adapting to your current AI Service structure
                        response = ai.client.models.generate_content(model='gemini-2.0-flash', contents=prompt)
                        st.session_state['coach_feedback'] = response.text
                        st.rerun()
                    except Exception as e:
                        st.error(f"AI Error: {e}")

    # --- DOWNLOADS ---
    st.divider()
    d1, d2 = st.columns(2)
    d1.button("📄 Download PDF (Final)", use_container_width=True)
    d2.button("� Download Word Doc (Editable)", use_container_width=True)

if st.session_state['logged_in']: main_app()
else: login_page()