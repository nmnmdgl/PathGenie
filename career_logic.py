import streamlit as st
from pydantic import BaseModel
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.prompts import ChatPromptTemplate

# Load API key from Streamlit secrets
GOOGLE_API_KEY = st.secrets["GOOGLE_API_KEY"]

# Initialize the LLM
llm = ChatGoogleGenerativeAI(
    model="gemini-1.5-pro", 
    api_key=GOOGLE_API_KEY,  # Explicitly pass API key
    temperature=0.7
)

class CareerInput(BaseModel):
    interests: str
    skills: str
    education: str

def suggest_careers(interests: str, skills: str, education: str) -> str:
    """Suggest potential career paths based on user profile."""
    prompt = ChatPromptTemplate.from_template(
        "Based on the following details:\n"
        "Interests: {interests}\n"
        "Skills: {skills}\n"
        "Education: {education}\n\n"
        "Suggest 3-5 possible career paths with short reasoning."
    )
    chain = prompt | llm
    response = chain.invoke({"interests": interests, "skills": skills, "education": education})
    return response.content

def generate_roadmap(career_choice: str) -> str:
    """Generate a learning and career roadmap for the chosen career."""
    prompt = ChatPromptTemplate.from_template(
        "Provide a detailed step-by-step roadmap for becoming a successful {career_choice}. "
        "Include skills to learn, certifications, projects, and possible job titles."
    )
    chain = prompt | llm
    response = chain.invoke({"career_choice": career_choice})
    return response.content

