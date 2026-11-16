from pathlib import Path
import os
import streamlit as st
from dotenv import load_dotenv

from game_logic import (
    initial_state, process_action, get_status, get_visible_room_description
)

# Loads the project's root .env when this app is run from the repository root.
load_dotenv(Path(__file__).resolve().parent.parent / ".env")
load_dotenv()

st.set_page_config(page_title="AI Escape Room | Version 2", page_icon="🔐", layout="wide")

try:
    from google import genai
except ImportError:
    genai = None

MODEL = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")


@st.cache_resource
def get_gemini_client():
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key or genai is None:
        return None
    return genai.Client(api_key=api_key)


def gemini_game_master(player_message: str, event_message: str, state: dict) -> str:
    """Gemini may narrate, but it never changes or decides game state."""
    client = get_gemini_client()
    if client is None:
        return event_message

    visible_context = get_visible_room_description(state)
    prompt = f"""
You are the atmospheric narrator for a mystery escape-room game.
The player is {state['player_name']}.
Visible room information:
{visible_context}

The player's latest action was:
{player_message}

The Python game engine has already validated the action and produced this result:
{event_message}

Rewrite the result as a concise, immersive response (2-4 sentences).
Important rules:
- Do not invent objects, clues, inventory items, puzzle outcomes, or state changes.
- Do not reveal future puzzle answers or hidden solutions.
- Do not contradict the Python result.
- If the action failed, explain the failure without granting progress.
- Never claim the player escaped unless the Python result explicitly says they escaped.
"""
    try:
        response = client.models.generate_content(model=MODEL, contents=prompt)
        return response.text.strip() if response and response.text else event_message
    except Exception:
        return event_message


if "game" not in st.session_state:
    st.session_state.game = initial_state()
if "messages" not in st.session_state:
    st.session_state.messages = []

state = st.session_state.game

with st.sidebar:
    st.title("🎮 Player Dashboard")
    st.write(f"**Player:** {state['player_name'] or 'Investigator'}")
    st.metric("⭐ Score", state["score"])
    st.metric("🧩 Puzzles solved", f"{sum(state['puzzles'].values())}/3")
    st.metric("💡 Hints used", state["hints_used"])
    st.subheader("🎒 Inventory")
    if state["inventory"]:
        for item in state["inventory"]:
            st.write(f"• {item.replace('_', ' ').title()}")
    else:
        st.caption("Your inventory is empty.")
    st.divider()
    if st.button("🔄 Restart game", use_container_width=True):
        player_name = state["player_name"]
        st.session_state.game = initial_state(player_name)
        st.session_state.messages = []
        st.rerun()

st.title("🔐 AI Escape Room")
st.caption("Version 2 · Gemini narrates, Python controls the rules")
st.info(
    "Your objective: investigate the study, solve three puzzles, recover the Chronos Gem, "
    "and unlock the exit. Try natural-language actions such as **'examine the painting'**, "
    "**'inspect the bookshelf'**, or **'I think the answer is blue'**."
)

if not state["player_name"]:
    name = st.text_input("Enter your investigator name", max_chars=40)
    if st.button("Enter the study"):
        if name.strip():
            state["player_name"] = name.strip()
            st.session_state.messages.append({
                "role": "assistant",
                "content": f"Welcome, {name.strip()}. The study door has locked behind you. "
                           "Look around and tell me what you want to investigate."
            })
            st.rerun()
        else:
            st.warning("Please enter your name to begin.")
    st.stop()

left, right = st.columns([2, 1])
with left:
    st.subheader("📜 The Mystery: The Vanishing Alchemist")
    st.write(get_visible_room_description(state))
with right:
    st.subheader("🗺️ Investigation guide")
    st.write("**Objects you can investigate:**")
    for obj in ["painting", "key table", "bookshelf", "locked drawer", "clock", "exit door"]:
        st.write(f"• {obj.title()}")
    st.caption("The game engine checks every action before progress is awarded.")

st.divider()
st.subheader("💬 Talk to the Game Master")

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

user_input = st.chat_input("What would you like to do?")
if user_input:
    st.session_state.messages.append({"role": "user", "content": user_input})
    event = process_action(state, user_input)
    reply = gemini_game_master(user_input, event, state)
    st.session_state.messages.append({"role": "assistant", "content": reply})
    st.rerun()

if state["escaped"]:
    st.success(f"🏆 You escaped, {state['player_name']}! Final score: {state['score']}")
    st.balloons()
elif state["game_over"]:
    st.error("The investigation has ended. Restart the game to try again.")
