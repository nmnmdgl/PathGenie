import os
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from pydantic import BaseModel, Field
import time

# Load API key
load_dotenv()
api_key = os.getenv("GOOGLE_API_KEY")

# Use flash for faster responses (change to pro if needed)
llm = ChatGoogleGenerativeAI(
    model="gemini-1.5-flash", 
    google_api_key=api_key
)

# Pydantic schema for structured output
class SalaryInfo(BaseModel):
    region: str = Field(description="Region name (e.g., USA, India, Europe)")
    entry: str = Field(description="Entry-level salary")
    mid: str = Field(description="Mid-level salary")
    senior: str = Field(description="Senior-level salary")

class CareerOption(BaseModel):
    title: str = Field(description="Career name")
    description: str = Field(description="Short description of the career")
    salary: SalaryInfo = Field(description="Salary details by region")

class CareerList(BaseModel):
    careers: list[CareerOption]

structured_llm = llm.with_structured_output(CareerList)


def safe_invoke(query, retries=3, delay=2):
    """Retry wrapper for LLM calls to handle timeouts."""
    for attempt in range(retries):
        try:
            return structured_llm.invoke(query).dict()
        except Exception as e:
            if attempt < retries - 1:
                time.sleep(delay)
            else:
                raise RuntimeError(f"LLM call failed after {retries} retries: {e}")


def suggest_careers(profile: dict, region: str = "Global"):
    """Suggests career options based on user profile and region."""
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
    1. Title
    2. Short description
    3. Salary info (entry, mid, senior) for the region: {region}
    """
    return safe_invoke(query)


def generate_roadmap(career: str, region: str = "Global"):
    """Generates a roadmap for a selected career, including salaries."""
    query = f"""
    Provide a step-by-step roadmap to pursue {career} as a career in {region}.
    Include skills, concrete steps, and timelines.
    At the end, also summarize salary expectations (entry, mid, senior) for {region}.
    """
    try:
        return llm.invoke(query).content
    except Exception as e:
        return f"⚠️ Failed to generate roadmap: {e}"
