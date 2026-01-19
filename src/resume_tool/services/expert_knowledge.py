# src/resume_tool/services/expert_knowledge.py

def get_career_paths():
    """Returns the Top 20 Career Paths for 2026 + Special Categories."""
    return [
        "General / Undecided",
        "--- ENTRY LEVEL & RETURNING ---",
        "First-Time Workforce (High School/Grad)",
        "Returning to Work (Parent/Caregiver)",
        "Career Pivot / Transition",
        "--- TECHNOLOGY & DATA ---",
        "Software Development & AI",
        "Cybersecurity & IT Support",
        "Data Analytics & Science",
        "--- HEALTHCARE ---",
        "Nursing & Patient Care",
        "Medical Administration & Billing",
        "Home Health & Personal Care",
        "--- TRADES & HANDS-ON ---",
        "Green Tech (Solar/Wind)",
        "Skilled Trades (Electrician/HVAC)",
        "Logistics & Supply Chain",
        "--- BUSINESS & SERVICE ---",
        "Digital Marketing & E-Commerce",
        "Project Management",
        "Customer Success & Sales",
        "Human Resources & Recruiting",
        "Finance & Accounting"
    ]

def get_coach_advice(role):
    """
    Returns coaching tips based on principles from 'The 2-Hour Job Search' 
    and 'The 7 Second CV'.
    """
    advice = {
        "First-Time Workforce (High School/Grad)": {
            "focus": "Transferable Skills",
            "tip": "Since you lack history, focus on **Attributes**. Use examples from sports, volunteering, or school projects. Prove you are reliable and eager to learn.",
            "book_ref": "💡 *Strategy:* Focus on 'Micro-Internships' and project work."
        },
        "Returning to Work (Parent/Caregiver)": {
            "focus": "Gap Management",
            "tip": "Don't hide the gap. Use a 'Functional Resume' style. Highlight the organizing, budgeting, and scheduling skills you used during your time away.",
            "book_ref": "💡 *The 2-Hour Job Search:* Networking is 3x more effective for you than applying online."
        },
        "Software Development & AI": {
            "focus": "Portfolio & GitHub",
            "tip": "List your 'Tech Stack' (Python, SQL, React) at the very top. Recruiters scan for these keywords first.",
            "book_ref": "💡 *The 7 Second CV:* If they don't see the language they need in 7 seconds, they move on."
        },
        "Green Tech (Solar/Wind)": {
            "focus": "Certifications & Safety",
            "tip": "Highlight any OSHA certifications or physical endurance experiences. This is a field that values reliability and safety above all.",
            "book_ref": "💡 *Trend 2026:* This is the fastest-growing sector for entry-level work."
        }
    }
    
    # Default Advice
    return advice.get(role, {
        "focus": "Results over Duties",
        "tip": "Don't just say what you did. Say what you *achieved*. Did you save time? Save money? Make a customer happy?",
        "book_ref": "💡 *Rule:* Every bullet point should have a Number (%, $, or count)."
    })