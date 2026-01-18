import streamlit as st
import sys
import os
import time
import json
from datetime import datetime

# --- PATH SETUP ---
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# --- IMPORTS ---
try:
    from services.portfolio_coach import PortfolioCoach
    from services.file_handlers import extract_text_from_file, generate_pdf, generate_docx, parse_resume_to_dict
    from services.expert_knowledge import classify_keyword, get_usage_tip
    from services.auth import login_user, create_user, save_user_draft
    from services.ai_service import AIService
    from database import SessionLocal, engine
    from models import Base, PortfolioProject, User, SavedResume
    from ats_auditor import get_analysis_data, perform_general_audit
except ImportError as e:
    st.error(f"⚠️ SYSTEM ERROR: Missing Module. {e}")
    st.stop()

# --- INITIALIZATION ---
Base.metadata.create_all(bind=engine)
coach = PortfolioCoach()

st.set_page_config(page_title="Career Command Center", page_icon="🚀", layout="wide", initial_sidebar_state="expanded")

# --- MODERN UI CSS ---
def local_css():
    st.markdown("""
    <style>
        /* GLOBAL FONTS & COLORS */
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600&display=swap');
        
        html, body, [class*="css"]  {
            font-family: 'Inter', sans-serif;
        }
        
        /* CARD STYLE FOR FORMS */
        .stForm {
            background-color: #1E1E1E;
            padding: 2rem;
            border-radius: 15px;
            box-shadow: 0 4px 15px rgba(0,0,0,0.3);
            border: 1px solid #333;
        }
        
        /* TABS MODERNIZATION */
        .stTabs [data-baseweb="tab-list"] {
            gap: 10px;
        }
        .stTabs [data-baseweb="tab"] {
            background-color: #2b2b2b;
            border-radius: 10px 10px 0 0;
            padding: 10px 20px;
            color: white;
        }
        .stTabs [aria-selected="true"] {
            background-color: #4CAF50 !important; /* Green Accent */
            color: white !important;
        }

        /* BUTTONS */
        .stButton > button {
            background: linear-gradient(90deg, #4CAF50 0%, #2E7D32 100%);
            color: white;
            border: none;
            border-radius: 8px;
            padding: 0.5rem 1rem;
            font-weight: 600;
            transition: all 0.3s ease;
        }
        .stButton > button:hover {
            transform: scale(1.02);
            box-shadow: 0 4px 12px rgba(76, 175, 80, 0.4);
        }

        /* METRIC CARDS */
        div[data-testid="metric-container"] {
            background-color: #262626;
            padding: 15px;
            border-radius: 10px;
            border-left: 5px solid #4CAF50;
        }
        
        /* SIDEBAR POLISH */
        section[data-testid="stSidebar"] {
            background-color: #121212;
        }
    </style>
    """, unsafe_allow_html=True)

# --- SESSION STATE ---
if 'logged_in' not in st.session_state: st.session_state['logged_in'] = False
if 'user_id' not in st.session_state: st.session_state['user_id'] = None
if 'username' not in st.session_state: st.session_state['username'] = None
if 'gemini_key' not in st.session_state: st.session_state['gemini_key'] = ""
if 'pdf_bytes' not in st.session_state: st.session_state['pdf_bytes'] = None
if 'docx_bytes' not in st.session_state: st.session_state['docx_bytes'] = None
if 'resume_name' not in st.session_state: st.session_state['resume_name'] = "My_Resume"

def get_db(): return SessionLocal()

# --- LOGIN PAGE ---
def login_page():
    local_css() # Apply Styles
    st.markdown("<h1 style='text-align: center; color: #4CAF50;'>🔐 Career Command Center</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center;'>Your AI-Powered Career Headquarters</p>", unsafe_allow_html=True)
    
    c1, c2, c3 = st.columns([1,2,1])
    with c2:
        t1, t2 = st.tabs(["Login", "Create Account"])
        with t1:
            with st.form("login"):
                u = st.text_input("Username")
                p = st.text_input("Password", type="password")
                if st.form_submit_button("Login", use_container_width=True):
                    db = get_db()
                    user = login_user(db, u, p)
                    db.close()
                    if user:
                        st.session_state['logged_in'] = True
                        st.session_state['user_id'] = user.id
                        st.session_state['username'] = user.username
                        st.session_state['form_name'] = user.saved_name or ""
                        st.session_state['form_email'] = user.saved_email or ""
                        st.session_state['form_phone'] = user.saved_phone or ""
                        st.session_state['form_link'] = user.saved_linkedin or ""
                        st.session_state['form_summary'] = user.saved_summary or ""
                        st.session_state['form_exp'] = user.saved_experience or ""
                        st.session_state['form_skills'] = user.saved_skills or ""
                        st.session_state['form_references'] = user.saved_references or ""
                        st.session_state['saved_role'] = user.saved_role or "General"
                        st.rerun()
                    else: st.error("Invalid credentials")
        with t2:
            with st.form("register"):
                nu = st.text_input("New Username")
                np = st.text_input("New Password", type="password")
                if st.form_submit_button("Create Account", use_container_width=True):
                    db = get_db()
                    if create_user(db, nu, np): st.success("Created! Go to Login."); 
                    else: st.error("Username taken.")
                    db.close()

# --- MAIN APP ---
def main_app():
    local_css() # Apply Styles
    
    # --- SIDEBAR ---
    with st.sidebar:
        st.title(f"👤 {st.session_state['username']}")
        
        # AI SETTINGS
        with st.expander("🔑 AI Settings", expanded=True):
            api_input = st.text_input("Google Gemini API Key", type="password", value=st.session_state['gemini_key'])
            if api_input:
                st.session_state['gemini_key'] = api_input
                st.success("AI Active!")
            else:
                st.warning("AI features disabled.")
        
        ai = AIService(st.session_state['gemini_key'])

        st.divider()

        # FEEDBACK BUTTON (NEW!)
        st.markdown("### 📢 Beta Feedback")
        st.caption("Found a bug? Have an idea?")
        # REPLACE THIS URL WITH YOUR ACTUAL GOOGLE FORM LINK
        st.link_button("🐛 Report a Bug", "https://docs.google.com/forms/d/e/1FAIpQLScKoStyO1aLznpUiIAWepq2nEBY3rE1V2rSZ_3P_ZKb-dzLDA/viewform?usp=publish-editor", use_container_width=True)

        st.divider()
        
        roles = ["Retail & Customer Service", "Admin & HR", "Tech", "General"]
        saved = st.session_state.get('saved_role', 'General')
        idx = roles.index(saved) if saved in roles else 3
        role = st.selectbox("Target Role", roles, index=idx)

        if st.button("Logout"): st.session_state['logged_in'] = False; st.rerun()

    st.markdown("## 🚀 Career Command Center")
    
    # --- TABS ---
    tab_guide, tab_build, tab_audit, tab_cover, tab_interview = st.tabs([
        "📚 User Guide", "🏗️ Builder", "📊 Auditor", "📝 Cover Letter", "🎤 Interview"
    ])
    
    # --- TAB 1: MASTER GUIDE (DETAILED) ---
    with tab_guide:
        st.markdown("# 🎓 Platform User Manual")
        st.markdown("Use this guide to master every tool in your command center.")
        
        with st.expander("🏗️ Tab 1: Resume Builder (How to Use)", expanded=True):
            st.markdown("""
            **Purpose:** Create a perfectly formatted, ATS-friendly resume.
            
            **Step-by-Step:**
            1.  **Auto-Fill (Optional):** If you have an old resume, upload it in the 'Auto-Fill' box. The system will read it and fill the fields for you.
            2.  **Contact Info:** Ensure your email and phone are correct. These go at the top of the PDF.
            3.  **Experience:**
                * *Magic Rewrite:* Type a basic sentence like "I sold shoes." Click the **'✨ Magic Rewrite'** button. The AI will convert it to "Achieved 120% of sales targets by delivering exceptional service..."
                * *Copy & Paste:* Copy the AI's suggestion and paste it into your final text box.
            4.  **Save & Generate:** Click this button to save your work to the database and create your download files.
            5.  **Download:** Use the buttons at the bottom to get a PDF (for applying) or DOCX (for editing).
            """)

        with st.expander("📊 Tab 2: ATS Auditor (How to Use)"):
            st.markdown("""
            **Purpose:** Check if your resume will pass the automated robots (ATS) used by companies.
            
            **Mode A: Job Match (Best for applying)**
            1.  Select **'🎯 Job Match'**.
            2.  Paste the **Job Description (JD)** from the listing (LinkedIn/Indeed).
            3.  Upload your Resume.
            4.  **Read the Score:**
                * 🔴 **0-40%:** Critical Fail. You are missing key hard skills. Add them immediately.
                * 🟡 **41-79%:** Good. You have the skills but maybe used different words.
                * 🟢 **80%+:** Excellent match. Apply now.
            
            **Mode B: Health Check (Best for general review)**
            1.  Select **'🏥 Health Check'**.
            2.  Upload your resume.
            3.  The system checks for formatting errors, weak words (e.g., "Responsible for"), and missing contact info.
            """)

        with st.expander("📝 Tab 3: Cover Letter Generator"):
            st.markdown("""
            **Purpose:** Write a tailored cover letter in seconds.
            
            **How to use:**
            1.  **Prerequisite:** You MUST have filled out the **Summary** section in the Resume Builder tab first.
            2.  Paste the **Job Description** into the box.
            3.  Click **Generate**.
            4.  The AI analyzes your summary against the JD and writes a letter connecting your specific skills to their needs.
            """)

        with st.expander("🎤 Tab 4: Interview Simulator"):
            st.markdown("""
            **Purpose:** Practice for the actual interview.
            
            **How to use:**
            1.  Paste the **Job Description**.
            2.  Click **Start Interview**.
            3.  The AI will generate 3 hard questions based on that specific job.
            4.  Type your answer in the box.
            5.  Click **Grade Answer**. The AI will act as a hiring manager and tell you if your answer was strong enough.
            """)

    # --- TAB 2: BUILDER ---
    with tab_build:
        c1, c2 = st.columns([2, 1])
        with c1:
            st.subheader("Smart Resume Editor")
        with c2:
             with st.popover("📂 Import Data"):
                up = st.file_uploader("Upload old Resume", type=["pdf","docx"])
                if up and st.button("⚡ Auto-Fill Data"):
                    d = parse_resume_to_dict(extract_text_from_file(up))
                    st.session_state.update({'form_name':d['name'], 'form_email':d['email'], 'form_phone':d['phone'], 'form_link':d['linkedin'], 'form_summary':d['summary'], 'form_exp':d['experience'], 'form_skills':d['skills'], 'form_references':d['references']})
                    st.rerun()

        with st.expander("✨ AI Bullet Point Magic Rewrite", expanded=False):
            col_exp, col_ai = st.columns([3, 1])
            exp_input = col_exp.text_area("Draft a Bullet Point (e.g. 'I managed a team')", height=80, key="raw_bullet")
            
            if col_ai.button("✨ Magic Rewrite", help="Use AI to make this professional"):
                if exp_input:
                    with st.spinner("Optimizing..."):
                        improved = ai.magic_rewrite(exp_input, role)
                        st.info(f"**Suggestion:**\n{improved}")
                else:
                    st.error("Type something first!")

        with st.form("resume"):
            c1, c2 = st.columns(2)
            name = c1.text_input("Name", value=st.session_state.get('form_name',''))
            email = c1.text_input("Email", value=st.session_state.get('form_email',''))
            phone = c2.text_input("Phone", value=st.session_state.get('form_phone',''))
            link = c2.text_input("Link", value=st.session_state.get('form_link',''))
            summ = st.text_area("Professional Summary", value=st.session_state.get('form_summary',''))
            
            st.markdown("---")
            st.markdown("### 💼 Experience")
            # Removed nested button section from here

            exp = st.text_area("Final Experience Section (Paste optimized bullets here)", height=250, value=st.session_state.get('form_exp',''))
            
            st.markdown("---")
            c3, c4 = st.columns(2)
            skill = c3.text_area("Skills & Certifications", height=150, value=st.session_state.get('form_skills',''))
            refs = c4.text_area("References", height=150, value=st.session_state.get('form_references',''))
            
            if st.form_submit_button("💾 Save & Generate Resume", use_container_width=True):
                st.session_state.update({'form_name':name, 'form_email':email, 'form_phone':phone, 'form_link':link, 'form_summary':summ, 'form_exp':exp, 'form_skills':skill, 'form_references':refs})
                data = {"name":name, "email":email, "phone":phone, "linkedin":link, "summary":summ, "experience":exp, "skills":skill, "references":refs, "role":role}
                db = get_db()
                save_user_draft(db, st.session_state['user_id'], data)
                db.close()
                st.session_state['pdf_bytes'] = generate_pdf(data)
                st.session_state['docx_bytes'] = generate_docx(data)
                st.session_state['resume_name'] = name.replace(" ", "_")
                st.success("Saved successfully!")
        
        if st.session_state['pdf_bytes']:
            st.divider()
            col_d1, col_d2 = st.columns(2)
            col_d1.download_button("📄 Download PDF", st.session_state['pdf_bytes'], f"{st.session_state['resume_name']}.pdf", "application/pdf", use_container_width=True)
            col_d2.download_button("📝 Download DOCX", st.session_state['docx_bytes'], f"{st.session_state['resume_name']}.docx", "application/vnd.openxmlformats-officedocument.wordprocessingml.document", use_container_width=True)

    # --- TAB 3: AUDITOR ---
    with tab_audit:
        st.subheader("ATS Resume Auditor")
        
        mode = st.radio("Select Audit Type", ["🎯 Job Match (Requires JD)", "🏥 General Health Check (No JD)"], horizontal=True)
        
        c1, c2 = st.columns(2)
        with c1: 
            up = st.file_uploader("Upload Resume for Scan", type=["pdf","docx"], key="audit_up")
        
        if "Job Match" in mode:
            with c1:
                jd = st.text_area("Paste Job Description", height=200)
                run = st.button("Run Match Analysis", use_container_width=True)
            
            if run and up and jd:
                res = get_analysis_data(extract_text_from_file(up), jd)
                with c2:
                    st.metric("Match Score", f"{res['match_score']}%")
                    st.progress(res['match_score'] / 100)
                    if res['missing_keywords']:
                        st.error("⚠️ Critical Missing Skills:")
                        st.write(", ".join(res['missing_keywords'][:10]))
                    else:
                        st.success("Perfect Match!")
        else:
            with c1:
                run = st.button("Run Health Check", use_container_width=True)
            if run and up:
                res = perform_general_audit(extract_text_from_file(up))
                with c2:
                    st.metric("Health Score", f"{res['score']}/100")
                    st.progress(res['score'] / 100)
                    for issue in res['issues']: st.error(issue)
                    for s in res['strengths']: st.success(s)

    # --- TAB 4: COVER LETTER ---
    with tab_cover:
        st.subheader("📝 AI Cover Letter Writer")
        c1, c2 = st.columns([1, 1])
        with c1:
            jd_cover = st.text_area("Paste Job Description", height=300)
            gen_btn = st.button("Generate Letter", use_container_width=True)
        with c2:
            if gen_btn:
                if not st.session_state.get('form_summary'):
                    st.error("⚠️ Please fill out your Resume Summary in the Builder tab first.")
                elif jd_cover:
                    with st.spinner("Drafting your letter..."):
                        letter = ai.generate_cover_letter(st.session_state['form_summary'], jd_cover)
                        st.text_area("Final Draft", value=letter, height=400)

    # --- TAB 5: INTERVIEW ---
    with tab_interview:
        st.subheader("🎤 Mock Interview Simulator")
        
        if 'interview_qs' not in st.session_state: st.session_state['interview_qs'] = []
        
        jd_interview = st.text_area("Paste Job Description to Generate Questions", height=100, key="jd_int")
        if st.button("Start Interview Session"):
            if jd_interview:
                with st.spinner("AI is analyzing the role..."):
                    st.session_state['interview_qs'] = ai.simulate_interview(jd_interview)
        
        if st.session_state['interview_qs']:
            st.divider()
            for i, q in enumerate(st.session_state['interview_qs']):
                with st.container():
                    st.markdown(f"**Question {i+1}: {q}**")
                    ans = st.text_area(f"Your Answer", key=f"ans_{i}", height=100)
                    if st.button(f"Grade Answer {i+1}"):
                        if ans:
                            feedback = ai.critique_answer(q, ans)
                            st.info(f"👨🏫 **Coach's Feedback:** {feedback}")

if st.session_state['logged_in']: main_app()
else: login_page()