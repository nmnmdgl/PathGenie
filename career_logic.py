import os
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.pydantic_v1 import BaseModel, Field

# Load API key
load_dotenv()
api_key = os.getenv("GOOGLE_API_KEY")

# Initialize model
llm = ChatGoogleGenerativeAI(model="gemini-1.5-pro", google_api_key=api_key)

# Pydantic schema for structured output
class CareerOption(BaseModel):
    title: str = Field(description="Career name")
    description: str = Field(description="Short description of the career")

class CareerList(BaseModel):
    careers: list[CareerOption]

structured_llm = llm.with_structured_output(CareerList)

# Mock salary data
SALARY_DATA = {
    "Data Scientist": {"India": "₹15 LPA", "USA": "$120k", "Europe": "€85k"},
    "Web Developer": {"India": "₹10 LPA", "USA": "$95k", "Europe": "€70k"},
    "AI Researcher": {"India": "₹18 LPA", "USA": "$150k", "Europe": "€100k"},
}

def suggest_careers(profile: dict):
    """Suggest exactly 3 careers based on user profile."""
    query = f"""
    Based on the following details:
    - Skills: {profile['skills']}
    - Hobbies: {profile['hobbies']}
    - Interests: {profile['interests']}
    - Hours per week: {profile['hours']}
    - Education: {profile['education']}
    - Past Projects: {profile['projects']}

    Suggest exactly 3 possible career options with short descriptions.
    """
    careers = structured_llm.invoke(query).dict()["careers"]
    return {"careers": careers}

def generate_roadmap(career: str, region: str):
    """Generate a roadmap including salary info for the selected region."""
    salary = SALARY_DATA.get(career, {}).get(region, "Not available")
    query = f"""
    Provide a detailed step-by-step roadmap to pursue a career as a {career}.
    Include concrete steps, skills to learn, timelines, and a note on the average salary in {region} ({salary}).
    """
    roadmap_text = llm.invoke(query).content
    # Add salary info at the top
    roadmap_with_salary = f"💰 Average Salary in {region}: {salary}\n\n{roadmap_text}"
    return roadmap_with_salary
