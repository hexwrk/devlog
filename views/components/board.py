"""
views/board.py — Full Board View
=================================
Loads tasks from storage, renders them as TaskCards,
provides filter bar and Add Task button.

The render pattern
------------------
_render() always:
  1. Destroys all existing card widgets
  2. Calls storage.load_tasks() fresh from disk
  3. Applies filters
  4. Rebuilds cards

This means disk is the single source of truth.
We never keep a separate in-memory list that could drift out of sync.
"""

import customtkinter as ctk
import storage
from models import Task
from views.components.task_card import TaskCard

MAIN_BG      = "#161616"
CARD_BG      = "#1C1C1E"
DIVIDER      = "#2C2C2E"
TEXT_PRIMARY = "#F5F5F7"
TEXT_MUTED   = "#6E6E73"
ACCENT       = "#7C5CFC"

ALL = "All"   # sentinel value for "no filter"


class BoardView(ctk.CTkFrame):

    def __init__(self, parent):
        super().__init__(parent, fg_color=MAIN_BG)
        self._build_header()
        self._build_filter_bar()
        self._build_scroll_area()
        self._render()

    # ── Header ────────────────────────────────────────────────────────────────

    def _build_header(self):
        row = ctk.CTkFrame(self, fg_color="transparent")
        row.pack(fill="x", padx=32, pady=(28, 0))

        ctk.CTkLabel(
            row, text="Board",
            font=ctk.CTkFont(family="Segoe UI", size=28, weight="bold"),
            text_color=TEXT_PRIMARY,
        ).pack(side="left")

        # Add Task button (top-right)
        ctk.CTkButton(
            row,
            text="+ Add Task",
            width=110, height=34, corner_radius=8,
            fg_color=ACCENT, hover_color="#5A3FD4",
            text_color="#FFFFFF",
            font=ctk.CTkFont(family="Segoe UI", size=13, weight="bold"),
            command=self._open_add_modal,
        ).pack(side="right")

    # ── Filter bar ────────────────────────────────────────────────────────────

    def _build_filter_bar(self):
        bar = ctk.CTkFrame(self, fg_color="transparent")
        bar.pack(fill="x", padx=32, pady=(14, 0))

        label_font = ctk.CTkFont(family="Segoe UI", size=12)
        menu_font  = ctk.CTkFont(family="Segoe UI", size=12)

        # Category filter
        ctk.CTkLabel(bar, text="Category", font=label_font,
                     text_color=TEXT_MUTED).pack(side="left")
        self._cat_var = ctk.StringVar(value=ALL)
        self._cat_menu = ctk.CTkOptionMenu(
            bar, variable=self._cat_var,
            values=[ALL], width=130, height=30,
            fg_color="#2C2C2E", button_color="#3A3A3C",
            text_color=TEXT_PRIMARY, font=menu_font,
            command=lambda _: self._render(),
        )
        self._cat_menu.pack(side="left", padx=(6, 20))

        # Skill filter
        ctk.CTkLabel(bar, text="Skill", font=label_font,
                     text_color=TEXT_MUTED).pack(side="left")
        self._skill_var = ctk.StringVar(value=ALL)
        self._skill_menu = ctk.CTkOptionMenu(
            bar, variable=self._skill_var,
            values=[ALL], width=130, height=30,
            fg_color="#2C2C2E", button_color="#3A3A3C",
            text_color=TEXT_PRIMARY, font=menu_font,
            command=lambda _: self._render(),
        )
        self._skill_menu.pack(side="left", padx=(6, 20))

        # Status filter
        ctk.CTkLabel(bar, text="Status", font=label_font,
                     text_color=TEXT_MUTED).pack(side="left")
        self._status_var = ctk.StringVar(value=ALL)
        self._status_menu = ctk.CTkOptionMenu(
            bar, variable=self._status_var,
            values=[ALL, "Todo", "In Progress", "Done", "Blocked"],
            width=130, height=30,
            fg_color="#2C2C2E", button_color="#3A3A3C",
            text_color=TEXT_PRIMARY, font=menu_font,
            command=lambda _: self._render(),
        )
        self._status_menu.pack(side="left", padx=(6, 0))

        # Divider
        ctk.CTkFrame(self, height=1, fg_color=DIVIDER).pack(
            fill="x", padx=32, pady=(14, 0)
        )

    # ── Scrollable card area ──────────────────────────────────────────────────

    def _build_scroll_area(self):
        self._scroll = ctk.CTkScrollableFrame(
            self, fg_color=MAIN_BG,
            scrollbar_button_color=DIVIDER,
        )
        self._scroll.pack(fill="both", expand=True, padx=32, pady=16)

    # ── Render ────────────────────────────────────────────────────────────────

    def _render(self):
        """
        Clear all cards, reload from disk, apply filters, rebuild.
        This is THE render pattern — always read from source of truth.
        """
        # 1. Destroy existing cards
        for widget in self._scroll.winfo_children():
            widget.destroy()

        # 2. Load fresh from disk
        tasks = storage.load_tasks()

        # 3. Update filter dropdowns with real values from data
        self._refresh_filter_options(tasks)

        # 4. Apply filters
        cat    = self._cat_var.get()
        skill  = self._skill_var.get()
        status = self._status_var.get()

        if cat    != ALL: tasks = [t for t in tasks if t.category == cat]
        if skill  != ALL: tasks = [t for t in tasks if t.skill    == skill]
        if status != ALL: tasks = [t for t in tasks if t.status   == status]

        # 5. Render cards (or empty state)
        if not tasks:
            ctk.CTkLabel(
                self._scroll,
                text="No tasks match the current filters.",
                font=ctk.CTkFont(family="Segoe UI", size=14),
                text_color=TEXT_MUTED,
            ).pack(pady=40)
            return

        for task in tasks:
            card = TaskCard(
                self._scroll, task=task,
                on_edit=self._open_edit_modal,
                on_delete=self._handle_delete,
            )
            card.pack(fill="x", pady=5)

    def _refresh_filter_options(self, tasks: list[Task]):
        """Keep dropdown values in sync with actual data."""
        cats   = [ALL] + sorted({t.category for t in tasks})
        skills = [ALL] + sorted({t.skill     for t in tasks})

        self._cat_menu.configure(values=cats)
        self._skill_menu.configure(values=skills)

        # If current selection no longer exists, reset to All
        if self._cat_var.get()   not in cats:   self._cat_var.set(ALL)
        if self._skill_var.get() not in skills: self._skill_var.set(ALL)

    # ── Callbacks ─────────────────────────────────────────────────────────────

    def _handle_delete(self, task_id: str):
        storage.delete_task(task_id)
        self._render()   # re-render from disk — the deleted task is simply gone

    def _open_add_modal(self):
        from views.task_modal import TaskModal
        TaskModal(self, task=None, on_save=self._on_modal_save)

    def _open_edit_modal(self, task: Task):
        from views.task_modal import TaskModal
        TaskModal(self, task=task, on_save=self._on_modal_save)

    def _on_modal_save(self):
        self._render()   # re-render after add or edit