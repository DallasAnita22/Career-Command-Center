from services.expert_knowledge import get_smart_tip

class PortfolioCoach:
    def get_advice(self, user_role="General"):
        category, tip_text = get_smart_tip(user_role)
        return {"category": category, "text": tip_text}