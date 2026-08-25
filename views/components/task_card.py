"""
views/components/task_card.py — Compact task row / kanban card
"""

from typing import Callable
import tkinter as tk
import customtkinter as ctk
from models import Task
import theme
from views.components import ui


class TaskCard(ctk.CTkFrame):

    def __init__(
        self,
        parent,
        task: Task,
        on_edit:   Callable[[Task], None],
        on_delete: Callable[[str],  None],
        on_advance: Callable[[Task], None] | None = None,
        compact:   bool = False,
    ):
        super().__init__(
            parent, fg_color=theme.CARD, corner_radius=theme.RADIUS_MD,
            border_width=1, border_color=theme.BORDER,
        )

        self._task       = task
        self._on_edit     = on_edit
        self._on_delete   = on_delete
        self._on_advance  = on_advance
        self._compact     = compact

        if compact:
            self._build_compact()
        else:
            self._build_full()
        self._bind_hover()

    # ── Full (list view) layout ──────────────────────────────────────────────

    def _build_full(self):
        task = self._task
        pad = theme.SPACE_LG

        outer = ctk.CTkFrame(self, fg_color="transparent")
        outer.pack(fill="x", padx=pad, pady=theme.SPACE_MD)

        ctk.CTkLabel(
            outer, text=theme.icon("skill"),
            font=theme.font(theme.ICON_SIZE_STD), text_color=theme.TEXT_SECONDARY, width=20,
        ).pack(side="left", padx=(0, theme.SPACE_MD))

        left = ctk.CTkFrame(outer, fg_color="transparent")
        left.pack(side="left", fill="x", expand=True)

        ctk.CTkLabel(
            left, text=task.title,
            font=theme.FONT_TASK_TITLE(), text_color=theme.TEXT, anchor="w",
        ).pack(anchor="w")

        badges = ctk.CTkFrame(left, fg_color="transparent")
        badges.pack(anchor="w", pady=(theme.SPACE_XS, 0))

        ui.CategoryDot(badges, task.category).pack(side="left", padx=(0, theme.SPACE_MD))
        ui.SkillBadge(badges, task.skill).pack(side="left", padx=(0, theme.SPACE_SM))
        ui.StatusBadge(badges, task.status).pack(side="left")

        right = ctk.CTkFrame(outer, fg_color="transparent")
        right.pack(side="right", padx=(theme.SPACE_MD, 0))

        if task.due_date:
            ctk.CTkLabel(
                right, text=f"{theme.icon('calendar')}  {task.due_date}",
                font=theme.FONT_META(), text_color=theme.TEXT_MUTED,
            ).pack(side="left", padx=(0, theme.SPACE_MD))

        ui.IconButton(right, theme.icon("edit"), lambda: self._on_edit(task), size=26).pack(side="left", padx=(0, 4))
        ui.IconButton(right, theme.icon("more"), self._open_overflow_menu, size=26).pack(side="left")

    # ── Compact (kanban column) layout ───────────────────────────────────────

    def _build_compact(self):
        task = self._task
        pad = theme.SPACE_SM

        outer = ctk.CTkFrame(self, fg_color="transparent")
        outer.pack(fill="x", padx=pad, pady=theme.SPACE_SM)

        top = ctk.CTkFrame(outer, fg_color="transparent")
        top.pack(fill="x")

        ctk.CTkLabel(
            top, text=task.title,
            font=theme.font(13, "bold"), text_color=theme.TEXT, anchor="w",
            wraplength=100, justify="left",
        ).pack(side="left", fill="x", expand=True)

        ui.IconButton(top, theme.icon("more"), self._open_overflow_menu, size=22).pack(side="right")

        meta = ctk.CTkFrame(outer, fg_color="transparent")
        meta.pack(anchor="w", pady=(theme.SPACE_XS, 0))
        ui.CategoryDot(meta, task.category).pack(anchor="w")

        badges = ctk.CTkFrame(outer, fg_color="transparent")
        badges.pack(anchor="w", pady=(theme.SPACE_XS, 0))
        ui.StatusBadge(badges, task.status).pack(side="left")

    # ── Overflow menu ─────────────────────────────────────────────────────────

    def _open_overflow_menu(self):
        menu = tk.Menu(
            self, tearoff=0,
            bg=theme.PANEL, fg=theme.TEXT,
            activebackground=theme.CARD_HOVER, activeforeground=theme.TEXT,
            bd=0,
        )
        menu.add_command(label="Edit", command=lambda: self._on_edit(self._task))
        if self._on_advance and self._task.status != "Done":
            nxt = theme.next_status(self._task.status)
            menu.add_command(label=f"Move to {nxt}", command=lambda: self._on_advance(self._task))
        menu.add_command(label="Delete", command=lambda: self._on_delete(self._task.id))
        try:
            menu.tk_popup(self.winfo_pointerx(), self.winfo_pointery())
        finally:
            menu.grab_release()

    def _bind_hover(self):
        self.bind("<Enter>", lambda e: self.configure(fg_color=theme.CARD_HOVER))
        self.bind("<Leave>", lambda e: self.configure(fg_color=theme.CARD))


def render_task_rows(container, tasks: list[Task], on_edit, on_delete, on_advance=None):
    """Shared list-view row renderer used by both Board and the Projects detail page."""
    for task in tasks:
        card = TaskCard(
            container, task=task,
            on_edit=on_edit, on_delete=on_delete, on_advance=on_advance,
        )
        card.pack(fill="x", pady=5)
