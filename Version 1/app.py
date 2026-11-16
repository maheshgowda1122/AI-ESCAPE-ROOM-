
import os
import time
import streamlit as st
from dotenv import load_dotenv
from google import genai

# ==========================================
# CONFIGURATION
# ==========================================

load_dotenv("/Users/mahesh/Desktop/AI_Escape_Room/.env")

st.set_page_config(
    page_title="AI Escape Room",
    page_icon="🔐",
    layout="wide"
)

API_KEY = os.getenv("GEMINI_API_KEY")
MODEL = "models/gemini-3.5-flash"

# ==========================================
# GEMINI AI CONNECTION
# ==========================================

@st.cache_resource
def get_gemini_client():
    if not API_KEY:
        return None
    return genai.Client(api_key=API_KEY)


def ask_gemini(prompt):
    client = get_gemini_client()

    if client is None:
        return "Gemini API key not found. Please check your .env file."

    try:
        response = client.models.generate_content(
            model=MODEL,
            contents=prompt
        )
        return response.text
    except Exception as e:
        return f"Gemini connection error: {str(e)}"


# ==========================================
# GAME LEVELS
# ==========================================

LEVELS = [
    {
        "title": "The Four Coloured Keys",
        "description": """
You are standing inside Dr. Vane's mysterious study.

There are four keys on the table:

🔴 Red   🔵 Blue   🟡 Gold   ⚪ Silver

A riddle is written under a painting:

"The cat in the hat hates the sky.
The cat with the eye-patch loves the sun.
The sleepy cat wants a rose.

Which key opens the door?"

Think carefully. Which colour matches the sky?
""",
        "answer": "blue",
        "reward": 10,
        "hint": "Think about the colour of the sky. Which key has that colour?",
        "success": """
The blue key fits perfectly!

CLICK!

The heavy wooden door slowly opens.
You have discovered the first secret of Dr. Vane's study.
"""
    },
    {
        "title": "The Hidden Cipher",
        "description": """
You enter a dusty library.

On an ancient piece of paper, you discover:

3 - 1 - 20

Below it, another message appears:

A = 1
B = 2
C = 3
...
Z = 26

Dr. Vane left a secret word.

What word do these numbers spell?
""",
        "answer": "cat",
        "reward": 20,
        "hint": "Convert each number into its corresponding alphabet letter.",
        "success": """
You solved the cipher!

The bookshelf moves aside, revealing a hidden passage.
A strange mechanical sound comes from the next room.
"""
    },
    {
        "title": "The Alchemist's Clock",
        "description": """
You finally reach the room containing the mysterious clock.

A note reads:

'I have hands but cannot clap.
I have a face but cannot smile.
I move forward but never walk.

What am I?'

Enter the answer to unlock the Chronos Gem.
""",
        "answer": "clock",
        "reward": 30,
        "hint": "Look at the mysterious object Dr. Vane has been obsessed with.",
        "success": """
CORRECT!

The clock stops moving backwards.

The Chronos Gem begins to glow.
You have successfully recovered Dr. Vane's greatest creation!
"""
    }
]


# ==========================================
# SESSION STATE
# ==========================================

defaults = {
    "started": False,
    "player": "",
    "level": 0,
    "score": 0,
    "hints_used": 0,
    "start_time": None,
    "completed": False,
    "history": []
}

for key, value in defaults.items():
    if key not in st.session_state:
        st.session_state[key] = value


# ==========================================
# CUSTOM CSS
# ==========================================

st.markdown("""
<style>

.stApp {
    background-color: #171615;
    color: #f5f5f5;
}

h1, h2, h3 {
    color: #f5f5f5 !important;
}

p, label {
    color: #eeeeee;
}

div.stButton > button {
    background-color: #292624;
    color: white;
    border: 1px solid #55504b;
    border-radius: 9px;
    padding: 10px 22px;
}

div.stButton > button:hover {
    background-color: #41403d;
    border-color: #d9a441;
    color: white;
}

.success-box {
    background: #183b2a;
    padding: 20px;
    border-radius: 10px;
    border-left: 5px solid #35b879;
    margin: 15px 0;
}

.story-box {
    background: #242220;
    padding: 22px;
    border-radius: 12px;
    border: 1px solid #48423c;
    line-height: 1.8;
}

.info-box {
    background: #202c40;
    padding: 15px;
    border-radius: 9px;
    color: #83baff;
}

</style>
""", unsafe_allow_html=True)


# ==========================================
# HEADER
# ==========================================

st.title("🔐 AI Escape Room")
st.caption("An interactive mystery powered by Google Gemini AI")

st.divider()


# ==========================================
# WELCOME SCREEN
# ==========================================

if not st.session_state.started:

    st.header("Welcome, Player!")

    st.write(
        "Enter the escape room, solve puzzles and use "
        "your intelligence to escape!"
    )

    name = st.text_input("Enter your name")

    if st.button("🚪 Start Escape Game"):

        if name.strip():

            st.session_state.player = name.strip()
            st.session_state.started = True
            st.session_state.start_time = time.time()

            st.rerun()

        else:
            st.warning("Please enter your name first.")

    st.stop()


# ==========================================
# TIMER
# ==========================================

elapsed = time.time() - st.session_state.start_time

remaining = max(0, 3600 - int(elapsed))

minutes = remaining // 60
seconds = remaining % 60

if remaining == 0 and not st.session_state.completed:

    st.error("⏰ TIME'S UP! The escape room is locked.")

    if st.button("Restart Game"):

        for key in defaults:
            st.session_state[key] = defaults[key]

        st.rerun()

    st.stop()


# ==========================================
# SIDEBAR
# ==========================================

with st.sidebar:

    st.header("🎮 Player Dashboard")

    st.write(f"**Player:** {st.session_state.player}")

    st.metric(
        "⏳ Time Remaining",
        f"{minutes:02d}:{seconds:02d}"
    )

    st.metric("⭐ Total Score", st.session_state.score)

    st.metric(
        "🧩 Current Level",
        f"{min(st.session_state.level + 1, 3)}/3"
    )

    st.metric("💡 Hints Used", st.session_state.hints_used)

    st.progress(
        min(st.session_state.level / 3, 1.0)
        if not st.session_state.completed else 1.0
    )

    st.divider()

    if st.button("🔄 Restart Game"):

        for key in defaults:
            st.session_state[key] = defaults[key]

        st.rerun()


# ==========================================
# GAME COMPLETION
# ==========================================

if st.session_state.completed:

    st.balloons()

    st.title("🏆 YOU ESCAPED!")

    st.success(
        f"Congratulations, {st.session_state.player}!"
    )

    st.header("You recovered the Chronos Gem!")

    st.write(
        "You successfully solved all three puzzles "
        "and escaped Dr. Vane's mysterious study."
    )

    col1, col2, col3 = st.columns(3)

    col1.metric("Final Score", st.session_state.score)
    col2.metric("Hints Used", st.session_state.hints_used)
    col3.metric("Levels Completed", "3/3")

    st.subheader("📜 Your Adventure")

    for item in st.session_state.history:
        st.write("✅", item)

    if st.button("Play Again"):

        for key in defaults:
            st.session_state[key] = defaults[key]

        st.rerun()

    st.stop()


# ==========================================
# CURRENT LEVEL
# ==========================================

level_index = st.session_state.level
current = LEVELS[level_index]

st.header(
    f"🧩 LEVEL {level_index + 1}: {current['title']}"
)

st.write(
    f"You are playing as **{st.session_state.player}**."
)

st.markdown(
    f'<div class="story-box">{current["description"].replace(chr(10), "<br>")}</div>',
    unsafe_allow_html=True
)

st.markdown(
    f'<div class="info-box">⭐ Correct answer reward: '
    f'{current["reward"]} points</div>',
    unsafe_allow_html=True
)

st.divider()


# ==========================================
# ANSWER VALIDATION
# ==========================================

answer = st.text_input(
    "✍️ Enter your answer:",
    key=f"answer_{level_index}",
    placeholder="Type your answer here..."
)

if st.button("🔓 SUBMIT ANSWER", use_container_width=True):

    if not answer.strip():

        st.warning("Enter an answer before submitting.")

    elif answer.strip().lower() == current["answer"]:

        st.session_state.score += current["reward"]

        st.session_state.history.append(
            f"Level {level_index + 1}: {current['title']} - Solved"
        )

        st.session_state.level += 1

        if st.session_state.level == len(LEVELS):
            st.session_state.completed = True

        st.session_state.success_message = current["success"]

        st.rerun()

    else:

        st.error("❌ Incorrect answer! Look carefully at the clues.")


# ==========================================
# GEMINI AI HINT SYSTEM
# ==========================================

st.divider()

st.subheader("🤖 Ask the AI Game Master")

st.write(
    "Need a little help? Gemini can give you a hint "
    "without revealing the answer."
)

if st.button("💡 Get AI Hint"):

    st.session_state.hints_used += 1

    prompt = f"""
    You are the AI Game Master of a mysterious escape room.

    Current puzzle:
    {current['description']}

    Official answer:
    {current['answer']}

    The player needs help.

    Give one short, useful hint.
    Never reveal the exact answer.
    Keep the atmosphere mysterious and entertaining.
    """

    with st.spinner("The Game Master is thinking..."):

        hint = ask_gemini(prompt)

    st.info(f"🧙 Game Master: {hint}")


# ==========================================
# AI GAME MASTER CHAT
# ==========================================

st.divider()

st.subheader("💬 Talk to the Game Master")

question = st.text_input(
    "Ask a question about the current mystery:",
    key=f"chat_{level_index}"
)

if st.button("Send to Game Master"):

    if question.strip():

        prompt = f"""
        You are Dr. Vane's mysterious AI Game Master.

        The player's name is {st.session_state.player}.

        Current puzzle:
        {current['description']}

        The correct answer is {current['answer']}.

        Player question:
        {question}

        Answer in a mysterious, friendly style.
        Do not directly reveal the answer.
        """

        with st.spinner("The Game Master is replying..."):

            reply = ask_gemini(prompt)

        st.write("🧙 **Game Master:**")
        st.write(reply)

    else:

        st.warning("Type a question first.")


# ==========================================
# FOOTER
# ==========================================

st.divider()

st.caption(
    "🔐 AI Escape Room | Powered by Python, Streamlit "
    "and Google Gemini"
)
