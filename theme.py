"""
theme.py — Central design system for DevLog
==============================================
The Tkinter/CustomTkinter equivalent of a CSS variables file. Every view
imports colors, fonts, spacing and icon maps from here instead of hardcoding
hex values, so the whole app stays visually consistent from one place.
"""

import customtkinter as ctk

# ── Colour tokens ────────────────────────────────────────────────────────────

BG                = "#080B12"
SIDEBAR           = "#0B0F18"
PANEL             = "#101622"
CARD              = "#141B27"
CARD_HOVER        = "#192131"
SURFACE_ELEVATED  = "#1A2231"

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

# ── Radius scale ─────────────────────────────────────────────────────────────

RADIUS_SM = 7    # buttons, inputs
RADIUS_MD = 10   # cards
RADIUS_LG = 12   # large panels, columns
RADIUS_PILL = 999

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


FONT_PAGE_TITLE    = lambda: font(28, "bold")
FONT_PAGE_SUBTITLE = lambda: font(13)
FONT_BREADCRUMB    = lambda: font(11)
FONT_SECTION       = lambda: font(15, "bold")
FONT_TASK_TITLE    = lambda: font(14, "bold")
FONT_BODY          = lambda: font(13)
FONT_META          = lambda: font(11)

# ── Icon glyph system ────────────────────────────────────────────────────────
# One curated set of monochrome Unicode glyphs, sized via `font()`, used
# everywhere instead of ad-hoc colourful emoji. Keeps every icon consistent
# regardless of platform emoji rendering.

ICON_SIZE_NAV     = 15
ICON_SIZE_STD     = 13
ICON_SIZE_LARGE   = 17

ICONS = {
    "overview":     "▥",
    "board":        "▤",
    "analytics":    "◭",
    "projects":     "▣",
    "settings":     "⚙",
    "search":       "⌕",
    "bell":         "◉",
    "add":          "+",
    "edit":         "✎",
    "more":         "⋯",
    "drag":         "⋮⋮",
    "calendar":     "▦",
    "clock":        "◷",
    "chevron":      "›",
    "chevron_down": "⌄",
    "refresh":      "↻",
    "streak":       "◆",
    "target":       "◎",
    "skill":        "◈",
    "external":     "↗",
    "file":         "▤",
    "folder":       "⌸",
    "close":        "✕",
    "check":        "✓",
    "back":         "‹",
}


def icon(name: str) -> str:
    return ICONS.get(name, "")

# ── Status pills ─────────────────────────────────────────────────────────────

STATUS = {
    "Todo":        {"icon": "○", "color": TEXT_MUTED,  "bg": "#1A2130"},
    "In Progress": {"icon": "◷", "color": WARNING,     "bg": "#2A2213"},
    "Done":        {"icon": "✓", "color": SUCCESS,     "bg": "#132A1D"},
    "Blocked":     {"icon": "⊗", "color": DANGER,      "bg": "#2A1517"},
}

STATUS_ORDER = ["Todo", "In Progress", "Done", "Blocked"]


def next_status(current: str) -> str:
    """Return the status that follows ``current`` in the workflow, wrapping to Todo."""
    cycle = ["Todo", "In Progress", "Done"]
    if current not in cycle:
        return "Todo"
    return cycle[(cycle.index(current) + 1) % len(cycle)]

# ── Category colours ─────────────────────────────────────────────────────────
# Category colour is expressed purely as a small dot next to the label
# (see views/components/ui.py CategoryDot) rather than a decorative emoji —
# the colour alone is the identifier.

CATEGORY_COLOURS = {
    "Lab": "#00D4FF", "Study": "#43E97B", "Project": PRIMARY,
    "CTF": "#FC5C7D", "Reading": "#F7B731", "Revision": "#FF9500",
}

# ── Skill → icon mapping ─────────────────────────────────────────────────────
# Every skill maps to the same neutral glyph — the skill *name* carries the
# information; the glyph is just a small visual anchor, not per-skill iconography.


def skill_icon(skill: str) -> str:
    return ICONS["skill"]
