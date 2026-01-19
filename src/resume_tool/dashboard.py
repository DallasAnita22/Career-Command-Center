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
        
        /* GUIDE STYLES */
        .guide-header { color: #4CAF50; font-size: 1.5rem; font-weight: bold; margin-top: 20px; }
        .score-red { color: #FF5252; font-weight: bold; }
        .score-yellow { color: #FFC107; font-weight: bold; }
        .score-green { color: #4CAF50; font-weight: bold; }
        
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
        
        # LINK TO BUG FORM
        st.link_button("🐛 Report a Bug", "https://forms.google.com/your-form-link-here", use_container_width=True)

        if st.button("Logout"): st.session_state['logged_in'] = False; st.rerun()

    # --- MAIN CONTENT ---
    st.markdown("<div class='main-header'>🚀 Career Command Center</div>", unsafe_allow_html=True)
    
    tab_work, tab_guide = st.tabs(["🛠️ Workspace", "📚 detailed User Guide"])
    
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
                
                if save: st.success("Draft Saved!")

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
                            
                            Format: Use Markdown. Be encouraging but critical.
                            """
                            
                            if ai.client:
                                response = ai.client.models.generate_content(
                                    model='gemini-2.0-flash', 
                                    contents=prompt
                                )
                                st.session_state['coach_feedback'] = response.text
                                st.rerun()
                            else:
                                st.error("❌ Client failed. Check Key.")
                    except Exception as e:
                        st.error(f"AI Error: {str(e)}")

    # === TAB 2: DETAILED USER GUIDE ===
    with tab_guide:
        st.markdown("# 🎓 How to Read Your Results")
        st.markdown("Understanding the Coach's feedback is the key to getting hired. Here is how to interpret the data.")
        
        

        with st.expander("📊 1. Understanding the Match Score", expanded=True):
            st.markdown("""
            The AI mimics an **ATS (Applicant Tracking System)**. It compares your resume text against the Job Description text.
            
            * <span class="score-red">0% - 40% (Critical Mismatch):</span>
                * **What it means:** The robot thinks you are applying for the wrong job.
                * **The Fix:** You are likely missing the "Hard Skills" (e.g., Python, Forklift, CPR). Look at the specific tools mentioned in the job post and add them to your **Skills** section.
            
            * <span class="score-yellow">41% - 75% (Good Context, Wrong Words):</span>
                * **What it means:** You have the experience, but you are using different language than the company.
                * **The Fix:** Synonym Swap. If they say "Client Success" and you say "Customer Service," **change your words to match theirs.**
            
            * <span class="score-green">76% - 100% (Interview Ready):</span>
                * **What it means:** You are a perfect paper match. Apply immediately.
            """, unsafe_allow_html=True)
            
        with st.expander("🔑 2. How to Handle 'Missing Keywords'"):
            st.markdown("""
            The Coach will list 3-5 words that are in the Job Description but NOT in your resume.
            
            **Where do I put them?**
            1.  **If it's a Hard Skill (e.g., 'React', 'Excel'):** Add it to your **Skills Section** at the bottom.
            2.  **If it's a Soft Skill (e.g., 'Leadership', 'Collaboration'):** Do NOT just list it. Weave it into a bullet point.
                * *Bad:* "Skills: Leadership."
                * *Good:* "Demonstrated **leadership** by guiding a team of 5..."
            """)
            
        with st.expander("🛠️ 3. Workflow Strategy"):
            st.markdown("""
            **The 'Ping-Pong' Method:**
            1.  Paste the **Job Description** on the Right.
            2.  Click **Analyze**.
            3.  Read the **Missing Keywords**.
            4.  Go to the **Left Editor** and add those specific keywords.
            5.  Click **Analyze** again.
            6.  Repeat until your score turns **Green**.
            """)
            
        with st.expander("🚀 4. Using Career Paths (Sidebar)"):
            st.markdown("""
            Changing the **"Industry / Path"** dropdown in the sidebar changes the AI's personality.
            
            * **General:** Good for office jobs. Focuses on clarity.
            * **Tech:** Focuses on languages (Java, Python) and projects.
            * **Trades:** Focuses on safety, certifications, and reliability.
            * **First-Time:** Focuses on potential, attitude, and transferable habits (punctuality, learning).
            
            *Tip: If you are pivoting careers, select the career you WANT, not the one you HAVE.*
            """)

if st.session_state['logged_in']: main_app()
else: login_page()