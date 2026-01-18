HARD_SKILLS = {"python", "java", "sql", "aws", "azure", "docker", "kubernetes", "react", "html", "css", "javascript", "excel", "salesforce", "sap", "linux", "scrum", "agile", "machine learning", "ai", "pandas"}
SOFT_SKILLS = {"communication", "leadership", "collaboration", "problem-solving", "adaptability", "organization", "creativity", "negotiation", "mentoring"}
ACTION_VERBS = {"managed", "led", "developed", "created", "executed", "analyzed", "improved", "generated", "spearheaded"}

def classify_keyword(word):
    word = word.lower()
    if word in HARD_SKILLS: return "HARD_SKILL"
    if word in SOFT_SKILLS: return "SOFT_SKILL"
    if word in ACTION_VERBS: return "ACTION_VERB"
    return "GENERAL"

def get_usage_tip(word, category):
    if category == "HARD_SKILL": return f"👉 Action: Add '{word}' to Skills or: 'Leveraged **{word}** to optimize...'"
    if category == "SOFT_SKILL": return f"👉 Action: Prove it: 'Demonstrated **{word}** by coordinating...'"
    return f"👉 Action: Ensure '{word}' appears in your summary."

EXPERT_INSIGHTS = {
    "General": {"tips": ["⚠️ Avoid 'Responsible for'. Use 'Orchestrated'.", "💡 Google Recruiters like: 'Accomplished [X] as measured by [Y]'."]},
    "Tech": {"keywords": ["software", "developer", "data"], "tips": ["⚠️ GitHub is mandatory. Pin top 3 repos.", "💡 Explain WHY you chose a tool."]},
    "Retail & Customer Service": {"keywords": ["retail", "customer"], "tips": ["⚠️ Highlight conflict resolution.", "💡 Quantify: 'Handled 50+ transactions daily'."]}
}

def get_smart_tip(user_role):
    import random
    cat = "General"
    for k, v in EXPERT_INSIGHTS.items():
        if "keywords" in v and any(kw in user_role.lower() for kw in v["keywords"]):
            cat = k
            break
    return cat, random.choice(EXPERT_INSIGHTS[cat]["tips"])