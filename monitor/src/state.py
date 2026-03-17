import json
from pathlib import Path

from platformdirs import user_state_dir

STATE_DIR = Path(user_state_dir("aab-monitor"))


def load_state() -> dict:
    STATE_DIR.mkdir(parents=True, exist_ok=True)
    try:
        return json.loads((STATE_DIR / "state.json").read_text())
    except FileNotFoundError:
        return {}


def save_state(state: dict):
    (STATE_DIR / "state.json").write_text(json.dumps(state, indent=2))
