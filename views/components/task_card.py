"""
views/components/task_card.py  (Redesign: Sleek & Minimal)
"""

from typing import Callable
import customtkinter as ctk
from models import Task

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

STATUS_BG = {
    "Todo":        "#2A2A2C",
    "In Progress": "#2A2210",
    "Done":        "#0D2A1A",
    "Blocked":     "#2A0D15",
}


class TaskCard(ctk.CTkFrame):

    def __init__(
        self,
        parent,
        task: Task,
        on_edit:   Callable[[Task], None],
        on_delete: Callable[[str],  None],
    ):
        super().__init__(parent, fg_color="transparent",border_color="#2C2C2E", corner_radius=12)

        self._task      = task
        self._on_edit   = on_edit
        self._on_delete = on_delete

        self._build()
        self._bind_hover()

    def _build(self):
        task = self._task

        outer = ctk.CTkFrame(self, fg_color="transparent")
        outer.pack(fill="x", padx=18, pady=14)

        left = ctk.CTkFrame(outer, fg_color="transparent")
        left.pack(side="left", fill="x", expand=True)

        ctk.CTkLabel(
            left,
            text=task.title,
            font=ctk.CTkFont(family="Segoe UI", size=14, weight="bold"),
            text_color=TEXT_PRIMARY,
            anchor="w",
        ).pack(anchor="w")

        tags = ctk.CTkFrame(left, fg_color="transparent")
        tags.pack(anchor="w", pady=(6, 0))

        # Category pill — dark bg, coloured text (tkinter only supports 6-digit hex)
        ctk.CTkLabel(
            tags,
            text=f"  {task.category}  ",
            font=ctk.CTkFont(family="Segoe UI", size=11),
            fg_color="#2C2C2E",
            text_color=task.category_colour,
            corner_radius=6,
        ).pack(side="left", padx=(0, 6))

        # Skill pill
        ctk.CTkLabel(
            tags,
            text=f"  {task.skill}  ",
            font=ctk.CTkFont(family="Segoe UI", size=11),
            fg_color="#2C2C2E",
            text_color=TEXT_MUTED,
            corner_radius=6,
        ).pack(side="left", padx=(0, 6))

        # Status pill
        sc = STATUS_COLOURS.get(task.status, TEXT_MUTED)
        sb = STATUS_BG.get(task.status, "#2A2A2C")
        ctk.CTkLabel(
            tags,
            text=f"  {task.status}  ",
            font=ctk.CTkFont(family="Segoe UI", size=11),
            fg_color=sb,
            text_color=sc,
            corner_radius=6,
        ).pack(side="left")

        right = ctk.CTkFrame(outer, fg_color="transparent")
        right.pack(side="right", padx=(12, 0))

        ctk.CTkButton(
            right,
            text="Edit",
            width=64, height=30, corner_radius=8,
            fg_color="#2C2C2E", hover_color="#3A3A3C",
            text_color=TEXT_PRIMARY,
            font=ctk.CTkFont(family="Segoe UI", size=12),
            command=lambda t=task: self._on_edit(t),
        ).pack(side="left", padx=(0, 6))

        ctk.CTkButton(
            right,
            text="Delete",
            width=70, height=30, corner_radius=8,
            fg_color="#2C1A1A", hover_color="#4A1A1A",
            text_color="#FC5C7D",
            font=ctk.CTkFont(family="Segoe UI", size=12),
            command=lambda t=task: self._on_delete(t.id),
        ).pack(side="left")

    def _bind_hover(self):
        self.bind("<Enter>", lambda e: self.configure(fg_color=CARD_HOVER))
        self.bind("<Leave>", lambda e: self.configure(fg_color=CARD_BG))
