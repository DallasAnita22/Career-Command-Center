import streamlit as st
import sys
import os
from services.ai_service import AIService
from services.file_handlers import generate_pdf, generate_docx
from services.expert_knowledge import get_career_paths, get_coach_advice
from services.auth import login_user, create_user
from database import SessionLocal, engine
from models import Base

# --- CONFIG ---
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
Base.metadata.create_all(bind=engine)
st.set_page_config(page_title="Career Command Center", page_icon="🚀", layout="wide", initial_sidebar_state="expanded")

# --- CSS ---
def local_css():
    st.markdown("""
    <style>
        .main-header { font-size: 2.5rem; color: #4CAF50; text-align: center; font-weight: 700; margin-bottom: 0px; }
        .coach-box { 
            background-color: #262730; 
            padding: 20px; 
            border-radius: 10px; 
            border-left: 5px solid #FFC107;
            margin-bottom: 20px;
        }
        .coach-title { color: #FFC107; font-weight: bold; font-size: 1.2rem; margin-bottom: 10px; }
        .stTextArea textarea { font-family: 'Courier New', monospace; }
        /* Tab Styling */
        .stTabs [data-baseweb="tab-list"] { gap: 10px; }
        .stTabs [data-baseweb="tab"] { background-color: #2b2b2b; border-radius: 10px 10px 0 0; color: white; }
        .stTabs [aria-selected="true"] { background-color: #4CAF50; color: white; }
    </style>
    """, unsafe_allow_html=True)

if 'logged_in' not in st.session_state: st.session_state['logged_in'] = False
if 'gemini_key' not in st.session_state: st.session_state['gemini_key'] = ""
if 'coach_feedback' not in st.session_state: st.session_state['coach_feedback'] = "👋 I'm ready to review your work! Paste your resume on the left, the job description on the right, and click 'Analyze'."

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
        
        # API KEY INPUT
        with st.expander("🔑 AI Access Key", expanded=True):
            key = st.text_input("Gemini API Key", type="password", value=st.session_state['gemini_key'])
            if key: 
                st.session_state['gemini_key'] = key
                st.caption("✅ Key Saved")
            else:
                st.error("❌ No Key Found")
        
        st.divider()
        st.markdown("### 🎯 Your Target")
        
        # CAREER PATHS
        role = st.selectbox("Industry / Path", get_career_paths(), index=0)
        advice = get_coach_advice(role)
        st.info(f"**Coach's Tip for {role}:**\n\n{advice['tip']}\n\n_{advice['book_ref']}_")

        # LOGOUT
        if st.button("Logout"): st.session_state['logged_in'] = False; st.rerun()

    # --- MAIN CONTENT ---
    st.markdown("<div class='main-header'>🚀 Career Command Center</div>", unsafe_allow_html=True)
    
    # RESTORED TABS: WORKSPACE vs USER GUIDE
    tab_work, tab_guide = st.tabs(["🛠️ Workspace", "📚 User Guide"])
    
    # === TAB 1: THE UNIFIED WORKSPACE ===
    with tab_work:
        col_editor, col_coach = st.columns([1.2, 1])
        
        # LEFT: EDITOR
        with col_editor:
            st.subheader("📝 Resume Editor")
            with st.form("resume_form"):
                name = st.text_input("Full Name")
                contact = st.text_input("Contact Info")
                summary = st.text_area("Professional Summary", height=100)
                st.markdown("### Experience")
                experience = st.text_area("Work History (Paste bullets)", height=300)
                skills = st.text_area("Skills", height=100)
                
                c_btn1, c_btn2 = st.columns(2)
                save = c_btn1.form_submit_button("💾 Save Progress", use_container_width=True)
                analyze = c_btn2.form_submit_button("🔍 Analyze with Coach", use_container_width=True)
                
                if save: st.success("Draft Saved! (Note: Cloud resets daily)")

        # RIGHT: AI COACH
        with col_coach:
            st.subheader("🤖 Live Coach Feedback")
            jd = st.text_area("Paste Job Description (Target)", height=150)
            
            st.markdown(f"""<div class="coach-box"><div class="coach-title">💬 AI Analysis</div>{st.session_state['coach_feedback']}</div>""", unsafe_allow_html=True)
            
            # AI LOGIC
            if analyze:
                if not st.session_state['gemini_key']:
                    st.error("❌ You must enter your API Key in the Sidebar first!")
                elif not jd or not experience:
                    st.warning("⚠️ I need both your Resume and the Job Description to compare.")
                else:
                    try:
                        with st.spinner("Coach is analyzing..."):
                            ai = AIService(st.session_state['gemini_key'])
                            
                            prompt = f"""
                            Act as a Career Coach for a {role}.
                            RESUME: {experience}
                            JOB: {jd}
                            
                            Provide:
                            1. Match Score (0-100%)
                            2. 3 Missing Keywords
                            3. Rewrite ONE bullet point to match the job.
                            """
                            
                            # UPDATED AI CALL FOR 2026 LIBRARY
                            if ai.client:
                                response = ai.client.models.generate_content(
                                    model='gemini-2.0-flash', 
                                    contents=prompt
                                )
                                st.session_state['coach_feedback'] = response.text
                                st.rerun()
                            else:
                                st.error("❌ API Client failed to initialize. Check your Key.")
                    except Exception as e:
                        st.error(f"AI Error: {str(e)}")
                        st.caption("Tip: Did you update requirements.txt to use google-genai?")

    # === TAB 2: USER GUIDE (RESTORED) ===
    with tab_guide:
        st.markdown("""
        # 🎓 User Guide & Troubleshooting
        
        ### 1. 🔑 How to fix "AI Key Not Working"
        * **Get a Key:** Go to [Google AI Studio](https://aistudio.google.com/app/apikey) and create a free key.
        * **Paste it:** Put it in the sidebar box labeled "AI Access Key".
        * **Error "404" or "Model Not Found"?** This means the system is outdated. Make sure you updated `requirements.txt` to include `google-genai`.
        
        ### 2. 🛠️ How to use the Workspace
        * **Left Side (Editor):** This is where you work. Type your resume details here.
        * **Right Side (Coach):** This is your guide.
            1. Paste the **Job Description** you are applying for in the top box.
            2. Click **Analyze**.
            3. The AI will tell you exactly what keywords you are missing.
        
        ### 3. 💾 Saving Data
        * **Important:** If you are using the Beta/Cloud version, your data **will disappear** if you close the tab.
        * **Always** click the "Download PDF" button (coming soon to this tab) before you leave!
        """)

if st.session_state['logged_in']: main_app()
else: login_page()