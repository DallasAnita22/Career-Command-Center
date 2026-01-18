import spacy
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import re

try:
    nlp = spacy.load("en_core_web_sm")
except OSError:
    import spacy.cli
    spacy.cli.download("en_core_web_sm")
    nlp = spacy.load("en_core_web_sm")

RESUME_NOISE = {"experience", "skills", "education", "summary", "responsible", "duties", "include", "worked", "helped", "team", "role", "company", "work", "job", "candidate", "requirements", "year", "excellent", "strong", "proficient", "various", "ability", "remote", "hybrid"}

def clean_text(text):
    if not text: return ""
    text = re.sub(r'[^a-z0-9\s]', ' ', text.lower())
    return re.sub(r'\s+', ' ', text).strip()

def get_tokens(text):
    doc = nlp(text)
    tokens = []
    for token in doc:
        if token.pos_ not in ["NOUN", "PROPN"]: continue
        if len(token.text) < 3 or token.is_stop or token.text in RESUME_NOISE: continue
        tokens.append(token.text)
    return set(tokens)

# --- EXISTING JD MATCH AUDIT ---
def get_analysis_data(resume_text, jd_text):
    if not resume_text or not jd_text: return {"match_score": 0, "common_keywords": [], "missing_keywords": []}
    
    r_tokens = get_tokens(clean_text(resume_text))
    j_tokens = get_tokens(clean_text(jd_text))
    
    try:
        cv = CountVectorizer()
        matrix = cv.fit_transform([" ".join(r_tokens), " ".join(j_tokens)])
        score = round(cosine_similarity(matrix)[0][1] * 100, 1)
    except: score = 0
    
    return {"match_score": score, "common_keywords": sorted(list(r_tokens & j_tokens)), "missing_keywords": sorted(list(j_tokens - r_tokens))}

# --- NEW: GENERAL HEALTH CHECK (No JD) ---
def perform_general_audit(resume_text):
    """Checks for best practices without a JD."""
    score = 100
    issues = []
    strengths = []
    
    text_lower = resume_text.lower()
    
    # 1. Contact Info Check
    if "@" not in text_lower:
        score -= 20
        issues.append("❌ Missing Email Address")
    else:
        strengths.append("✅ Email Detected")
        
    if not any(char.isdigit() for char in resume_text):
        score -= 20
        issues.append("❌ No Phone Number or Metrics found")
    
    # 2. Weak Word Check
    weak_words = ["responsible for", "duties included", "helped", "worked on", "attempted"]
    found_weak = [w for w in weak_words if w in text_lower]
    if found_weak:
        score -= 15
        issues.append(f"⚠️ Weak words detected: {', '.join(found_weak)}")
    else:
        strengths.append("✅ Strong Action Verbs used")
        
    # 3. Length Check
    word_count = len(resume_text.split())
    if word_count < 200:
        score -= 10
        issues.append("⚠️ Resume is too short (under 200 words)")
    elif word_count > 2000:
        score -= 10
        issues.append("⚠️ Resume is too long (over 2 pages)")
    else:
        strengths.append("✅ Optimal Word Count")
        
    # 4. Section Check
    required_sections = ["experience", "education", "skills"]
    missing_sections = [s for s in required_sections if s not in text_lower]
    if missing_sections:
        score -= 15
        issues.append(f"❌ Missing Sections: {', '.join(missing_sections).title()}")
    
    return {
        "score": max(0, score),
        "issues": issues,
        "strengths": strengths
    }