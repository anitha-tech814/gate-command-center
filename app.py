import streamlit as st
import google.generativeai as genai
import json
import re
from datetime import datetime

# Page Configuration
st.set_page_config(
    page_title="GATE & PSU Career Command Center",
    page_icon="🎓",
    layout="wide"
)

# Initialize Session State Variables
if "xp" not in st.session_state:
    st.session_state.xp = 300
if "error_vault" not in st.session_state:
    st.session_state.error_vault = []

# Setup Gemini API Key from Streamlit Secrets
api_status = {"loaded": False, "message": ""}

if "GEMINI_API_KEY" in st.secrets:
    try:
        genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
        api_status["loaded"] = True
    except Exception as e:
        api_status["loaded"] = False
        api_status["message"] = f"API Key Configuration Error: {str(e)}"
else:
    api_status["loaded"] = False
    api_status["message"] = "GEMINI_API_KEY is missing in Streamlit Secrets."

# ---------------------------------------------------------
# HELPER FUNCTIONS
# ---------------------------------------------------------
def safe_generate(prompt):
    """Generates response using Gemini API safely with fallback models."""
    if not api_status["loaded"]:
        return False, "⚠️ Gemini API key is missing or invalid. Please check Secrets settings in Streamlit."

    models_to_try = ['gemini-1.5-flash', 'gemini-1.5-pro', 'gemini-2.0-flash-exp']
    
    for model_name in models_to_try:
        try:
            model = genai.GenerativeModel(model_name)
            response = model.generate_content(prompt)
            if response and response.text:
                return True, response.text
        except Exception:
            continue

    return False, "❌ Failed to generate response from AI models. Rate limit reached or connection issue."

def parse_quiz_json(raw_text):
    """Extracts and parses JSON quiz structure from AI raw response."""
    try:
        json_match = re.search(r'\[.*\]', raw_text, re.DOTALL)
        if json_match:
            clean_json = json_match.group(0)
            return json.loads(clean_json)
    except Exception:
        pass
    return None

# ---------------------------------------------------------
# TOP HEADER & GAMIFICATION DASHBOARD
# ---------------------------------------------------------
st.title("🎓 GATE & PSU Career Command Center")

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.markdown("### ⏳ Target Exam Countdown")
    target_date = datetime(2027, 2, 6)
    days_left = (target_date - datetime.now()).days
    st.write(f"**GATE Exam Date:** Feb 06, 2027")
    st.success(f"🚀 {days_left} Days Remaining")

with col2:
    st.markdown("### ⭐️ Earned XP")
    st.subheader(f"{st.session_state.xp} XP")
    st.caption("⬆️ +20 XP per quiz completed")

with col3:
    st.markdown("### 🔒 Current Level")
    level = (st.session_state.xp // 200) + 1
    st.subheader(f"Level {level} / 4")

with col4:
    st.markdown("### ⚙️ Target Exam Date")
    st.date_input("Change Target Date:", datetime(2027, 2, 6), key="exam_date")

st.divider()

# ---------------------------------------------------------
# NAVIGATION TABS
# ---------------------------------------------------------
tab1, tab2, tab3, tab4, tab5, tab6, tab7 = st.tabs([
    "📖 Learning Modules", 
    "🎮 Gamified Hub", 
    "🤖 AI Tutor", 
    "📝 Practice Questions", 
    "🎯 AI Quiz Arena", 
    "📚 PYQ Solved Bank", 
    "🛠️ Error Vault"
])

# TAB 1: LEARNING MODULES
with tab1:
    st.header("📖 Core Syllabus & Learning Modules")
    subject = st.selectbox("Select Subject:", ["Data Structures & Algorithms", "Operating Systems", "DBMS", "Computer Networks", "Engineering Mathematics", "General Aptitude"])
    
    st.subheader(f"Key Topics for {subject}")
    if subject == "Data Structures & Algorithms":
        st.write("* Linear Data Structures: Arrays, Linked Lists, Stacks, Queues.")
        st.write("* Trees & Graphs: Binary Trees, BST, AVL Trees, Graph Traversals (BFS/DFS).")
        st.write("* Sorting & Searching: Quick Sort, Merge Sort, Heap Sort, Binary Search.")
    else:
        st.write(f"Complete syllabus overview and study notes for {subject}.")

# TAB 2: GAMIFIED HUB
with tab2:
    st.header("🎮 Gamified Study Progress")
    st.progress(min(st.session_state.xp / 1000, 1.0))
    st.write(f"Earn **{1000 - st.session_state.xp} more XP** to reach Master Level!")

# TAB 3: AI TUTOR
with tab3:
    st.header("🤖 GATE AI Concept Tutor")
    user_query = st.text_input("Ask any concept, formula, or problem explanation:")
    if st.button("Ask AI Tutor"):
        if user_query:
            with st.spinner("AI Tutor is thinking..."):
                success, response = safe_generate(f"Explain this GATE concept clearly with examples: {user_query}")
                if success:
                    st.info(response)
                else:
                    st.error(response)

# TAB 4: PRACTICE QUESTIONS
with tab4:
    st.header("📝 Topic-wise Practice Questions")
    st.caption("Generate practice questions dynamically based on difficulty.")
    
    p_subject = st.selectbox("Select Subject for Practice:", ["Algorithms", "Data Structures", "Operating Systems", "DBMS"], key="prac_sub")
    p_diff = st.select_slider("Difficulty Level:", options=["Easy", "Medium", "Hard"], value="Medium")
    
    if st.button("Generate Practice Problem"):
        with st.spinner("Generating Practice Problem..."):
            prompt = f"Generate 1 high-quality GATE exam practice question for {p_subject} at {p_diff} difficulty level. Include problem statement, options (A, B, C, D), correct option, and step-by-step detailed solution."
            success, response = safe_generate(prompt)
            if success:
                st.markdown(response)
            else:
                st.error(response)

# TAB 5: AI QUIZ ARENA
with tab5:
    st.header("🎯 AI Quiz Arena")
    q_subject = st.selectbox("Select Quiz Topic:", ["Data Structures", "Algorithms", "General Aptitude"], key="quiz_sub")
    
    if st.button("Start Live Quiz"):
        with st.spinner("Generating Quiz Questions..."):
            prompt = f"Generate 2 multiple-choice GATE questions for {q_subject}. Output as raw text with Questions, Options A-D, and Correct Answer."
            success, response = safe_generate(prompt)
            if success:
                st.markdown(response)
                st.session_state.xp += 20
                st.success("🎉 Quiz Completed! You earned +20 XP!")
            else:
                st.error(response)

# TAB 6: PYQ SOLVED BANK
with tab6:
    st.header("📚 Previous Year GATE Solved Questions")
    st.write("Browse and practice actual past GATE questions with full solutions.")
    pyq_sub = st.selectbox("Select PYQ Topic:", ["Data Structures", "DBMS", "Operating Systems"])
    if st.button("Fetch PYQs"):
        with st.spinner("Fetching PYQs..."):
            prompt = f"Provide 2 actual previous year GATE questions for {pyq_sub} with year mentioned and detailed solutions."
            success, response = safe_generate(prompt)
            if success:
                st.markdown(response)
            else:
                st.error(response)

# TAB 7: ERROR VAULT
with tab7:
    st.header("🛠️ My Error Vault")
    st.caption("Save your mistakes during practice and revise them here to avoid repeating them.")
    
    err_text = st.text_area("Note down any concept/mistake you want to revise later:")
    if st.button("Save to Error Vault"):
        if err_text:
            st.session_state.error_vault.append(err_text)
            st.success("Saved to Error Vault!")
            
    if st.session_state.error_vault:
        st.subheader("Saved Mistakes:")
        for idx, item in enumerate(st.session_state.error_vault, 1):
            st.warning(f"**{idx}.** {item}")
