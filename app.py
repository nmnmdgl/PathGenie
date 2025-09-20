# app.py
import streamlit as st
from career_logic import suggest_careers, generate_roadmap
from chatbot import init_chatbot

st.set_page_config(page_title="Career Guidance", layout="wide")
st.title("🎓 AI-Powered Career Guidance")

# ---------------- Sidebar ---------------- #
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

region = st.sidebar.selectbox(
    "Preferred Job Region",
    ["India", "USA", "Europe", "UK", "Remote"]
)

# ---------------- Generate Careers ---------------- #
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
        st.session_state["career_options"] = suggest_careers(profile)
        st.session_state.pop("selected_career", None)
        st.session_state.pop("roadmap", None)

# ---------------- Show career options ---------------- #
if "career_options" in st.session_state:
    careers = st.session_state["career_options"].get("careers", [])
    st.subheader("✨ Suggested Career Options")

    cols = st.columns(3)
    for idx, career in enumerate(careers):
        with cols[idx % 3]:
            title = career.get("title", f"Career {idx+1}")
            desc = career.get("description", "")
            st.markdown(f"**{title}**")
            if desc:
                st.caption(desc)

            salary_obj = career.get("salary", {})
            salary_val = salary_obj.get(region, None)
            if salary_val:
                st.write(f"💰 **Estimated Salary ({region})**: {salary_val}")

    # Career selection
    titles = [c.get("title", str(i)) for i, c in enumerate(careers)]
    selected_career = st.radio("Select a career to view its roadmap:", titles, horizontal=True)

    if selected_career and st.session_state.get("selected_career") != selected_career:
        selected_obj = next((c for c in careers if c.get("title") == selected_career), None)
        career_name_for_query = selected_career if selected_obj is None else selected_obj.get("title", selected_career)

        st.session_state["roadmap"] = generate_roadmap(career_name_for_query, region)
        st.session_state["selected_career"] = selected_career
        st.session_state["conversation"] = init_chatbot(st.session_state["roadmap"], career_name_for_query)

# ---------------- Show roadmap & chatbot ---------------- #
if "roadmap" in st.session_state:
    st.subheader(f"📍 Roadmap for {st.session_state.get('selected_career')}")
    roadmap = st.session_state["roadmap"]
    if isinstance(roadmap, list):
        st.markdown("\n".join([f"- {step}" for step in roadmap]))
    else:
        st.markdown(roadmap)

    st.subheader("💬 Ask About This Career Roadmap")
    user_query = st.text_input("Type your question...")
    if user_query:
        response = st.session_state["conversation"].run(user_query)
        st.markdown(f"**Advisor:** {response}")
