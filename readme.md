# 🎓 AI-Powered Career Guidance

An interactive **Streamlit application** that provides **personalized career guidance**, step-by-step **roadmaps**, region-based **salary insights**, and an integrated **AI-powered chatbot** for career queries.  

---

## ✨ Features

- 🧭 **Personalized Career Suggestions**  
  Get 3 tailored career recommendations based on your **skills, hobbies, interests, education, and projects**.

- 🗺️ **Career Roadmaps**  
  Each career comes with a **detailed roadmap** (skills to learn, timelines, projects, and resources).  

- 💰 **Region-Specific Salary Insights**  
  Roadmaps display **average salary ranges** for your chosen region (India, USA, or Europe).  

- 🤖 **Integrated Chatbot**  
  Ask follow-up questions about the selected roadmap with a built-in **AI career advisor**.  

- 🎨 **Modern UI**  
  Built with Streamlit, offering an **intuitive sidebar input panel**, **career cards**, and a clean **roadmap display**.  

---

## 🛠️ Tech Stack

- **Frontend/UI**: [Streamlit](https://streamlit.io/)  
- **LLM**: Google Gemini (`langchain-google-genai`)  
- **Language**: Python 3.10+  
- **Environment Management**: Conda / venv  
- **Dependencies**:  
  - `streamlit`  
  - `python-dotenv`  
  - `langchain-core`  
  - `langchain-google-genai`  

---

## 📂 Project Structure

career_advisor/
│── app.py              # Main Streamlit app (UI + chatbot integration)
│── career_logic.py     # Core logic for career suggestions & roadmaps
│── chatbot.py          # Chatbot initialization with context
│── .env                # Stores your GOOGLE_API_KEY
│── README.md           # Project documentation


