"""
settings_store.py — JSON persistence for local app preferences
================================================================
Same read-fresh-from-disk pattern as storage.py, but for the small set of
user preferences the Settings page exposes: display name/role, weekly streak
goal, and default board view. Kept separate from tasks.json because it is
conceptually different data (app config, not task records).
"""

import json
import os

DATA_FILE = os.path.join(os.path.dirname(__file__), "settings.json")

DEFAULTS = {
    "display_name": "Tristan Joubert",
    "role": "Student",
    "weekly_streak_goal": 7,
    "default_board_view": "list",
}


def load_settings() -> dict:
    """Return saved settings merged over defaults; never raises."""
    settings = dict(DEFAULTS)
    if not os.path.exists(DATA_FILE):
        return settings
    try:
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            saved = json.load(f)
        if isinstance(saved, dict):
            settings.update({k: v for k, v in saved.items() if k in DEFAULTS})
    except (json.JSONDecodeError, OSError):
        pass
    return settings


def save_settings(settings: dict) -> None:
    """Persist a settings dict (only known keys are written)."""
    clean = {k: settings.get(k, DEFAULTS[k]) for k in DEFAULTS}
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(clean, f, indent=2, ensure_ascii=False)
