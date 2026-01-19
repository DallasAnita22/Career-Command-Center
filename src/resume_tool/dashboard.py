import streamlit as st
import sys
import os
from services.ai_service import AIService
from services.file_handlers import generate_pdf, generate_docx, parse_resume_to_dict, extract_text_from_file
from services.expert_knowledge import get_career_paths, get_coach_advice
from services.auth import login_user, create_user, save_user_draft
from database import SessionLocal, engine
from models import Base, PortfolioProject
# Restore the Math-based Auditor functions
from ats_auditor import get_analysis_data, perform_general_audit 

# --- CONFIG ---
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
Base.metadata.create_all(bind=engine)
st.set_page_config(page_title="Career Command Center", page_icon="🚀", layout="wide", initial_sidebar_state="expanded")

# --- CSS STYLING ---
def local_css():
    st.markdown("""
    <style>
        .main-header { font-size: 2.2rem; color: #4CAF50; text-align: center; font-weight: 700; margin-bottom: 10px; }
        .sub-header { font-size: 1.2rem; color: #aaa; text-align: center; margin-bottom: 20px; }
        
        /* COACH BOX (Live Feedback) */
        .coach-box { 
            background-color: #262730; padding: 20px; border-radius: 10px; 
            border-left: 5px solid #FFC107; margin-bottom: 20px;
        }
        .coach-title { color: #FFC107; font-weight: bold; font-size: 1.2rem; margin-bottom: 10px; }
        
        /* AUDIT BOX (Deep Analysis) */
        .audit-box {
            background-color: #1E1E1E; padding: 20px; border-radius: 10px;
            border-left: 5px solid #2196F3; margin-bottom: 10px;
        }

        /* SCORES */
        .score-red { color: #FF5252; font-weight: bold; font-size: 1.5rem; }
        .score-yellow { color: #FFC107; font-weight: bold; font-size: 1.5rem; }
        .score-green { color: #4CAF50; font-weight: bold; font-size: 1.5rem; }

        /* TABS */
        .stTabs [data-baseweb="tab-list"] { gap: 8px; }
        .stTabs [data-baseweb="tab"] { background-color: #2b2b2b; border-radius: 8px 8px 0 0; color: white; padding: 10px 15px; }
        .stTabs [aria-selected="true"] { background-color: #4CAF50; color: white; }
    </style>
    """, unsafe_allow_html=True)

# --- SESSION STATE SETUP ---
if 'logged_in' not in st.session_state: st.session_state['logged_in'] = False
if 'gemini_key' not in st.session_state: 
    try:
        st.session_state['gemini_key'] = st.secrets["GEMINI_API_KEY"]
    except:
        st.session_state['gemini_key'] = ""
if 'coach_feedback' not in st.session_state: st.session_state['coach_feedback'] = "👋 I'm ready! Paste your Job Description above and click 'Analyze' for instant feedback."
if 'audit_results' not in st.session_state: st.session_state['audit_results'] = None

# Helper to merge builder fields into one text block for the Auditor
def compile_resume_text():
    return f"""
    {st.session_state.get('form_name', '')}
    {st.session_state.get('form_email', '')} | {st.session_state.get('form_phone', '')}
    {st.session_state.get('form_summary', '')}
    EXPERIENCE
    {st.session_state.get('form_exp', '')}
    SKILLS
    {st.session_state.get('form_skills', '')}
    """

def get_db(): return SessionLocal()

# --- LOGIN PAGE ---
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
                        # Load saved data into session
                        st.session_state.update({
                            'form_name': user.saved_name, 'form_email': user.saved_email,
                            'form_phone': user.saved_phone, 'form_summary': user.saved_summary,
                            'form_exp': user.saved_experience, 'form_skills': user.saved_skills
                        })
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
        st.markdown("### 🎯 Career Target")
        role = st.selectbox("Industry / Path", get_career_paths(), index=0)
        advice = get_coach_advice(role)
        st.info(f"**Coach's Tip:**\n\n{advice['tip']}\n\n_{advice['book_ref']}_")
        
        st.link_button("🐛 Report a Bug", "https://forms.google.com/your-form-link-here", use_container_width=True)
        if st.button("Logout"): st.session_state['logged_in'] = False; st.rerun()

    # --- HEADER ---
    st.markdown("<div class='main-header'>🚀 Career Command Center</div>", unsafe_allow_html=True)
    st.markdown("<div class='sub-header'>Build. Audit. Optimize. Succeed.</div>", unsafe_allow_html=True)
    
    # --- TABS ---
    tab_build, tab_audit, tab_cover, tab_interview, tab_portfolio, tab_guide = st.tabs([
        "🛠️ The Workshop (Build)", 
        "🔬 The Lab (Deep Audit)", 
        "📝 Cover Letter", 
        "🎤 Interview Prep",
        "💼 Portfolio Locker",
        "📚 User Manual"
    ])
    
    # === TAB 1: THE WORKSHOP (Split Screen) ===
    with tab_build:
        col_edit, col_coach = st.columns([1.3, 1])
        
        # LEFT: EDITOR
        with col_edit:
            st.subheader("📝 Resume Editor")
            
            # Auto-Fill
            with st.popover("📂 Import from File"):
                up = st.file_uploader("Upload old Resume", type=["pdf","docx"])
                if up and st.button("⚡ Auto-Fill Data"):
                    d = parse_resume_to_dict(extract_text_from_file(up))
                    st.session_state.update({'form_name':d['name'], 'form_email':d['email'], 'form_phone':d['phone'], 'form_link':d['linkedin'], 'form_summary':d['summary'], 'form_exp':d['experience'], 'form_skills':d['skills']})
                    st.rerun()

            with st.form("resume_form"):
                c1, c2 = st.columns(2)
                st.session_state['form_name'] = c1.text_input("Name", value=st.session_state.get('form_name',''))
                st.session_state['form_phone'] = c2.text_input("Phone", value=st.session_state.get('form_phone',''))
                st.session_state['form_email'] = c1.text_input("Email", value=st.session_state.get('form_email',''))
                st.session_state['form_link'] = c2.text_input("LinkedIn", value=st.session_state.get('form_link',''))
                
                st.session_state['form_summary'] = st.text_area("Summary (The Hook)", height=100, value=st.session_state.get('form_summary',''))
                
                st.markdown("### Experience")
                st.session_state['form_exp'] = st.text_area("Work History (Paste bullets)", height=300, value=st.session_state.get('form_exp',''))
                
                st.markdown("### Skills")
                st.session_state['form_skills'] = st.text_area("Skills & Certifications", height=100, value=st.session_state.get('form_skills',''))
                
                # SAVE & SYNC
                if st.form_submit_button("💾 Save & Sync to Auditor", use_container_width=True):
                    # Save to DB
                    data = {"name": st.session_state['form_name'], "email": st.session_state['form_email'], 
                            "phone": st.session_state['form_phone'], "summary": st.session_state['form_summary'],
                            "experience": st.session_state['form_exp'], "skills": st.session_state['form_skills'], "role": role}
                    db = get_db()
                    save_user_draft(db, st.session_state['user_id'], data)
                    db.close()
                    # Generate Files
                    st.session_state['pdf_bytes'] = generate_pdf(data)
                    st.session_state['docx_bytes'] = generate_docx(data)
                    st.success("Saved! Your data is now ready in 'The Lab' tab.")

            if st.session_state.get('pdf_bytes'):
                st.download_button("📄 Download PDF", st.session_state['pdf_bytes'], "resume.pdf", "application/pdf")

        # RIGHT: LIVE COACH
        with col_coach:
            st.subheader("🤖 Live Coach")
            st.caption("Paste a Job Description here to get real-time advice while you type.")
            jd_live = st.text_area("Target Job Description", height=150, key="jd_live_input")
            
            st.markdown(f"""<div class="coach-box"><div class="coach-title">💬 Instant Feedback</div>{st.session_state['coach_feedback']}</div>""", unsafe_allow_html=True)
            
            if st.button("🔍 Analyze Current Draft", use_container_width=True):
                if not st.session_state['gemini_key']: st.error("Please enter API Key in Sidebar")
                elif not jd_live: st.warning("Paste a Job Description first!")
                else:
                    ai = AIService(st.session_state['gemini_key'])
                    current_text = compile_resume_text()
                    try:
                        with st.spinner("Coach is reading..."):
                            prompt = f"Act as a Coach for {role}. Resume: {current_text}. Job: {jd_live}. Give 1 Match Score, 3 Missing Keywords, 1 Rewrite suggestion. Be concise."
                            if ai.client:
                                response = ai.client.models.generate_content(model='gemini-2.0-flash', contents=prompt)
                                st.session_state['coach_feedback'] = response.text
                                st.rerun()
                    except Exception as e: st.error(f"Error: {e}")

    # === TAB 2: THE LAB (Deep Auditor) ===
    with tab_audit:
        st.subheader("🔬 Deep Scan Auditor")
        st.markdown("This tool uses **Mathematics** (Cosine Similarity) to verify if you pass the robot (ATS) filter.")
        
        col_a1, col_a2 = st.columns(2)
        
        with col_a1:
            st.info("ℹ️ **Source:** analyzing the resume you built in 'The Workshop'.")
            jd_audit = st.text_area("Paste Job Description for Deep Audit", height=300, key="jd_audit_input")
            
            if st.button("🚀 Run Deep Scan", use_container_width=True):
                resume_text = compile_resume_text()
                if not resume_text.strip():
                    st.error("Your resume is empty! Go to 'The Workshop' tab to build it.")
                elif not jd_audit:
                    st.error("Paste a Job Description.")
                else:
                    # Run the Math Audit from ats_auditor.py
                    results = get_analysis_data(resume_text, jd_audit)
                    st.session_state['audit_results'] = results
        
        with col_a2:
            if st.session_state['audit_results']:
                res = st.session_state['audit_results']
                score = res['match_score']
                
                # Visual Score
                color_class = "score-green" if score > 75 else "score-yellow" if score > 40 else "score-red"
                st.markdown(f"### Match Score: <span class='{color_class}'>{score}%</span>", unsafe_allow_html=True)
                st.progress(score / 100)
                
                st.divider()
                
                # Missing Keywords
                st.markdown("### ⚠️ Missing Keywords")
                if res['missing_keywords']:
                    st.write("The ATS is looking for these exact words. Add them to your **Skills** or **Summary**.")
                    st.error(", ".join(res['missing_keywords'][:10]))
                else:
                    st.success("No major keywords missing! Great job.")
                
                # AI Verdict (Extra Layer)
                with st.expander("🤖 View AI Verdict (Gemini)", expanded=False):
                    if st.button("Ask AI for 'The Fix'"):
                        ai = AIService(st.session_state['gemini_key'])
                        if ai.client:
                            prompt = f"The user has a match score of {score}%. Missing keywords: {res['missing_keywords']}. Give 3 specific sentences they can add to their resume to fix this."
                            resp = ai.client.models.generate_content(model='gemini-2.0-flash', contents=prompt)
                            st.write(resp.text)

    # === TAB 3: COVER LETTER ===
    with tab_cover:
        st.subheader("📝 Cover Letter Generator")
        jd_cover = st.text_area("Paste Job Description", height=200, key="cv_jd")
        if st.button("Draft Letter"):
            ai = AIService(st.session_state['gemini_key'])
            if ai.client:
                with st.spinner("Writing..."):
                    letter = ai.generate_cover_letter(st.session_state['form_summary'], jd_cover)
                    st.text_area("Result", value=letter, height=400)

    # === TAB 4: INTERVIEW ===
    with tab_interview:
        st.subheader("🎤 Interview Prep")
        jd_int = st.text_area("Paste Job Description", height=100, key="int_jd")
        if st.button("Start Mock Interview"):
            ai = AIService(st.session_state['gemini_key'])
            if ai.client:
                qs = ai.simulate_interview(jd_int)
                for q in qs: st.write(f"- {q}")

    # === TAB 5: PORTFOLIO LOCKER ===
    with tab_portfolio:
        st.subheader("💼 Career Locker (STAR Method)")
        st.markdown("Store your biggest wins here so you don't forget them during interviews.")
        
        def save_p(uid, t, s, tk, a, r): 
            db=get_db(); db.add(PortfolioProject(user_id=uid, title=t, industry=role, situation=s, task=tk, action=a, result=r)); db.commit(); db.close()
        def get_p(uid): 
            db=get_db(); p=db.query(PortfolioProject).filter(PortfolioProject.user_id=uid).all(); db.close(); return p
            
        c1, c2 = st.columns([1, 1.5])
        with c1.form("port_form"):
            t=st.text_input("Project Title")
            s=st.text_area("Situation (The Problem)")
            tk=st.text_area("Task (Your Role)")
            a=st.text_area("Action (What you did)")
            r=st.text_area("Result (The Outcome/$$$)")
            if st.form_submit_button("Save STAR Story"):
                save_p(st.session_state['user_id'], t, s, tk, a, r)
                st.success("Saved!")
                st.rerun()
        
        with c2:
            st.markdown("### 🗄️ Saved Stories")
            projects = get_p(st.session_state['user_id'])
            if projects:
                for p in projects:
                    with st.expander(f"📌 {p.title} ({p.industry})"):
                        st.markdown(f"**S:** {p.situation}\n\n**T:** {p.task}\n\n**A:** {p.action}\n\n**R:** {p.result}")
            else:
                st.info("No stories saved yet.")

    # === TAB 6: USER MANUAL ===
    with tab_guide:
        st.markdown("# 🎓 Master Manual")
        
        st.info("*(Software Architecture: Python (Streamlit) + SQLite + Gemini AI + Cosine Similarity)*")

        st.markdown("### 🚀 How to Command Your Career")
        st.markdown("We designed this app to work in a loop: **Write -> Check -> Audit -> Finalize**.")
        
        c1, c2 = st.columns(2)
        with c1:
            st.markdown("""
            **Step 1: The Workshop (Tab 1)**
            * This is your creative space. 
            * Use the **Live Coach** on the right for quick checks.
            * *Tip:* Click "Save & Sync" frequently. This sends your text to the Auditor.
            
            **Step 2: The Lab (Tab 2)**
            * **Deep Audit:** This uses Mathematics (Cosine Similarity), not just AI.
            * If the Coach says you are good, but the Lab gives you a **40%**, trust the Lab. It is stricter, like a real ATS.
            * Take "Missing Keywords" and add them to your resume in Tab 1.
            """)
        with c2:
            st.markdown("""
            **Step 3: Portfolio Locker (Tab 5)**
            * **The STAR Method:** Use this to prepare for interviews.
            * Situation, Task, Action, Result.
            * Save your best stories here so you can reference them during phone screens.
            
            **Step 4: Interview & Cover Letters**
            * Once your resume is scored > 75%, proceed to generate a Cover Letter (Tab 3).
            * Run a Mock Interview (Tab 4) with the specific Job Description.
            """)
            
        st.divider()
        st.caption("Career Command Center v2.0 | Built with 💡 by Gemini")

if st.session_state['logged_in']: main_app()
else: login_page()