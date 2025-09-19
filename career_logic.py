import streamlit as st
from pydantic import BaseModel
from typing import List, Dict
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.output_parsers import PydanticOutputParser

# ✅ Read API key from Streamlit secrets (nested inside [API_KEYS])
GOOGLE_API_KEY = st.secrets["API_KEYS"]["GOOGLE_API_KEY"]

# Initialize the LLM
llm = ChatGoogleGenerativeAI(
    model="gemini-1.5-flash",
    api_key=GOOGLE_API_KEY,
    temperature=0.3
)

# -----------------------------
# Pydantic Models
# -----------------------------
class Career(BaseModel):
    title: str
    description: str
    skills: List[str]
    salary: Dict[str, str]  # region -> salary mapping
    roadmap: List[str]

class CareerList(BaseModel):
    careers: List[Career]

# Output parser
parser = PydanticOutputParser(pydantic_object=CareerList)

# -----------------------------
# Suggest careers
# -----------------------------
def suggest_careers(profile: str) -> List[Dict]:
    query = f"""
    Based on this user profile: {profile}, suggest 3 careers.
    For each career, include:
    - title
    - description
    - skills (list of 3–5)
    - salary (for regions: US, India, Europe; use ranges like "$70k-$100k")
    - roadmap (5 steps from beginner to advanced)

    Format output according to this JSON schema:
    {parser.get_format_instructions()}
    """

    careers = llm.invoke(query)
    structured = parser.invoke(careers)
    return structured.careers

# -----------------------------
# Generate roadmap
# -----------------------------
def generate_roadmap(career: str) -> List[str]:
    query = f"""
    Provide a step-by-step roadmap for becoming a successful {career}.
    Include 5 stages with actionable milestones.
    """

    response = llm.invoke(query)
    steps = response.content.split("\n")
    return [step.strip("- ") for step in steps if step.strip()]
