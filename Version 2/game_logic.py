"""Deterministic game rules for AI Escape Room Version 2.

The LLM is deliberately excluded from all state-changing decisions.
Only this module can award items, solve puzzles, or unlock the exit.
"""

import re

OBJECTS = {
    "painting": ("painting", "picture", "portrait", "frame"),
    "key_table": ("key table", "table", "keys", "key rack"),
    "bookshelf": ("bookshelf", "bookcase", "books", "shelf"),
    "drawer": ("drawer", "locked drawer", "desk drawer"),
    "clock": ("clock", "watch", "pocket watch"),
    "door": ("door", "exit", "exit door"),
}

def initial_state(player_name: str = "") -> dict:
    return {
        "player_name": player_name,
        "score": 0,
        "hints_used": 0,
        "inventory": [],
        "examined": [],
        "puzzles": {"coloured_key": False, "hidden_cipher": False, "alchemist_clock": False},
        "drawer_open": False,
        "escaped": False,
        "game_over": False,
        "history": [],
    }


def get_status(state: dict) -> dict:
    return {
        "score": state["score"],
        "inventory": list(state["inventory"]),
        "puzzles_solved": sum(state["puzzles"].values()),
        "escaped": state["escaped"],
    }


def get_visible_room_description(state: dict) -> str:
    examined = set(state["examined"])
    lines = [
        "You are in Dr. Thaddeus Vane's abandoned study.",
        "A painting hangs above a small table. A bookshelf stands beside a desk.",
        "The desk has a locked drawer. An old clock rests near the exit door.",
        "The exit door is secured by the mystery of the Chronos Gem.",
    ]
    if "painting" in examined:
        lines.append("The painting shows three cats. A riddle mentions the sky, the sun, and a rose.")
    if "key_table" in examined:
        lines.append("Four coloured keys are visible: red, blue, gold, and silver.")
    if "bookshelf" in examined:
        lines.append("An old paper on the bookshelf shows: 3 - 1 - 20, with A=1 through Z=26.")
    if state["drawer_open"]:
        lines.append("The drawer is open. Inside is a note with a riddle about something with hands and a face.")
    if "clock" in examined:
        lines.append("The clock's second hand appears to be moving backwards.")
    return "\n".join(lines)


def _contains_any(text: str, words: tuple) -> bool:
    return any(word in text for word in words)


def _record(state: dict, action: str, result: str) -> str:
    state["history"].append({"action": action, "result": result})
    return result


def process_action(state: dict, user_text: str) -> str:
    """Parse a natural-language action and apply only validated state changes."""
    raw = user_text.strip()
    text = re.sub(r"\s+", " ", raw.lower())

    if not raw:
        return "Type an action or question so I can help with your investigation."
    if state["escaped"]:
        return "You have already escaped. Choose Restart game if you want another attempt."

    if text in {"help", "commands", "what can i do"} or "what should i do" in text:
        return _record(state, raw,
            "You can examine the painting, key table, bookshelf, drawer, clock, or door. "
            "You can also submit a puzzle answer in ordinary language.")

    # Hint requests never reveal a solution directly.
    if "hint" in text:
        state["hints_used"] += 1
        if not state["puzzles"]["coloured_key"]:
            hint = "Look at the words in the painting riddle. One of the colours is strongly associated with the sky."
        elif not state["puzzles"]["hidden_cipher"]:
            hint = "The numbers use the alphabet mapping shown on the paper. Convert each number into a letter."
        elif not state["puzzles"]["alchemist_clock"]:
            hint = "The note describes an object with hands and a face. Search the room for it."
        else:
            hint = "Check your inventory and the exit door."
        return _record(state, raw, "💡 Hint: " + hint)

    # Object inspection
    inspect_words = ("examine", "inspect", "look at", "search", "investigate", "describe", "check")
    is_inspection = _contains_any(text, inspect_words)
    if is_inspection:
        if _contains_any(text, OBJECTS["painting"]):
            state["examined"].append("painting") if "painting" not in state["examined"] else None
            return _record(state, raw,
                "The painting shows three cats. The carved riddle says: the cat in the hat hates the sky; "
                "the eye-patch cat loves the sun; the sleepy cat wants a rose.")
        if _contains_any(text, OBJECTS["key_table"]):
            state["examined"].append("key_table") if "key_table" not in state["examined"] else None
            return _record(state, raw, "Four keys sit on the table: red, blue, gold, and silver.")
        if _contains_any(text, OBJECTS["bookshelf"]):
            state["examined"].append("bookshelf") if "bookshelf" not in state["examined"] else None
            return _record(state, raw,
                "You find a slip of paper: 3 - 1 - 20. Beneath it is the alphabet code A=1, B=2 ... Z=26.")
        if _contains_any(text, OBJECTS["drawer"]):
            state["examined"].append("drawer") if "drawer" not in state["examined"] else None
            if state["drawer_open"]:
                return _record(state, raw, "The drawer is open and empty except for the alchemist's note.")
            return _record(state, raw, "The drawer is locked. It appears to need the blue key and the word from the cipher.")
        if _contains_any(text, OBJECTS["clock"]):
            state["examined"].append("clock") if "clock" not in state["examined"] else None
            return _record(state, raw, "The brass clock has hands and a face. Its second hand is ticking backwards.")
        if _contains_any(text, OBJECTS["door"]):
            state["examined"].append("door") if "door" not in state["examined"] else None
            if state["escaped"]:
                return _record(state, raw, "The exit is open. You are free.")
            return _record(state, raw, "The exit door is sealed. The Chronos Gem is needed to release its lock.")
        return _record(state, raw, "I cannot identify that object. Try the painting, key table, bookshelf, drawer, clock, or door.")

    # Opening the drawer is a validated action, not an LLM decision.
    if "open" in text and _contains_any(text, OBJECTS["drawer"]):
        if state["drawer_open"]:
            return _record(state, raw, "The drawer is already open.")
        if not state["puzzles"]["coloured_key"] or "blue_key" not in state["inventory"]:
            return _record(state, raw, "The drawer stays locked. You have not earned or collected the correct key.")
        if not state["puzzles"]["hidden_cipher"]:
            return _record(state, raw, "The drawer's combination is still unknown. Solve the bookshelf cipher first.")
        state["drawer_open"] = True
        state["score"] += 15
        return _record(state, raw,
            "🔓 The blue key turns, and the cipher word releases the drawer. Inside is a note: "
            "'I have hands but cannot clap. I have a face but cannot smile. I move forward but never walk. What am I?'")

    # Puzzle 1: Blue key. Must inspect the painting and key table first.
    if "use" not in text and any(word in text for word in ("blue", "red", "gold", "silver")) and not state["puzzles"]["coloured_key"]:
        if "painting" not in state["examined"] or "key_table" not in state["examined"]:
            return _record(state, raw, "First examine the painting and the key table. You need both clues before choosing.")
        if "blue" in text:
            state["puzzles"]["coloured_key"] = True
            state["inventory"].append("blue_key")
            state["score"] += 10
            return _record(state, raw, "✅ Correct. The sky points to the blue key. You collect the blue key.")
        return _record(state, raw, "That colour does not fit the riddle. Reconsider the clue about the sky.")

    # Puzzle 2: A1Z26 cipher gives CAT. Must inspect bookshelf.
    if any(word in text for word in ("cat", "3-1-20", "3 1 20", "three one twenty")) and not state["puzzles"]["hidden_cipher"]:
        if "bookshelf" not in state["examined"]:
            return _record(state, raw, "Find and inspect the bookshelf paper before submitting the cipher answer.")
        if "cat" in text or "3-1-20" in text or "3 1 20" in text or "three one twenty" in text:
            state["puzzles"]["hidden_cipher"] = True
            state["score"] += 20
            return _record(state, raw, "✅ Correct. 3=C, 1=A, and 20=T. The hidden word is CAT. Remember it for the locked drawer.")

    # Puzzle 3: Clock riddle. Drawer must be opened and clock inspected.
    if any(word in text for word in ("clock", "timepiece", "watch")) and not state["puzzles"]["alchemist_clock"]:
        if not state["drawer_open"]:
            return _record(state, raw, "The final riddle is hidden in the locked drawer. Open it first.")
        if "clock" not in state["examined"]:
            return _record(state, raw, "Inspect the old clock before answering the note.")
        state["puzzles"]["alchemist_clock"] = True
        state["inventory"].append("chronos_gem")
        state["score"] += 25
        return _record(state, raw, "✅ Correct. It is a clock! Behind its face you discover the Chronos Gem.")

    # Final exit action
    if any(word in text for word in ("unlock", "open", "escape", "leave")) and _contains_any(text, OBJECTS["door"]):
        if all(state["puzzles"].values()) and "chronos_gem" in state["inventory"]:
            state["escaped"] = True
            state["score"] += 25
            return _record(state, raw, "🏆 The Chronos Gem glows. The exit unlocks, and you escape Dr. Vane's study!")
        return _record(state, raw, "The exit remains sealed. You must solve all three puzzles and recover the Chronos Gem.")

    # Catch attempted item use / impossible actions.
    if "use" in text and "key" in text:
        if "blue_key" not in state["inventory"]:
            return _record(state, raw, "You cannot use a key you have not collected.")
        return _record(state, raw, "The blue key belongs to the locked drawer. Try opening the drawer after solving the cipher.")

    return _record(state, raw,
        "The room offers no response to that action yet. Try examining an object, asking for a hint, "
        "or submitting the answer to a clue. Type **help** for ideas.")
