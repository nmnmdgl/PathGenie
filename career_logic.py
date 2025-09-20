# career_logic.py
import streamlit as st
import os
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.output_parsers import PydanticOutputParser
from pydantic import BaseModel, Field
from typing import List, Dict

# -----------------------------
# Load API Key from secrets.toml
# -----------------------------
os.environ["GOOGLE_API_KEY"] = st.secrets["API_KEYS"]["GOOGLE_API_KEY"]

# -----------------------------
# Pydantic Models
# -----------------------------
class SalaryRange(BaseModel):
    min: int = Field(..., description="Minimum salary in local currency or USD")
    max: int = Field(..., description="Maximum salary in local currency or USD")


class Career(BaseModel):
    title: str
    description: str
    salary: Dict[str, SalaryRange]


class CareerList(BaseModel):
    careers: List[Career]


# -----------------------------
# LLM + Parser
# -----------------------------
llm = ChatGoogleGenerativeAI(model="gemini-1.5-flash", temperature=0)
parser = PydanticOutputParser(pydantic_object=CareerList)


# -----------------------------
# Functions
# -----------------------------
def suggest_careers(profile: dict) -> CareerList:
    """
    Query Gemini to suggest careers for a given profile.
    """
    query = f"""
    You are an expert career advisor.
    Suggest 3 career paths for this user profile: {profile}.

    Return the result ONLY in this JSON format:
    {{
      "careers": [
        {{
          "title": "Job Title",
          "description": "Role description",
          "salary": {{
            "India": {{"min": 400000, "max": 1500000}},
            "USA": {{"min": 60000, "max": 120000}},
            "Europe": {{"min": 40000, "max": 90000}},
            "UK": {{"min": 35000, "max": 75000}},
            "Remote": {{"min": 50000, "max": 100000}}
          }}
        }}
      ]
    }}
    """

    response = llm.invoke(query)

    try:
        return parser.invoke(response)
    except Exception:
        import json
        try:
            raw = json.loads(response.content)
            if isinstance(raw, list):
                raw = {"careers": raw}
            return CareerList(**raw)
        except Exception as e:
            raise ValueError(f"Could not parse Gemini response: {response.content}") from e


def generate_roadmap(career_title: str, region: str) -> str:
    """
    Generate a step-by-step career roadmap for the given career and region.
    """
    query = f"""
    You are an expert career coach.
    Create a clear roadmap for becoming a **{career_title}** in {region}.
    Include skills to learn, projects to build, certifications, and networking tips.
    Use bullet points and keep it concise but actionable.
    """

    response = llm.invoke(query)
    return response.content.strip()
