# AI Escape Room — Version 2

Version 2 adds deterministic game-state management and action validation.

## Features
- Streamlit chat interface with natural-language actions.
- Gemini acts only as the narrator/Game Master.
- Python validates puzzle answers and all state-changing actions.
- Structured state: examined objects, inventory, solved puzzles, drawer status, score and escape status.
- Invalid actions do not award points or change puzzle state.
- Restart support.
- Five automated tests in `test_game_logic.py`.

## Requirements
- Python 3.10+
- A Gemini API key from Google AI Studio (optional; without it, built-in narration is used).

## Setup

Run these commands from the repository root:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r "Version 2/requirements.txt"
```

Create or edit the `.env` file in the repository root:

```env
GEMINI_API_KEY=put_your_own_key_here
GEMINI_MODEL=gemini-2.5-flash
```

Never commit `.env` or paste your API key into Python files, notebooks, screenshots or GitHub.

## Run

From the repository root:

```bash
streamlit run "Version 2/app.py"
```

## How to play
1. Enter your investigator name.
2. Examine the painting and key table. Solve the colour riddle with **blue**.
3. Examine the bookshelf. Decode `3-1-20` using A=1, B=2 ... Z=26. The answer is **CAT**.
4. Open the drawer after solving both earlier puzzles.
5. Examine the clock and solve the note's riddle with **clock**.
6. Unlock the exit door.

Example natural-language actions:
- `Examine the painting`
- `Inspect the key table`
- `I think the answer is blue`
- `Look at the bookshelf`
- `The cipher spells CAT`
- `Open the drawer`
- `Inspect the clock`
- `The answer is a clock`
- `Unlock the exit door`

## Architecture
Player message → Streamlit UI → Python action parser → deterministic validation → structured game state.
If Gemini is configured, it receives the validated result and narrates it. Gemini cannot award items, solve puzzles, or unlock the door.

## Tests

From the repository root:

```bash
python -m unittest discover -s "Version 2" -p "test_*.py" -v
```
