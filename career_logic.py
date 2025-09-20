# career_logic.py

from typing import List, Dict
from pydantic import BaseModel, Field, ValidationError
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.output_parsers import PydanticOutputParser
import json
import toml
import os


# -----------------------------
# Load API Key from .toml
# -----------------------------
config = toml.load("config.toml")
os.environ["GOOGLE_API_KEY"] = config["API_KEYS"]["GOOGLE_API_KEY"]


# -----------------------------
# Pydantic Models
# -----------------------------
class SalaryRange(BaseModel):
    min: int = Field(..., description="Minimum salary in local currency or USD")
    max: int = Field(..., description="Maximum salary in local currency or USD")


class Career(BaseModel):
    title: str = Field(..., description="The job title")
    description: str = Field(..., description="Brief description of the role")
    salary: Dict[str, SalaryRange] = Field(
        ..., description="Salary ranges by region (India, USA, Europe, UK, Remote)"
    )


class CareerList(BaseModel):
    careers: List[Career]


# -----------------------------
# LLM + Parser
# -----------------------------
llm = ChatGoogleGenerativeAI(model="gemini-1.5-flash", temperature=0)
parser = PydanticOutputParser(pydantic_object=CareerList)


def suggest_careers(profile: str) -> CareerList:
    """
    Query the Gemini LLM to suggest careers for a given profile.
    Always enforces the format: {"careers": [...]}
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
        # Try structured parsing first
        return parser.invoke(response)

    except ValidationError:
        # Fallback: try loading raw JSON and fixing structure
        try:
            raw = json.loads(response.content)

            # If Gemini returned just a list, wrap it
            if isinstance(raw, list):
                raw = {"careers": raw}

            return CareerList(**raw)

        except Exception as inner_e:
            raise ValueError(f"Could not parse LLM response: {response.content}") from inner_e
