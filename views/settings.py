"""
views/settings.py — Settings page
=====================================
Real, working preferences backed by settings_store.json: display name/role
(shown in the sidebar + header), weekly streak goal, and default board view.
Plus a read-only About section (data file location, taxonomy, shortcuts).
"""

from typing import Callable
import customtkinter as ctk
import storage
import settings_store
import theme
from models import CATEGORIES
from views.task_modal import SKILLS
from views.components import ui

APP_VERSION = "DevLog v1.0"

SHORTCUTS = [
    ("N", "New Task"), ("/", "Search"), ("B", "Board"),
    ("O", "Overview"), ("A", "Analytics"), ("Esc", "Close"), ("Enter", "Confirm"),
]


class SettingsView(ctk.CTkFrame):

    def __init__(self, parent, on_settings_saved: Callable[[dict], None]):
        super().__init__(parent, fg_color=theme.BG)
        self._on_settings_saved = on_settings_saved

        self._scroll = ctk.CTkScrollableFrame(self, fg_color=theme.BG, scrollbar_button_color=theme.BORDER)
        self._scroll.pack(fill="both", expand=True, padx=theme.SPACE_3XL, pady=theme.SPACE_3XL)

        self._body = ctk.CTkFrame(self._scroll, fg_color="transparent")
        self._body.pack(fill="both", expand=True)

        self.refresh()

    def refresh(self):
        for w in self._body.winfo_children():
            w.destroy()

        settings = settings_store.load_settings()

        header = ui.PageHeader(
            self._body, title="Settings",
            breadcrumb=["Settings"],
            subtitle="Configure your profile and workspace defaults.",
        )
        header.pack(fill="x")

        self._build_profile_card(settings)
        self._build_preferences_card(settings)
        self._build_about_card()

    # ── Profile ──────────────────────────────────────────────────────────────

    def _build_profile_card(self, settings):
        ui.SectionLabel(self._body, "Profile", pady=(theme.SPACE_2XL, theme.SPACE_SM))
        card = ui.Card(self._body)
        card.pack(fill="x")

        self._name_entry = self._field(card, "Display Name", settings["display_name"])
        self._role_entry = self._field(card, "Role", settings["role"])

    # ── Preferences ──────────────────────────────────────────────────────────

    def _build_preferences_card(self, settings):
        ui.SectionLabel(self._body, "Preferences", pady=(theme.SPACE_2XL, theme.SPACE_SM))
        card = ui.Card(self._body)
        card.pack(fill="x")

        self._goal_entry = self._field(
            card, "Weekly Streak Goal (days)", str(settings["weekly_streak_goal"])
        )

        ctk.CTkLabel(
            card, text="Default Board View", font=theme.FONT_META(), text_color=theme.TEXT_MUTED,
        ).pack(anchor="w", padx=theme.SPACE_LG, pady=(theme.SPACE_SM, theme.SPACE_XS))

        self._view_var = ctk.StringVar(value=settings["default_board_view"])
        toggle_row = ctk.CTkFrame(card, fg_color="transparent")
        toggle_row.pack(anchor="w", padx=theme.SPACE_LG, pady=(0, theme.SPACE_MD))

        self._list_toggle = ctk.CTkRadioButton(
            toggle_row, text="List", variable=self._view_var, value="list",
            fg_color=theme.PRIMARY, text_color=theme.TEXT, font=theme.FONT_BODY(),
        )
        self._list_toggle.pack(side="left", padx=(0, theme.SPACE_LG))
        self._board_toggle = ctk.CTkRadioButton(
            toggle_row, text="Board", variable=self._view_var, value="board",
            fg_color=theme.PRIMARY, text_color=theme.TEXT, font=theme.FONT_BODY(),
        )
        self._board_toggle.pack(side="left")

        footer = ctk.CTkFrame(card, fg_color="transparent")
        footer.pack(fill="x", padx=theme.SPACE_LG, pady=(theme.SPACE_SM, theme.SPACE_LG))

        self._status_label = ctk.CTkLabel(
            footer, text="", font=theme.FONT_META(), text_color=theme.SUCCESS,
        )
        self._status_label.pack(side="left")

        ui.PrimaryButton(footer, text="Save Changes", command=self._save, width=140).pack(side="right")

    def _field(self, parent, label, value):
        ctk.CTkLabel(
            parent, text=label, font=theme.FONT_META(), text_color=theme.TEXT_MUTED,
        ).pack(anchor="w", padx=theme.SPACE_LG, pady=(theme.SPACE_LG, theme.SPACE_XS))
        entry = ctk.CTkEntry(
            parent, height=36, corner_radius=theme.RADIUS_SM,
            fg_color=theme.PANEL, border_color=theme.BORDER,
            text_color=theme.TEXT, font=theme.FONT_BODY(),
        )
        entry.insert(0, value)
        entry.pack(fill="x", padx=theme.SPACE_LG, pady=(0, theme.SPACE_MD))
        return entry

    def _save(self):
        goal_text = self._goal_entry.get().strip()
        goal = int(goal_text) if goal_text.isdigit() and int(goal_text) > 0 else settings_store.DEFAULTS["weekly_streak_goal"]

        settings = {
            "display_name": self._name_entry.get().strip() or settings_store.DEFAULTS["display_name"],
            "role": self._role_entry.get().strip() or settings_store.DEFAULTS["role"],
            "weekly_streak_goal": goal,
            "default_board_view": self._view_var.get(),
        }
        settings_store.save_settings(settings)
        self._status_label.configure(text=f"{theme.icon('check')}  Saved")
        self._on_settings_saved(settings)

    # ── About ────────────────────────────────────────────────────────────────

    def _build_about_card(self):
        ui.SectionLabel(self._body, "About", pady=(theme.SPACE_2XL, theme.SPACE_SM))
        card = ui.Card(self._body)
        card.pack(fill="x", pady=(0, theme.SPACE_2XL))

        self._about_row(card, "Version", APP_VERSION)
        self._about_row(card, "Data File", storage.DATA_FILE)
        self._about_row(card, "Categories", ", ".join(CATEGORIES))
        self._about_row(card, "Skills", ", ".join(SKILLS))

        ui.Divider(card, padx=theme.SPACE_LG, pady=theme.SPACE_SM)

        ctk.CTkLabel(
            card, text="Keyboard Shortcuts", font=theme.FONT_META(), text_color=theme.TEXT_MUTED,
        ).pack(anchor="w", padx=theme.SPACE_LG, pady=(theme.SPACE_SM, theme.SPACE_XS))

        shortcuts_row = ctk.CTkFrame(card, fg_color="transparent")
        shortcuts_row.pack(anchor="w", padx=theme.SPACE_LG, pady=(0, theme.SPACE_LG), fill="x")
        for key, action in SHORTCUTS:
            chip = ctk.CTkFrame(shortcuts_row, fg_color=theme.PANEL, corner_radius=theme.RADIUS_SM)
            chip.pack(side="left", padx=(0, theme.SPACE_SM), pady=2)
            ctk.CTkLabel(
                chip, text=f" {key} ", font=theme.font(11, "bold"),
                text_color=theme.TEXT, fg_color=theme.CARD, corner_radius=4,
            ).pack(side="left", padx=4, pady=4)
            ctk.CTkLabel(
                chip, text=f" {action} ", font=theme.FONT_META(), text_color=theme.TEXT_MUTED,
            ).pack(side="left", padx=(0, 6))

    def _about_row(self, parent, label, value):
        row = ctk.CTkFrame(parent, fg_color="transparent")
        row.pack(fill="x", padx=theme.SPACE_LG, pady=(theme.SPACE_MD, 0))
        ctk.CTkLabel(
            row, text=label, font=theme.FONT_BODY(), text_color=theme.TEXT_SECONDARY, anchor="w", width=100,
        ).pack(side="left")
        ctk.CTkLabel(
            row, text=value, font=theme.FONT_BODY(), text_color=theme.TEXT, anchor="w",
            wraplength=520, justify="left",
        ).pack(side="left", fill="x", expand=True)
