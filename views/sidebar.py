"""
views/sidebar.py — Primary navigation
=======================================
WORKSPACE (Overview / Board / Analytics), PROJECTS (the six fixed task
categories), a Settings link, a small streak-consistency card, and a user
footer. Only the selected item ever receives the accent background — every
other row stays neutral.
"""

from typing import Callable
import customtkinter as ctk
import theme
from models import CATEGORIES
from views.components import ui

SIDEBAR_WIDTH = 232

NAV_ITEMS = [
    ("Overview",  "overview",  "overview"),
    ("Board",     "board",     "board"),
    ("Analytics", "analytics", "analytics"),
]


class Sidebar(ctk.CTkFrame):

    def __init__(
        self,
        parent,
        on_nav: Callable[[str], None],
        on_category: Callable[[str], None],
        on_settings: Callable[[], None],
    ):
        super().__init__(parent, width=SIDEBAR_WIDTH, fg_color=theme.SIDEBAR, corner_radius=0)
        self.pack_propagate(False)

        self._on_nav      = on_nav
        self._on_category  = on_category
        self._on_settings  = on_settings

        self._nav_buttons: dict[str, ctk.CTkButton] = {}
        self._category_buttons: dict[str, ctk.CTkButton] = {}

        self._build_brand()
        self._build_nav()
        self._build_categories()
        self._build_streak_card()
        self._build_settings_link()
        self._build_user_footer()

    # ── Brand ─────────────────────────────────────────────────────────────────

    def _build_brand(self):
        ctk.CTkLabel(
            self, text="DevLog",
            font=theme.font(17, "bold"), text_color=theme.TEXT,
        ).pack(anchor="w", padx=theme.SPACE_XL, pady=(theme.SPACE_XL, theme.SPACE_LG))
        ui.Divider(self, padx=0)

    # ── Workspace nav ────────────────────────────────────────────────────────

    def _build_nav(self):
        ui.SectionLabel(
            self, "Workspace",
        ).pack(anchor="w", padx=theme.SPACE_XL, pady=(theme.SPACE_LG, theme.SPACE_SM))

        for label, key, icon_key in NAV_ITEMS:
            btn = self._nav_row(f"{theme.icon(icon_key)}   {label}", lambda k=key: self._on_nav(k))
            self._nav_buttons[key] = btn

    def _build_categories(self):
        ui.SectionLabel(
            self, "Projects",
        ).pack(anchor="w", padx=theme.SPACE_XL, pady=(theme.SPACE_XL, theme.SPACE_SM))

        all_btn = self._nav_row(f"{theme.icon('projects')}   All Projects", lambda: self._on_nav("projects"))
        self._nav_buttons["projects"] = all_btn

        for category in CATEGORIES:
            colour = theme.CATEGORY_COLOURS.get(category, theme.TEXT_MUTED)
            btn = self._nav_row(f"●   {category}", lambda c=category: self._on_category(c), text_color=colour)
            self._category_buttons[category] = btn

    def _nav_row(self, text, command, text_color=None):
        btn = ctk.CTkButton(
            self, text=text, anchor="w",
            height=34, corner_radius=theme.RADIUS_SM,
            fg_color="transparent", hover_color=theme.PANEL,
            text_color=text_color or theme.TEXT_SECONDARY,
            font=theme.FONT_BODY(),
            command=command,
        )
        btn.pack(fill="x", padx=theme.SPACE_MD, pady=1)
        return btn

    # ── Streak card ──────────────────────────────────────────────────────────

    def _build_streak_card(self):
        card = ui.Card(self)
        card.pack(side="top", fill="x", padx=theme.SPACE_LG, pady=(theme.SPACE_2XL, 0))

        ctk.CTkLabel(
            card, text=f"{theme.icon('streak')}  Stay Consistent",
            font=theme.font(12, "bold"), text_color=theme.TEXT,
        ).pack(anchor="w", padx=theme.SPACE_MD, pady=(theme.SPACE_MD, theme.SPACE_XS))

        ctk.CTkLabel(
            card, text="Small daily progress leads to big results.",
            font=theme.FONT_META(), text_color=theme.TEXT_MUTED,
            wraplength=SIDEBAR_WIDTH - 2 * theme.SPACE_LG - 2 * theme.SPACE_MD,
            justify="left",
        ).pack(anchor="w", padx=theme.SPACE_MD)

        self._streak_days_label = ctk.CTkLabel(
            card, text="— / 7 days",
            font=theme.FONT_META(), text_color=theme.TEXT_SECONDARY,
        )
        self._streak_days_label.pack(anchor="w", padx=theme.SPACE_MD, pady=(theme.SPACE_SM, theme.SPACE_XS))

        self._streak_progress = ui.ProgressBar(card)
        self._streak_progress.pack(fill="x", padx=theme.SPACE_MD, pady=(0, theme.SPACE_MD))

    def set_streak(self, days: int, goal: int):
        self._streak_days_label.configure(text=f"{days} / {goal} days")
        self._streak_progress.set(min(days / goal, 1.0) if goal else 0)

    # ── Settings link ────────────────────────────────────────────────────────

    def _build_settings_link(self):
        wrap = ctk.CTkFrame(self, fg_color="transparent")
        wrap.pack(side="bottom", fill="x", pady=(theme.SPACE_SM, 0))
        ui.Divider(wrap, padx=theme.SPACE_LG, pady=(0, theme.SPACE_SM))
        btn = self._nav_row_in(wrap, f"{theme.icon('settings')}   Settings", self._on_settings)
        self._nav_buttons["settings"] = btn

    def _nav_row_in(self, parent, text, command):
        btn = ctk.CTkButton(
            parent, text=text, anchor="w",
            height=34, corner_radius=theme.RADIUS_SM,
            fg_color="transparent", hover_color=theme.PANEL,
            text_color=theme.TEXT_SECONDARY,
            font=theme.FONT_BODY(),
            command=command,
        )
        btn.pack(fill="x", padx=theme.SPACE_MD, pady=1)
        return btn

    # ── User footer ──────────────────────────────────────────────────────────

    def _build_user_footer(self):
        wrap = ctk.CTkFrame(self, fg_color="transparent")
        wrap.pack(side="bottom", fill="x", padx=theme.SPACE_LG, pady=theme.SPACE_LG)

        row = ctk.CTkFrame(wrap, fg_color="transparent")
        row.pack(fill="x")

        self._avatar = ctk.CTkLabel(
            row, text="TJ",
            width=32, height=32, corner_radius=16,
            fg_color=theme.PRIMARY, text_color="#FFFFFF",
            font=theme.font(12, "bold"),
        )
        self._avatar.pack(side="left")

        col = ctk.CTkFrame(row, fg_color="transparent")
        col.pack(side="left", padx=(theme.SPACE_SM, 0))

        self._name_label = ctk.CTkLabel(
            col, text="Tristan Joubert",
            font=theme.font(12, "bold"), text_color=theme.TEXT, anchor="w",
        )
        self._name_label.pack(anchor="w")

        self._role_label = ctk.CTkLabel(
            col, text="Student",
            font=theme.FONT_META(), text_color=theme.TEXT_MUTED, anchor="w",
        )
        self._role_label.pack(anchor="w")

    def set_user(self, display_name: str, role: str):
        self._name_label.configure(text=display_name)
        self._role_label.configure(text=role)
        initials = "".join(part[0] for part in display_name.split()[:2]).upper() or "?"
        self._avatar.configure(text=initials)

    # ── Active-state styling ─────────────────────────────────────────────────

    def set_active(self, key: str):
        for k, btn in self._nav_buttons.items():
            active = k == key
            btn.configure(
                fg_color=theme.PRIMARY if active else "transparent",
                text_color="#FFFFFF" if active else theme.TEXT_SECONDARY,
            )
        self.set_active_category(None)

    def set_active_category(self, category: str | None):
        for c, btn in self._category_buttons.items():
            active = c == category
            colour = theme.CATEGORY_COLOURS.get(c, theme.TEXT_MUTED)
            btn.configure(
                fg_color=theme.PANEL if active else "transparent",
                text_color="#FFFFFF" if active else colour,
            )
        if category is not None:
            for k, btn in self._nav_buttons.items():
                btn.configure(fg_color="transparent", text_color=theme.TEXT_SECONDARY)
