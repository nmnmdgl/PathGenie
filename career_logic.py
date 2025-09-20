# career_logic.py
import streamlit as st
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.output_parsers import PydanticOutputParser
from pydantic import BaseModel, Field
from typing import List, Dict, Any, Union
import json


# Load API key from Streamlit secrets
GOOGLE_API_KEY = st.secrets["API_KEYS"]["GOOGLE_API_KEY"]


# ---------------- Pydantic Models ---------------- #
class Career(BaseModel):
    title: str = Field(..., description="The career title")
    description: str = Field(..., description="A short description of the career")
    salary: Dict[str, Union[str, Dict[str, Union[int, float]]]] = Field(
        default_factory=dict,
        description=(
            "Estimated salaries by region. Can be a string like '5-8 LPA' "
            "or a dict with min/max (e.g., {'min': 60000, 'max': 120000})"
        )
    )


class CareerList(BaseModel):
    careers: List[Career]


# ---------------- LLM Setup ---------------- #
llm = ChatGoogleGenerativeAI(
    model="gemini-1.5-flash",
    google_api_key=GOOGLE_API_KEY,
)
parser = PydanticOutputParser(pydantic_object=CareerList)


# ---------------- Helpers ---------------- #
def safe_parse_salary(salary_field: Any) -> Dict[str, str]:
    """Normalize salary into {region: 'min-max'} format."""
    if isinstance(salary_field, dict):
        normalized = {}
        for region, val in salary_field.items():
            if isinstance(val, dict) and "min" in val and "max" in val:
                normalized[region] = f"{val['min']} - {val['max']}"
            else:
                normalized[region] = str(val)
        return normalized
    if isinstance(salary_field, str):
        try:
            return json.loads(salary_field.replace("'", '"'))
        except Exception:
            return {}
    return {}


# ---------------- Core Functions ---------------- #
def suggest_careers(profile: Dict[str, Any]) -> Dict[str, Any]:
    query = (
        f"Suggest 3 careers for someone with profile: {profile}. "
        f"Return JSON strictly in the format: {{'careers': [{{'title':.., 'description':.., 'salary':..}}]}}. "
        f"The 'salary' must be a dictionary with regions as keys "
        f"(India, USA, Europe, UK, Remote). Each region value can be either "
        f"a string (like '5-8 LPA') or an object with 'min' and 'max'."
    )

    raw = llm.invoke(query).content.strip()

    # Try to parse JSON safely
    try:
        data = json.loads(raw)
    except Exception:
        # Sometimes LLM outputs list directly
        try:
            data = json.loads(raw.replace("'", '"'))
        except Exception:
            raise ValueError(f"Could not parse LLM response: {raw[:200]}")

    # Auto-wrap if bare list
    if isinstance(data, list):
        data = {"careers": data}

    # Parse into Pydantic model
    parsed = CareerList(**data)

    # Normalize salaries
    for career in parsed.careers:
        career.salary = safe_parse_salary(career.salary)

    return parsed.dict()


def generate_roadmap(career_name: str, region: str) -> List[str]:
    query = (
        f"Generate a step-by-step roadmap for becoming a {career_name} in {region}. "
        f"List 5-7 key steps as bullet points."
    )
    result = llm.invoke(query)
    return [line.strip("-• ") for line in result.content.split("\n") if line.strip()]
