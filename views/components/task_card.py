"""
views/components/task_card.py — Modern SaaS-style task row
"""

from typing import Callable
import tkinter as tk
import customtkinter as ctk
from models import Task
import theme


class TaskCard(ctk.CTkFrame):

    def __init__(
        self,
        parent,
        task: Task,
        on_edit:   Callable[[Task], None],
        on_delete: Callable[[str],  None],
        compact:   bool = False,
    ):
        super().__init__(
            parent, fg_color=theme.CARD, corner_radius=12,
            border_width=1, border_color=theme.BORDER,
        )

        self._task      = task
        self._on_edit    = on_edit
        self._on_delete  = on_delete
        self._compact    = compact

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
            outer, text="⋮⋮",
            font=theme.font(13), text_color=theme.TEXT_MUTED,
        ).pack(side="left", padx=(0, theme.SPACE_MD))

        ctk.CTkLabel(
            outer, text=theme.skill_icon(task.skill),
            font=theme.font(15), text_color=theme.TEXT_SECONDARY, width=20,
        ).pack(side="left", padx=(0, theme.SPACE_MD))

        left = ctk.CTkFrame(outer, fg_color="transparent")
        left.pack(side="left", fill="x", expand=True)

        ctk.CTkLabel(
            left, text=task.title,
            font=theme.FONT_TASK_TITLE(), text_color=theme.TEXT, anchor="w",
        ).pack(anchor="w")

        badges = ctk.CTkFrame(left, fg_color="transparent")
        badges.pack(anchor="w", pady=(theme.SPACE_XS, 0))

        self._category_badge(badges, task)
        self._skill_badge(badges, task)
        self._status_pill(badges, task)

        right = ctk.CTkFrame(outer, fg_color="transparent")
        right.pack(side="right", padx=(theme.SPACE_MD, 0))

        if task.due_date:
            ctk.CTkLabel(
                right, text=task.due_date,
                font=theme.FONT_META(), text_color=theme.TEXT_MUTED,
            ).pack(side="left", padx=(0, theme.SPACE_MD))

        self._icon_button(right, "✎", lambda: self._on_edit(task)).pack(side="left", padx=(0, 4))
        self._icon_button(right, "⋯", self._open_overflow_menu).pack(side="left")

    # ── Compact (kanban column) layout ───────────────────────────────────────

    def _build_compact(self):
        task = self._task
        pad = theme.SPACE_SM

        outer = ctk.CTkFrame(self, fg_color="transparent")
        outer.pack(fill="x", padx=pad, pady=theme.SPACE_SM)

        top = ctk.CTkFrame(outer, fg_color="transparent")
        top.pack(fill="x")

        ctk.CTkLabel(
            top, text=theme.skill_icon(task.skill),
            font=theme.font(13), text_color=theme.TEXT_SECONDARY,
        ).pack(side="left", padx=(0, theme.SPACE_XS))

        ctk.CTkLabel(
            top, text=task.title,
            font=theme.font(13, "bold"), text_color=theme.TEXT, anchor="w",
            wraplength=90, justify="left",
        ).pack(side="left", fill="x", expand=True)

        self._icon_button(top, "⋯", self._open_overflow_menu).pack(side="right")

        badges = ctk.CTkFrame(outer, fg_color="transparent")
        badges.pack(anchor="w", pady=(theme.SPACE_XS, 0))
        self._status_pill(badges, task)

    # ── Shared badge builders ────────────────────────────────────────────────

    def _category_badge(self, parent, task):
        colour = theme.CATEGORY_COLOURS.get(task.category, theme.TEXT_MUTED)
        icon = theme.CATEGORY_ICONS.get(task.category, "▣")
        ctk.CTkLabel(
            parent, text=f" {icon} {task.category} ",
            font=theme.FONT_META(), fg_color=theme.PANEL,
            text_color=colour, corner_radius=6,
        ).pack(side="left", padx=(0, theme.SPACE_SM))

    def _skill_badge(self, parent, task):
        ctk.CTkLabel(
            parent, text=f" {task.skill} ",
            font=theme.FONT_META(), fg_color=theme.PANEL,
            text_color=theme.TEXT_MUTED, corner_radius=6,
        ).pack(side="left", padx=(0, theme.SPACE_SM))

    def _status_pill(self, parent, task):
        info = theme.STATUS.get(task.status, theme.STATUS["Todo"])
        ctk.CTkLabel(
            parent, text=f" {info['icon']} {task.status} ",
            font=theme.FONT_META(), fg_color=info["bg"],
            text_color=info["color"], corner_radius=999,
        ).pack(side="left")

    def _icon_button(self, parent, symbol, command):
        return ctk.CTkButton(
            parent, text=symbol,
            width=26, height=26, corner_radius=6,
            fg_color="transparent", hover_color=theme.PANEL,
            text_color=theme.TEXT_MUTED,
            font=theme.font(13),
            command=command,
        )

    # ── Overflow menu ─────────────────────────────────────────────────────────

    def _open_overflow_menu(self):
        menu = tk.Menu(
            self, tearoff=0,
            bg=theme.PANEL, fg=theme.TEXT,
            activebackground=theme.CARD_HOVER, activeforeground=theme.TEXT,
            bd=0,
        )
        menu.add_command(label="Edit", command=lambda: self._on_edit(self._task))
        menu.add_command(label="Delete", command=lambda: self._on_delete(self._task.id))
        try:
            menu.tk_popup(self.winfo_pointerx(), self.winfo_pointery())
        finally:
            menu.grab_release()

    def _bind_hover(self):
        self.bind("<Enter>", lambda e: self.configure(fg_color=theme.CARD_HOVER))
        self.bind("<Leave>", lambda e: self.configure(fg_color=theme.CARD))
