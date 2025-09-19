import streamlit as st
from career_logic import suggest_careers, generate_roadmap
from chatbot import init_chatbot

st.set_page_config(page_title="Career Guidance", layout="wide")
st.title("🎓 AI-Powered Career Guidance")

# Sidebar inputs
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

# NEW: Region input
region = st.sidebar.selectbox(
    "Preferred Job Region",
    ["USA", "India", "Europe", "UK", "Remote"]
)

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

# Show career options
if "career_options" in st.session_state:
    careers = st.session_state["career_options"]  # list, not dict
    st.subheader("✨ Suggested Career Options")

    cols = st.columns(3)
    for idx, career in enumerate(careers):
        with cols[idx % 3]:
            st.markdown(f"**{career['title']}**")
            st.caption(career["description"])

            # Show salary estimate for chosen region
            if "salary" in career and region in career["salary"]:
                st.write(f"💰 Salary in {region}: {career['salary'][region]}")

    # Selection
    selected_career = st.radio(
        "Select a career to view its roadmap:",
        [c["title"] for c in careers],
        horizontal=True
    )

    if selected_career and st.session_state.get("selected_career") != selected_career:
        st.session_state["roadmap"] = generate_roadmap(selected_career, region)
        st.session_state["selected_career"] = selected_career
        st.session_state["conversation"] = init_chatbot(
            st.session_state["roadmap"], selected_career
        )

    if "roadmap" in st.session_state:
        st.subheader(f"📍 Roadmap for {st.session_state['selected_career']}")
        st.markdown(st.session_state["roadmap"])

        # Chatbot
        st.subheader("💬 Ask About This Career Roadmap")
        user_query = st.text_input("Type your question...")
        if user_query:
            response = st.session_state["conversation"].run(user_query)
            st.markdown(f"**Advisor:** {response}")
