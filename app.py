# app.py
import streamlit as st
from career_logic import suggest_careers, generate_roadmap
from chatbot import init_chatbot
from typing import Any

st.set_page_config(page_title="Career Guidance", layout="wide")
st.title("🎓 AI-Powered Career Guidance")


# ---------------- Utility helpers ----------------
def get_attr(obj: Any, key: str):
    """Safely get attribute from dict, pydantic model (v1/v2) or object."""
    # dict-like
    if isinstance(obj, dict):
        return obj.get(key)
    # pydantic v2
    if hasattr(obj, "model_dump"):
        try:
            return obj.model_dump().get(key)
        except Exception:
            pass
    # pydantic v1 or plain object
    if hasattr(obj, "dict"):
        try:
            return obj.dict().get(key)
        except Exception:
            pass
    if hasattr(obj, key):
        return getattr(obj, key)
    # fallback to __dict__
    if hasattr(obj, "__dict__"):
        return obj.__dict__.get(key)
    return None


def get_salary_for_region(salary_obj: Any, region: str):
    """Return salary value for selected region from salary object/dict/model."""
    if salary_obj is None:
        return None
    # if already a dict
    if isinstance(salary_obj, dict):
        # try exact region, then lowercase, then first available
        return salary_obj.get(region) or salary_obj.get(region.lower()) or next(iter(salary_obj.values()), None)
    # if pydantic with model_dump
    if hasattr(salary_obj, "model_dump"):
        try:
            sd = salary_obj.model_dump()
            return sd.get(region) or sd.get(region.lower()) or next(iter(sd.values()), None)
        except Exception:
            pass
    # if pydantic v1 dict()
    if hasattr(salary_obj, "dict"):
        try:
            sd = salary_obj.dict()
            return sd.get(region) or sd.get(region.lower()) or next(iter(sd.values()), None)
        except Exception:
            pass
    # fallback
    return str(salary_obj)


# ---------------- Sidebar inputs ---------------- #
st.sidebar.header("Tell us about yourself")
skills = st.sidebar.multiselect(
    "Skills",
    ["Python", "Data Analysis", "Machine Learning", "Web Development", "Finance", "Design"]
)
hobbies = st.sidebar.multiselect(
    "Hobbies",
    ["Reading", "Gaming", "Sports", "Traveling", "Music", "Art"]
)
interests = st.sidebar.multiselect(
    "Interests",
    ["AI", "Business", "Healthcare", "Education", "Technology", "Research"]
)
hours = st.sidebar.slider("Hours per week you can commit", 1, 40, 10)
education = st.sidebar.selectbox("Education Level", ["High School", "Bachelor's", "Master's", "PhD"])
projects = st.sidebar.text_area("List some projects you’ve worked on")

# Region selection
region = st.sidebar.selectbox(
    "Preferred Job Region",
    ["India", "USA", "Europe", "UK", "Remote"]
)

# Generate button
if st.sidebar.button("Generate Career Options"):
    with st.spinner("Analyzing your profile..."):
        profile = {
            "skills": skills,
            "hobbies": hobbies,
            "interests": interests,
            "hours": hours,
            "education": education,
            "projects": projects,
            "region": region,
        }
        # expect a list from suggest_careers()
        st.session_state["career_options"] = suggest_careers(profile)
        st.session_state.pop("selected_career", None)
        st.session_state.pop("roadmap", None)


# ---------------- Show career options ---------------- #
if "career_options" in st.session_state:
    careers = st.session_state["career_options"]  # should be a list
    st.subheader("✨ Suggested Career Options")

    cols = st.columns(3)
    for idx, career in enumerate(careers):
        with cols[idx % 3]:
            title = get_attr(career, "title") or get_attr(career, "name") or f"Career {idx+1}"
            desc = get_attr(career, "description") or ""
            st.markdown(f"**{title}**")
            if desc:
                st.caption(desc)

            # salary display for chosen region (if present)
            salary_obj = get_attr(career, "salary")
            salary_val = get_salary_for_region(salary_obj, region)
            if salary_val:
                st.write(f"💰 **Estimated Salary ({region})**: {salary_val}")

    # selection radio (use titles)
    titles = [get_attr(c, "title") or get_attr(c, "name") or str(i) for i, c in enumerate(careers)]
    selected_career = st.radio(
        "Select a career to view its roadmap:",
        titles,
        horizontal=True
    )

    # Generate roadmap for selected career
    if selected_career and st.session_state.get("selected_career") != selected_career:
        # find career object matching the selected title
        selected_obj = None
        for c in careers:
            cand_title = get_attr(c, "title") or get_attr(c, "name")
            if cand_title == selected_career:
                selected_obj = c
                break

        # fallback: if not found, use the selected string itself
        career_name_for_query = selected_career if selected_obj is None else (get_attr(selected_obj, "title") or selected_career)

        st.session_state["roadmap"] = generate_roadmap(career_name_for_query, region)
        st.session_state["selected_career"] = selected_career
        st.session_state["conversation"] = init_chatbot(st.session_state["roadmap"], career_name_for_query)

# ---------------- Show roadmap & chatbot ---------------- #
if "roadmap" in st.session_state:
    st.subheader(f"📍 Roadmap for {st.session_state.get('selected_career')}")
    st.markdown(st.session_state["roadmap"])

    st.subheader("💬 Ask About This Career Roadmap")
    user_query = st.text_input("Type your question...")
    if user_query:
        response = st.session_state["conversation"].run(user_query)
        st.markdown(f"**Advisor:** {response}")
