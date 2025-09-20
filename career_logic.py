# career_logic.py
import streamlit as st
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.output_parsers import PydanticOutputParser
from pydantic import BaseModel, Field
from typing import List, Dict, Any
import json

# Load API key from Streamlit secrets
GOOGLE_API_KEY = st.secrets["API_KEYS"]["GOOGLE_API_KEY"]

# ---------------- Pydantic Models ---------------- #
class Career(BaseModel):
    title: str = Field(..., description="The career title")
    description: str = Field(..., description="A short description of the career")
    salary: Dict[str, str] = Field(
        default_factory=dict,
        description="Estimated salaries by region (e.g., {'India': '5-8 LPA', 'USA': '80-120k USD'})"
    )

class CareerList(BaseModel):
    careers: List[Career]


# ---------------- LLM Setup ---------------- #
llm = ChatGoogleGenerativeAI(model="gemini-1.5-flash", google_api_key=GOOGLE_API_KEY)
parser = PydanticOutputParser(pydantic_object=CareerList)


# ---------------- Helpers ---------------- #
def safe_parse_salary(salary_field: Any) -> Dict[str, str]:
    """Ensure salary is always returned as a dictionary."""
    if isinstance(salary_field, dict):
        return salary_field
    if isinstance(salary_field, str):
        try:
            return json.loads(salary_field.replace("'", '"'))  # convert single quotes → double quotes
        except Exception:
            return {}
    return {}


# ---------------- Core Functions ---------------- #
def suggest_careers(profile: Dict[str, Any]) -> Dict[str, Any]:
    query = (
        f"Suggest 3 careers for someone with profile: {profile}. "
        f"Return JSON with fields: title, description, and salary (dict with India, USA, Europe, UK, Remote)."
    )

    result = llm.invoke(query)
    parsed = parser.invoke(result)

    # Fix salary if model returned a string
    for career in parsed.careers:
        career.salary = safe_parse_salary(career.salary)

    return parsed.dict()


def generate_roadmap(career_name: str) -> List[str]:
    query = (
        f"Generate a step-by-step roadmap for becoming a {career_name}. "
        f"List 5-7 key steps as bullet points."
    )
    result = llm.invoke(query)
    return [line.strip("-• ") for line in result.content.split("\n") if line.strip()]
