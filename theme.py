"""
theme.py — Central design system for DevLog
==============================================
The Tkinter/CustomTkinter equivalent of a CSS variables file. Every view
imports colors, fonts, spacing and icon maps from here instead of hardcoding
hex values, so the whole app stays visually consistent from one place.
"""

import customtkinter as ctk

# ── Colour tokens ────────────────────────────────────────────────────────────

BG              = "#080B12"
SIDEBAR         = "#0B0F18"
PANEL           = "#101622"
CARD            = "#141B27"
CARD_HOVER      = "#192131"

BORDER          = "#222B3B"

TEXT            = "#F4F5F7"
TEXT_SECONDARY  = "#929AAA"
TEXT_MUTED      = "#626A7A"

PRIMARY         = "#7C4DFF"
PRIMARY_HOVER   = "#8B5CF6"
PRIMARY_PRESSED = "#6633E6"

SUCCESS         = "#22C55E"
WARNING         = "#F59E0B"
DANGER          = "#EF4444"
INFO            = "#3B82F6"

# ── Spacing scale ────────────────────────────────────────────────────────────

SPACE_XS  = 4
SPACE_SM  = 8
SPACE_MD  = 12
SPACE_LG  = 16
SPACE_XL  = 20
SPACE_2XL = 24
SPACE_3XL = 32

# ── Typography ───────────────────────────────────────────────────────────────

FONT_FAMILY = "Segoe UI"


def font(size: int, weight: str = "normal") -> ctk.CTkFont:
    return ctk.CTkFont(family=FONT_FAMILY, size=size, weight=weight)


FONT_PAGE_TITLE = lambda: font(28, "bold")
FONT_SECTION    = lambda: font(15, "bold")
FONT_TASK_TITLE = lambda: font(14, "bold")
FONT_BODY       = lambda: font(13)
FONT_META       = lambda: font(11)

# ── Status pills ─────────────────────────────────────────────────────────────

STATUS = {
    "Todo":        {"icon": "○", "color": TEXT_MUTED,  "bg": "#1A2130"},
    "In Progress": {"icon": "◷", "color": WARNING,     "bg": "#2A2213"},
    "Done":        {"icon": "✓", "color": SUCCESS,     "bg": "#132A1D"},
    "Blocked":     {"icon": "⊗", "color": DANGER,      "bg": "#2A1517"},
}

# ── Category colours + icons ─────────────────────────────────────────────────

CATEGORY_COLOURS = {
    "Lab": "#00D4FF", "Study": "#43E97B", "Project": PRIMARY,
    "CTF": "#FC5C7D", "Reading": "#F7B731", "Revision": "#FF9500",
}

CATEGORY_ICONS = {
    "Lab": "🧪", "Study": "📖", "Project": "▣",
    "CTF": "🚩", "Reading": "📚", "Revision": "↺",
}

# ── Skill → task-type icon mapping ───────────────────────────────────────────

_SKILL_ICON_GROUPS = {
    "</>": {"Python", "JavaScript", "HTML", "CSS"},
    "🗄":   {"SQL"},
    "☁":   {"Docker", "Networking"},
    "🧪":   {"Web Security", "Cryptography", "Reverse Engineering"},
    "🔧":  {"Git"},
    "🖥":  {"CustomTkinter", "Linux"},
}

_SKILL_TO_ICON = {
    skill: icon for icon, skills in _SKILL_ICON_GROUPS.items() for skill in skills
}


def skill_icon(skill: str) -> str:
    return _SKILL_TO_ICON.get(skill, "▣")
