from google import genai
import streamlit as st

class AIService:
    def __init__(self, api_key):
        self.api_key = api_key
        self.client = None
        if self.api_key:
            try:
                # 2026 Syntax: Initialize the Client directly
                self.client = genai.Client(api_key=self.api_key)
            except Exception as e:
                print(f"Init Error: {e}")

    def is_configured(self):
        return bool(self.client)

    def magic_rewrite(self, text, role):
        if not self.is_configured(): return "⚠️ Please enter API Key in Sidebar."
        
        prompt = f"""
        Act as an expert Resume Writer for a {role} role.
        Rewrite the following resume bullet point to use the STAR method (Situation, Task, Action, Result).
        Make it sound professional, impactful, and use strong action verbs.
        Keep it concise (1 sentence).
        
        Input text: "{text}"
        
        Rewritten version:
        """
        try:
            # New 2026 Generation Call
            response = self.client.models.generate_content(
                model='gemini-flash-latest', 
                contents=prompt
            )
            return response.text.strip()
        except Exception as e:
            return f"Error: {str(e)}"

    def generate_cover_letter(self, resume_text, job_description):
        if not self.is_configured(): return "⚠️ Please enter API Key in Sidebar."
        
        prompt = f"""
        Write a professional cover letter for a candidate applying to this job.
        
        JOB DESCRIPTION:
        {job_description}
        
        CANDIDATE RESUME SUMMARY:
        {resume_text}
        
        Instructions:
        1. Tone: Professional and enthusiastic.
        2. Highlight 2 specific matches between the resume and JD.
        3. Keep it under 300 words.
        4. Use placeholders like [Your Name] for missing info.
        """
        try:
            response = self.client.models.generate_content(
                model='gemini-flash-latest',
                contents=prompt
            )
            return response.text.strip()
        except Exception as e:
            return f"Error: {str(e)}"

    def simulate_interview(self, job_description):
        if not self.is_configured(): return ["⚠️ Please enter API Key in Sidebar."]
        
        prompt = f"""
        Based on the following Job Description, generate 3 challenging interview questions 
        that a hiring manager would ask.
        
        JOB DESCRIPTION:
        {job_description}
        
        Format output strictly as a Python list of strings.
        Example: ["Question 1", "Question 2", "Question 3"]
        """
        try:
            response = self.client.models.generate_content(
                model='gemini-flash-latest',
                contents=prompt
            )
            text = response.text.replace("[", "").replace("]", "").replace('"', "")
            questions = [q.strip() for q in text.split(",")]
            return questions[:3]
        except Exception as e:
            return [f"Error: {str(e)}"]

    def critique_answer(self, question, user_answer):
        if not self.is_configured(): return "⚠️ Config Error."
        
        prompt = f"""
        You are an Interview Coach. 
        Question: "{question}"
        Candidate Answer: "{user_answer}"
        
        Provide a brief critique (2-3 sentences). 
        Did they use the STAR method? Did they sound confident? 
        Give one specific improvement.
        """
        try:
            response = self.client.models.generate_content(
                model='gemini-flash-latest',
                contents=prompt
            )
            return response.text.strip()
        except Exception as e:
            return f"Error: {str(e)}"
