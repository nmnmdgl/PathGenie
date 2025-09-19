# career_logic.py
import streamlit as st
from langchain_google_genai import ChatGoogleGenerativeAI
from pydantic import BaseModel, Field
from typing import Dict, List

# Load API key from Streamlit secrets
GOOGLE_API_KEY = st.secrets["API_KEYS"]["GOOGLE_API_KEY"]

# Initialize model
llm = ChatGoogleGenerativeAI(model="gemini-1.5-pro", google_api_key=GOOGLE_API_KEY)

# Pydantic schema for structured output
class Career(BaseModel):
    title: str = Field(description="Career name")
    description: str = Field(description="Short description of the career")
    salary: Dict[str, str] = Field(description="Estimated salary ranges for regions like India, USA, Europe, UK, Remote")

class CareerList(BaseModel):
    careers: List[Career]

structured_llm = llm.with_structured_output(CareerList)


def suggest_careers(profile: dict):
    """Suggests career options based on user profile."""
    query = f"""
    Based on the following details:
    - Skills: {profile['skills']}
    - Hobbies: {profile['hobbies']}
    - Interests: {profile['interests']}
    - Hours per week: {profile['hours']}
    - Education: {profile['education']}
    - Past Projects: {profile['projects']}

    Suggest exactly 3 possible career options.
    For each option, return:
    - title (career name)
    - description (short description)
    - salary (a JSON object with keys: India, USA, Europe, UK, Remote)
    """
    result = structured_llm.invoke(query)
    return result.careers  # return list of Career objects


def generate_roadmap(career: str, region: str):
    """Generates a roadmap for a selected career and includes salary context."""
    query = f"""
    Give me a step-by-step roadmap to pursue {career} as a career in {region}.
    Include concrete steps, skills, and timelines.
    Also mention the typical salary scale for {career} in {region}.
    """
    return llm.invoke(query).content
