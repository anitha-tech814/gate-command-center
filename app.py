import os
import json
import time
import re
from datetime import datetime, date
import streamlit as st
import google.generativeai as genai
from dotenv import load_dotenv

# ------------------------------------------
# PAGE CONFIGURATION
# ------------------------------------------
st.set_page_config(
    page_title="GATE & PSU Career Command Center",
    page_icon="🎓",
    layout="wide"
)

# ------------------------------------------
# LOAD ENVIRONMENT & SETUP API
# ------------------------------------------
load_dotenv(override=True)

# 1. First check Streamlit secrets, then .env, then direct fallback key
api_key = None

try:
    if "GEMINI_API_KEY" in st.secrets:
        api_key = st.secrets["GEMINI_API_KEY"]
except Exception:
    pass

if not api_key:
    api_key = os.getenv("GEMINI_API_KEY")

# Direct key fallback for immediate working
if not api_key:
    api_key = ""

api_status = {"loaded": False, "message": ""}

if api_key and len(api_key.strip()) > 10:
    try:
        genai.configure(api_key=api_key.strip())
        api_status["loaded"] = True
        api_status["message"] = "API Key Connected Successfully!"
    except Exception as e:
        api_status["loaded"] = False
        api_status["message"] = f"Configuration Error: {e}"
else:
    api_status["loaded"] = False
    api_status["message"] = "Invalid or Missing Gemini API Key."

# ------------------------------------------
# HELPER FUNCTIONS
# ------------------------------------------
def safe_generate(prompt):
    """Generates response using Gemini API safely with fallback models."""
    if not api_status["loaded"]:
        return False, "⚠️ Gemini API key is missing or invalid. Please check Tab 8 Settings."
    
    models_to_try = ['gemini-1.5-flash', 'gemini-1.5-pro', 'gemini-2.0-flash']
    
    for model_name in models_to_try:
        try:
            model = genai.GenerativeModel(model_name)
            response = model.generate_content(prompt)
            if response and response.text:
                return True, response.text
        except Exception as e:
            continue

    return False, "❌ Failed to generate response from AI models. Rate limit reached or connection issue."

def parse_quiz_json(raw_text):
    """Extracts and parses JSON quiz structure from AI raw response."""
    try:
        json_match = re.search(r'\[.*\]', raw_text, re.DOTALL)
        if json_match:
            clean_json = json_match.group(0)
            return json.loads(clean_json)
        return json.loads(raw_text)
    except Exception:
        return None

# ------------------------------------------
# SESSION STATE INITIALIZATION
# ------------------------------------------
if 'unlocked_level' not in st.session_state:
    st.session_state.unlocked_level = 1
if 'xp_points' not in st.session_state:
    st.session_state.xp_points = 150
if 'badges' not in st.session_state:
    st.session_state.badges = ["🌱 Beginner Explorer"]
if 'exam_date' not in st.session_state:
    st.session_state.exam_date = date(2027, 2, 6) # Default Target GATE Date
if 'quiz_started' not in st.session_state:
    st.session_state.quiz_started = False
if 'quiz_submitted' not in st.session_state:
    st.session_state.quiz_submitted = False
if 'quiz_questions' not in st.session_state:
    st.session_state.quiz_questions = []
if 'quiz_answers' not in st.session_state:
    st.session_state.quiz_answers = {}
if 'quiz_score_history' not in st.session_state:
    st.session_state.quiz_score_history = []
if 'quiz_start_time' not in st.session_state:
    st.session_state.quiz_start_time = 0
if 'quiz_time_limit' not in st.session_state:
    st.session_state.quiz_time_limit = 10
if 'quiz_elapsed' not in st.session_state:
    st.session_state.quiz_elapsed = 0

# ------------------------------------------
# HEADER & DASHBOARD WITH EXAM COUNTDOWN
# ------------------------------------------
st.title("🎓 GATE & PSU Career Command Center")

# Calculate Days Left
today = date.today()
days_left = (st.session_state.exam_date - today).days

# Top Executive Dashboard
dash_col1, dash_col2, dash_col3, dash_col4 = st.columns([2, 1.2, 1.2, 1.6])

with dash_col1:
    st.subheader("⏳ Target Exam Countdown")
    if days_left > 0:
        st.metric("GATE Exam Date", f"{st.session_state.exam_date.strftime('%b %d, %Y')}", f"{days_left} Days Remaining 🚀")
    else:
        st.error("🎯 Exam Time Is Here! All the best!")

with dash_col2:
    st.metric("⭐ Earned XP", f"{st.session_state.xp_points} XP", "+20 XP per quiz")

with dash_col3:
    st.metric("🔓 Current Level", f"Level {st.session_state.unlocked_level} / 4")

with dash_col4:
    st.subheader("⚙️ Target Exam Date")
    new_date = st.date_input("Change Target Date:", value=st.session_state.exam_date)
    if new_date != st.session_state.exam_date:
        st.session_state.exam_date = new_date
        st.rerun()

st.divider()

# ------------------------------------------
# MAIN NAVIGATION TABS (8 TABS)
# ------------------------------------------
tab1, tab2, tab3, tab4, tab5, tab6, tab7, tab8 = st.tabs([
    "📖 Learning Modules",
    "🎮 Gamified Hub",
    "🤖 AI Tutor",
    "📝 Practice Questions",
    "🎯 AI Quiz Arena",
    "📚 PYQ Solved Bank",
    "🛡️ Error Vault",
    "🏢 PSU & Settings"
])

# ------------------------------------------
# TAB 1: LEARNING MODULES
# ------------------------------------------
with tab1:
    st.header("📖 Core Syllabus & Learning Modules")
    subject = st.selectbox(
        "Select Subject:",
        ["Data Structures & Algorithms", "Database Management Systems (DBMS)", "Operating Systems (OS)", "Computer Networks (CN)", "Theory of Computation (TOC)"]
    )
    
    st.subheader(f"Key Topics for {subject}")
    if subject == "Data Structures & Algorithms":
        st.markdown("""
        * **Linear Data Structures:** Arrays, Linked Lists, Stacks, Queues.
        * **Trees & Graphs:** Binary Search Trees, AVL Trees, Heap, BFS, DFS, Dijkstra's Algorithm.
        * **Algorithm Design:** Dynamic Programming, Greedy Approach, Divide and Conquer.
        """)
    elif subject == "Database Management Systems (DBMS)":
        st.markdown("""
        * **ER Model & Relational Algebra:** Tuple Relational Calculus, Domain Relational Calculus.
        * **SQL & Normalization:** 1NF, 2NF, 3NF, BCNF, Functional Dependencies.
        * **Transactions & Indexing:** ACID Properties, Concurrency Control, B & B+ Trees.
        """)
    else:
        st.info("Select topics from syllabus and prepare core concepts for GATE examination.")

# ------------------------------------------
# TAB 2: GAMIFIED LEARNING HUB
# ------------------------------------------
with tab2:
    st.header("🎮 Gamified Learning & Quest Tracker")
    st.write("Complete learning quests, earn XP points, unlock higher levels, and collect GATE badges!")

    # Gamification Stats Header
    col_xp, col_lvl, col_badge = st.columns(3)
    with col_xp:
        st.metric("⭐ Total XP", f"{st.session_state.xp_points} XP")
    with col_lvl:
        st.metric("🔓 Current Level", f"Level {st.session_state.unlocked_level} / 4")
    with col_badge:
        st.metric("🏅 Badges Earned", len(st.session_state.badges))

    st.divider()

    # Level Roadmap
    st.subheader("🗺️ GATE CS Mastery Roadmap")
    
    levels_data = [
        {"level": 1, "name": "Level 1: Fundamentals (Linear DS, Basic SQL, Process Mgmt)", "req_xp": 0},
        {"level": 2, "name": "Level 2: Intermediate (Trees, Graphs, Normalization, Threads)", "req_xp": 200},
        {"level": 3, "name": "Level 3: Advanced (DP, Concurrency, Virtual Memory, IP Addressing)", "req_xp": 500},
        {"level": 4, "name": "Level 4: GATE Grand Master (Mixed PYQs & High Weightage Mock Tests)", "req_xp": 1000}
    ]

    for lvl in levels_data:
        is_unlocked = st.session_state.unlocked_level >= lvl["level"]
        status_icon = "🟢 Unlocked" if is_unlocked else "🔒 Locked"
        
        with st.expander(f"{'⚡' if is_unlocked else '🔒'} {lvl['name']} — {status_icon}"):
            if is_unlocked:
                st.success(f"You have unlocked Level {lvl['level']}! Start solving problems to gain more XP.")
                if st.button(f"Start Quests for Level {lvl['level']}", key=f"lvl_btn_{lvl['level']}"):
                    st.session_state.xp_points += 50
                    if st.session_state.xp_points >= 200 and st.session_state.unlocked_level == 1:
                        st.session_state.unlocked_level = 2
                        st.session_state.badges.append("⚔️ Intermediate Challenger")
                        st.balloons()
                    st.rerun()
            else:
                st.warning(f"Requires {lvl['req_xp']} XP to unlock. Keep practicing in Tab 4 & Tab 5!")

    st.divider()
    st.subheader("🏆 Your Badges Collection")
    badge_cols = st.columns(4)
    for idx, badge in enumerate(st.session_state.badges):
        with badge_cols[idx % 4]:
            st.info(f"**{badge}**")

# ------------------------------------------
# TAB 3: AI TUTOR
# ------------------------------------------
with tab3:
    st.header("🤖 AI Interactive Tutor")
    st.write("Ask any doubt regarding GATE CS/IT syllabus, algorithms, concepts, or numerical problems.")
    
    user_query = st.text_area("Enter your question/doubt here:", placeholder="Explain B+ Tree insertion with an example...")
    
    if st.button("Ask AI Tutor", type="primary"):
        if user_query.strip():
            with st.spinner("AI Tutor is analyzing your query..."):
                prompt = f"Act as an expert GATE Computer Science professor. Answer this query in a clear, structured way with step-by-step logic, key formulas, and an example if needed:\n\n{user_query}"
                success, response = safe_generate(prompt)
                if success:
                    st.success("### Answer:")
                    st.markdown(response)
                else:
                    st.error(response)
        else:
            st.warning("Please enter a question before submitting.")

# ------------------------------------------
# TAB 4: PRACTICE QUESTIONS
# ------------------------------------------
with tab4:
    st.header("📝 Topic-wise Practice Questions")
    st.write("Generate practice questions dynamically based on difficulty.")
    
    p_subject = st.selectbox("Select Subject for Practice:", ["Algorithms", "DBMS", "Operating Systems", "Computer Networks"], key="p_sub")
    p_diff = st.select_slider("Difficulty Level:", options=["Easy", "Medium", "Hard", "GATE Standard"])
    
    if st.button("Generate Practice Problem"):
        with st.spinner("Creating custom practice problem..."):
            prompt = f"Generate 1 high-quality {p_diff} level multiple-choice problem for GATE CS on subject: {p_subject}. Provide statement, 4 options (A, B, C, D), correct option, and detailed explanation."
            success, res = safe_generate(prompt)
            if success:
                st.markdown(res)
            else:
                st.error(res)

# ------------------------------------------
# TAB 5: AI QUIZ ARENA
# ------------------------------------------
with tab5:
    st.header("🎯 AI Dynamic Quiz Arena")

    if not st.session_state.quiz_started and not st.session_state.quiz_submitted:
        col1, col2, col3 = st.columns(3)
        with col1:
            quiz_subject = st.selectbox("Subject", ["Algorithms", "DBMS", "Operating Systems", "Computer Networks"], key="quiz_subject_select")
        with col2:
            quiz_difficulty = st.selectbox("Difficulty", ["Easy", "Medium", "Hard", "GATE Level"], key="quiz_difficulty_select")
        with col3:
            time_limit = st.slider("Time Limit (Minutes)", 5, 30, 10)

        if st.button("🚀 Start AI Generated Quiz", type="primary", use_container_width=True):
            with st.spinner("AI is generating your custom quiz..."):
                prompt = f"""Generate a 5-question multiple choice quiz on '{quiz_subject}' at '{quiz_difficulty}' level for GATE CS.
Return ONLY a valid JSON array of objects with no extra formatting, markdown ticks, or text.
JSON Structure template:
[{"id": 1, "question": "...", "options": {"A": "...", "B": "...", "C": "...", "D": "..."}, "correct_answer": "A", "explanation": "...", "marks": 2}]"""
                
                success, result = safe_generate(prompt)
                if success:
                    questions = parse_quiz_json(result)
                    if questions and len(questions) >= 1:
                        st.session_state.quiz_questions = questions[:5]
                        st.session_state.quiz_answers = {}
                        st.session_state.quiz_started = True
                        st.session_state.quiz_submitted = False
                        st.session_state.quiz_start_time = time.time()
                        st.session_state.quiz_time_limit = time_limit
                        st.session_state.quiz_elapsed = 0
                        st.rerun()
                    else:
                        st.error("❌ Could not parse quiz questions from AI response. Please try again.")
                        with st.expander("Debug: Raw AI Response"):
                            st.code(result)
                else:
                    st.warning(result)

        if st.session_state.quiz_score_history:
            st.divider()
            st.subheader("📈 Your Recent Quiz Scores")
            for i, record in enumerate(reversed(st.session_state.quiz_score_history[-5:]), 1):
                score_pct = int(record['percentage'])
                score_icon = "🏆" if score_pct >= 80 else "✅" if score_pct >= 50 else "📖"
                st.write(f"{score_icon} **Quiz {len(st.session_state.quiz_score_history) - i + 1}** "
                         f"| {record['subject']} ({record['difficulty']}) "
                         f"| **{record['score']}/{record['total']} marks ({score_pct}%)** "
                         f"| Time: {record['time_taken']}")

    elif st.session_state.quiz_started and not st.session_state.quiz_submitted:
        questions = st.session_state.quiz_questions
        total_marks = sum(q.get('marks', 1) for q in questions)

        elapsed = time.time() - st.session_state.quiz_start_time
        remaining = max(0, st.session_state.quiz_time_limit * 60 - elapsed)
        mins_left = int(remaining // 60)
        secs_left = int(remaining % 60)

        timer_col, marks_col, count_col = st.columns(3)
        with timer_col:
            if remaining > 60:
                st.info(f"⏱️ **Time Remaining: {mins_left}m {secs_left:02d}s**")
            elif remaining > 0:
                st.warning(f"⚠️ **Hurry! {mins_left}m {secs_left:02d}s left!**")
            else:
                st.error("🚨 **Time's Up!**")
        with marks_col:
            st.info(f"📝 **Total Marks: {total_marks}**")
        with count_col:
            answered = len(st.session_state.quiz_answers)
            st.info(f"✅ **Answered: {answered} / {len(questions)}**")

        st.divider()

        for idx, q in enumerate(questions):
            q_id = q.get('id', idx + 1)
            marks = q.get('marks', 1)
            st.markdown(f"### Question {q_id} ({marks} mark{'s' if marks > 1 else ''})")
            st.markdown(f"**{q.get('question', 'Question text missing')}**")

            options = q.get('options', {})
            option_list = [f"{key}: {val}" for key, val in options.items()]

            if option_list:
                prev_answer = st.session_state.quiz_answers.get(str(q_id))
                prev_index = None
                if prev_answer:
                    for i, opt in enumerate(option_list):
                        if opt.startswith(prev_answer + ":"):
                            prev_index = i
                            break

                selected = st.radio(
                    f"Your answer for Q{q_id}:",
                    option_list,
                    index=prev_index,
                    key=f"quiz_q_{q_id}",
                    label_visibility="collapsed"
                )

                if selected:
                    answer_key = selected.split(":")[0].strip()
                    st.session_state.quiz_answers[str(q_id)] = answer_key

            st.divider()

        btn_col1, btn_col2 = st.columns([3, 1])
        with btn_col1:
            if st.button("📩 Submit Quiz & View Results", type="primary", use_container_width=True):
                st.session_state.quiz_submitted = True
                st.session_state.quiz_elapsed = time.time() - st.session_state.quiz_start_time
                st.rerun()
        with btn_col2:
            if st.button("🗑️ Abort Quiz", use_container_width=True):
                st.session_state.quiz_started = False
                st.session_state.quiz_submitted = False
                st.session_state.quiz_questions = []
                st.session_state.quiz_answers = {}
                st.rerun()

    elif st.session_state.quiz_submitted:
        questions = st.session_state.quiz_questions
        answers = st.session_state.quiz_answers
        elapsed = st.session_state.quiz_elapsed

        mins_taken = int(elapsed // 60)
        secs_taken = int(elapsed % 60)
        time_str = f"{mins_taken}m {secs_taken:02d}s"

        total_marks = sum(q.get('marks', 1) for q in questions)
        earned_marks = 0
        correct_count = 0

        st.subheader("📊 Quiz Results")
        st.divider()

        for idx, q in enumerate(questions):
            q_id = str(q.get('id', idx + 1))
            marks = q.get('marks', 1)
            correct = q.get('correct_answer', '')
            user_ans = answers.get(q_id, "Not Answered")
            is_correct = user_ans == correct

            if is_correct:
                earned_marks += marks
                correct_count += 1

            icon = "✅" if is_correct else "❌" if user_ans != "Not Answered" else "⬜"
            status = "Correct" if is_correct else "Incorrect" if user_ans != "Not Answered" else "Skipped"

            with st.expander(f"{icon} Question {q_id}: {status} ({marks} mark{'s' if marks > 1 else ''})", expanded=(not is_correct)):
                st.markdown(f"**{q.get('question', '')}**")
                options = q.get('options', {})
                for key, val in options.items():
                    if key == correct and key == user_ans:
                        st.markdown(f"✅ **{key}: {val}** ← Your Answer (Correct!)")
                    elif key == correct:
                        st.markdown(f"✅ **{key}: {val}** ← Correct Answer")
                    elif key == user_ans:
                        st.markdown(f"❌ ~~{key}: {val}~~ ← Your Answer")
                    else:
                        st.markdown(f"&nbsp;&nbsp;&nbsp;&nbsp;{key}: {val}")

                st.info(f"💡 **Explanation:** {q.get('explanation', 'No explanation available.')}")

        st.divider()
        percentage = (earned_marks / total_marks * 100) if total_marks > 0 else 0

        xp_earned = int(earned_marks * 20)
        st.session_state.xp_points += xp_earned
        st.toast(f"🎉 Earned +{xp_earned} XP!")

        sc1, sc2, sc3, sc4 = st.columns(4)
        sc1.metric("Score", f"{earned_marks} / {total_marks}")
        sc2.metric("Accuracy", f"{int(percentage)}%")
        sc3.metric("Correct", f"{correct_count} / {len(questions)}")
        sc4.metric("Time Taken", time_str)

        score_record = {
            'subject': st.session_state.get('quiz_subject_select', 'Unknown'),
            'difficulty': st.session_state.get('quiz_difficulty_select', 'Unknown'),
            'score': earned_marks,
            'total': total_marks,
            'percentage': percentage,
            'correct': correct_count,
            'out_of': len(questions),
            'time_taken': time_str
        }
        
        if not st.session_state.quiz_score_history or st.session_state.quiz_score_history[-1] != score_record:
            st.session_state.quiz_score_history.append(score_record)

        st.divider()
        if st.button("🔄 Take Another Quiz", type="primary", use_container_width=True):
            st.session_state.quiz_started = False
            st.session_state.quiz_submitted = False
            st.session_state.quiz_questions = []
            st.session_state.quiz_answers = {}
            st.rerun()

# ------------------------------------------
# TAB 6: PYQ SOLVED BANK
# ------------------------------------------
with tab6:
    st.header("📚 PYQ Solved Questions Bank")
    st.subheader("High Weightage Solved GATE CS PYQs")
    st.markdown("""
    * **Algorithms:** Time complexity of Master Theorem cases.
    * **DBMS:** B+ Tree indexing & Normalization (3NF vs BCNF).
    * **OS:** Virtual Memory & Page Fault calculations.
    """)

# ------------------------------------------
# TAB 7: ERROR VAULT & PERSONAL PLAN
# ------------------------------------------
with tab7:
    st.header("🛡️ Error Vault & Strategy Plan")
    st.text_area("Record your Weak Spots / Frequently Made Mistakes:", "Mistake in Page Replacement FIFO calculations...")
    st.info("💡 AI Tip: Revision after 3 days reduces error rates by 60%.")

# ------------------------------------------
# TAB 8: PSU GUIDANCE & SETTINGS
# ------------------------------------------
with tab8:
    st.header("⚙️ PSU Guidance & System Settings")

    st.subheader("🏢 PSU & Career Opportunities")
    st.markdown("""
    * **Top Hiring PSUs:** ONGC, IOCL, GAIL, POSOCO, DRDO, BARC.
    * **General Cutoff:** AIR < 300 for top PSUs.
    * **Higher Studies:** M.Tech AI/DS at IISc, IIT Bombay, IIT Delhi.
    """)

    st.divider()
    st.subheader("🔑 API Connection Status")
    if api_status["loaded"]:
        st.success(f"**Gemini API:** {api_status['message']}")
    else:
        st.error(f"**Gemini API:** {api_status['message']}")

    st.divider()
    st.subheader("🔄 Progress Reset")
    if st.button("Reset All Progress"):
        st.session_state.unlocked_level = 1
        st.session_state.xp_points = 0
        st.session_state.badges = ["🌱 Beginner Explorer"]
        st.rerun()
