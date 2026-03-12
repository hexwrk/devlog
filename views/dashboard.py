"""
views/dashboard.py — Dashboard View
=====================================
Reads tasks from storage, passes them to analytics, displays results.

Call chain:  DashboardView → analytics.py functions → storage.load_tasks()

This view is READ-ONLY. It never calls storage.save_task() or any write
function. The dashboard just observes — it never mutates.

Refresh mechanism
-----------------
A "Refresh" button and auto-refresh on show() ensure the dashboard
always reflects the current state of tasks.json without restarting.
"""

import customtkinter as ctk
import storage
from models import analytics

MAIN_BG      = "#161616"
CARD_BG      = "#1C1C1E"
CARD_HOVER   = "#242426"
DIVIDER      = "#2C2C2E"
TEXT_PRIMARY = "#F5F5F7"
TEXT_MUTED   = "#6E6E73"
ACCENT       = "#7C5CFC"

STATUS_COLOURS = {
    "Todo":        "#6E6E73",
    "In Progress": "#F7B731",
    "Done":        "#43E97B",
    "Blocked":     "#FC5C7D",
}


class DashboardView(ctk.CTkFrame):

    def __init__(self, parent):
        super().__init__(parent, fg_color=MAIN_BG)
        self._build_static_layout()
        self.refresh()

    # ── Static layout (built once) ────────────────────────────────────────────

    def _build_static_layout(self):
        # Scrollable so it works on smaller screens
        self._scroll = ctk.CTkScrollableFrame(
            self, fg_color=MAIN_BG, scrollbar_button_color=DIVIDER
        )
        self._scroll.pack(fill="both", expand=True, padx=32, pady=28)

        # ── Header row ────────────────────────────────────────────────────────
        header = ctk.CTkFrame(self._scroll, fg_color="transparent")
        header.pack(fill="x", pady=(0, 4))

        ctk.CTkLabel(
            header, text="Dashboard",
            font=ctk.CTkFont(family="Segoe UI", size=28, weight="bold"),
            text_color=TEXT_PRIMARY,
        ).pack(side="left")

        ctk.CTkButton(
            header, text="↻  Refresh",
            width=100, height=32, corner_radius=8,
            fg_color="#2C2C2E", hover_color="#3A3A3C",
            text_color=TEXT_MUTED,
            font=ctk.CTkFont(family="Segoe UI", size=12),
            command=self.refresh,
        ).pack(side="right")

        ctk.CTkFrame(self._scroll, height=1, fg_color=DIVIDER).pack(
            fill="x", pady=(12, 24)
        )

        # ── Row 1: Streak + Completion rate ──────────────────────────────────
        row1 = ctk.CTkFrame(self._scroll, fg_color="transparent")
        row1.pack(fill="x", pady=(0, 16))

        self._streak_card  = self._big_stat_card(row1, "🔥", "Day Streak", ACCENT)
        self._rate_card    = self._big_stat_card(row1, "✅", "Completion", "#43E97B")

        # ── Row 2: Status breakdown ───────────────────────────────────────────
        ctk.CTkLabel(
            self._scroll, text="STATUS BREAKDOWN",
            font=ctk.CTkFont(family="Segoe UI", size=11, weight="bold"),
            text_color=TEXT_MUTED,
        ).pack(anchor="w", pady=(0, 8))

        row2 = ctk.CTkFrame(self._scroll, fg_color="transparent")
        row2.pack(fill="x", pady=(0, 24))

        self._status_cards: dict[str, ctk.CTkLabel] = {}
        for status, colour in STATUS_COLOURS.items():
            card, value_label = self._status_tile(row2, status, colour)
            self._status_cards[status] = value_label

        # ── Row 3: Insights ───────────────────────────────────────────────────
        ctk.CTkLabel(
            self._scroll, text="INSIGHTS",
            font=ctk.CTkFont(family="Segoe UI", size=11, weight="bold"),
            text_color=TEXT_MUTED,
        ).pack(anchor="w", pady=(0, 8))

        row3 = ctk.CTkFrame(self._scroll, fg_color="transparent")
        row3.pack(fill="x", pady=(0, 24))

        self._skill_card = self._insight_card(row3, "🛠", "Most Active Skill")
        self._due_card   = self._insight_card(row3, "📅", "Due Today")

        # ── Row 4: Quick add ──────────────────────────────────────────────────
        ctk.CTkFrame(self._scroll, height=1, fg_color=DIVIDER).pack(
            fill="x", pady=(0, 20)
        )

        ctk.CTkButton(
            self._scroll,
            text="+ Quick Add Task",
            height=42, corner_radius=10,
            fg_color=ACCENT, hover_color="#5A3FD4",
            text_color="#FFFFFF",
            font=ctk.CTkFont(family="Segoe UI", size=14, weight="bold"),
            command=self._open_add_modal,
        ).pack(fill="x")

    # ── Card builders (return references to dynamic labels) ───────────────────

    def _big_stat_card(self, parent, icon: str, label: str, colour: str):
        """Large prominent stat card. Returns the value label for updating."""
        frame = ctk.CTkFrame(parent, fg_color=CARD_BG, corner_radius=14)
        frame.pack(side="left", padx=(0, 16), ipadx=24, ipady=20, fill="x", expand=True)

        ctk.CTkLabel(
            frame, text=icon,
            font=ctk.CTkFont(size=28),
        ).pack(pady=(4, 0))

        value_lbl = ctk.CTkLabel(
            frame, text="—",
            font=ctk.CTkFont(family="Segoe UI", size=42, weight="bold"),
            text_color=colour,
        )
        value_lbl.pack()

        ctk.CTkLabel(
            frame, text=label,
            font=ctk.CTkFont(family="Segoe UI", size=12),
            text_color=TEXT_MUTED,
        ).pack(pady=(0, 4))

        return value_lbl

    def _status_tile(self, parent, status: str, colour: str):
        """Small status count tile. Returns (frame, value_label)."""
        frame = ctk.CTkFrame(parent, fg_color=CARD_BG, corner_radius=10)
        frame.pack(side="left", padx=(0, 10), ipadx=16, ipady=12, fill="x", expand=True)

        value_lbl = ctk.CTkLabel(
            frame, text="0",
            font=ctk.CTkFont(family="Segoe UI", size=26, weight="bold"),
            text_color=colour,
        )
        value_lbl.pack()

        ctk.CTkLabel(
            frame, text=status,
            font=ctk.CTkFont(family="Segoe UI", size=11),
            text_color=TEXT_MUTED,
        ).pack()

        return frame, value_lbl

    def _insight_card(self, parent, icon: str, label: str):
        """Insight card showing a text value. Returns value label."""
        frame = ctk.CTkFrame(parent, fg_color=CARD_BG, corner_radius=10)
        frame.pack(side="left", padx=(0, 16), ipadx=20, ipady=16, fill="x", expand=True)

        top = ctk.CTkFrame(frame, fg_color="transparent")
        top.pack(fill="x")

        ctk.CTkLabel(
            top, text=f"{icon}  {label}",
            font=ctk.CTkFont(family="Segoe UI", size=12),
            text_color=TEXT_MUTED,
        ).pack(anchor="w")

        value_lbl = ctk.CTkLabel(
            frame, text="—",
            font=ctk.CTkFont(family="Segoe UI", size=18, weight="bold"),
            text_color=TEXT_PRIMARY,
        )
        value_lbl.pack(anchor="w", pady=(4, 0))

        return value_lbl

    # ── Refresh — recompute all values from disk ──────────────────────────────

    def refresh(self):
        """
        Load tasks fresh from disk and update every label.
        Called on init and whenever the user clicks Refresh.
        Also called by main.py when switching to this view.
        """
        tasks = storage.load_tasks()

        # Streak
        streak = analytics.get_streak(tasks)
        self._streak_card.configure(text=str(streak))

        # Completion rate
        rate = analytics.get_completion_rate(tasks)
        self._rate_card.configure(text=f"{rate}%")

        # Status counts
        counts = analytics.get_status_counts(tasks)
        for status, label in self._status_cards.items():
            label.configure(text=str(counts.get(status, 0)))

        # Most active skill
        skill = analytics.get_most_active_skill(tasks)
        self._skill_card.configure(text=skill)

        # Due today
        due = analytics.get_due_today(tasks)
        due_text = str(len(due)) if due else "None"
        self._due_card.configure(text=due_text)

    # ── Quick add ─────────────────────────────────────────────────────────────

    def _open_add_modal(self):
        from views.task_modal import TaskModal
        TaskModal(self, task=None, on_save=self.refresh)
