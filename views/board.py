"""
views/board.py — Full Board View
Uses a manual Canvas+Scrollbar for smooth fast scrolling.
CTkScrollableFrame has laggy scroll on Windows — canvas is native and instant.
"""

import customtkinter as ctk
import tkinter as tk
import storage
from models import Task
from views.components.task_card import TaskCard

MAIN_BG      = "#161616"
CARD_BG      = "#1C1C1E"
DIVIDER      = "#2C2C2E"
TEXT_PRIMARY = "#F5F5F7"
TEXT_MUTED   = "#6E6E73"
ACCENT       = "#7C5CFC"
ALL          = "All"


class BoardView(ctk.CTkFrame):

    def __init__(self, parent):
        super().__init__(parent, fg_color=MAIN_BG)
        self._build_header()
        self._build_filter_bar()
        self._build_scroll_area()
        self._render()

    def _build_header(self):
        row = ctk.CTkFrame(self, fg_color="transparent")
        row.pack(fill="x", padx=32, pady=(28, 0))

        ctk.CTkLabel(
            row, text="Board",
            font=ctk.CTkFont(family="Segoe UI", size=28, weight="bold"),
            text_color=TEXT_PRIMARY,
        ).pack(side="left")

        ctk.CTkButton(
            row,
            text="+ Add Task",
            width=110, height=34, corner_radius=8,
            fg_color=ACCENT, hover_color="#5A3FD4",
            text_color="#FFFFFF",
            font=ctk.CTkFont(family="Segoe UI", size=13, weight="bold"),
            command=self._open_add_modal,
        ).pack(side="right")

    def _build_filter_bar(self):
        bar = ctk.CTkFrame(self, fg_color="transparent")
        bar.pack(fill="x", padx=32, pady=(14, 0))

        lf = ctk.CTkFont(family="Segoe UI", size=12)

        ctk.CTkLabel(bar, text="Category", font=lf, text_color=TEXT_MUTED).pack(side="left")
        self._cat_var = ctk.StringVar(value=ALL)
        self._cat_menu = ctk.CTkOptionMenu(
            bar, variable=self._cat_var, values=[ALL],
            width=130, height=30, fg_color="#2C2C2E", button_color="#3A3A3C",
            text_color=TEXT_PRIMARY, font=lf,
            command=lambda _: self._render(),
        )
        self._cat_menu.pack(side="left", padx=(6, 20))

        ctk.CTkLabel(bar, text="Skill", font=lf, text_color=TEXT_MUTED).pack(side="left")
        self._skill_var = ctk.StringVar(value=ALL)
        self._skill_menu = ctk.CTkOptionMenu(
            bar, variable=self._skill_var, values=[ALL],
            width=130, height=30, fg_color="#2C2C2E", button_color="#3A3A3C",
            text_color=TEXT_PRIMARY, font=lf,
            command=lambda _: self._render(),
        )
        self._skill_menu.pack(side="left", padx=(6, 20))

        ctk.CTkLabel(bar, text="Status", font=lf, text_color=TEXT_MUTED).pack(side="left")
        self._status_var = ctk.StringVar(value=ALL)
        self._status_menu = ctk.CTkOptionMenu(
            bar, variable=self._status_var,
            values=[ALL, "Todo", "In Progress", "Done", "Blocked"],
            width=130, height=30, fg_color="#2C2C2E", button_color="#3A3A3C",
            text_color=TEXT_PRIMARY, font=lf,
            command=lambda _: self._render(),
        )
        self._status_menu.pack(side="left", padx=(6, 0))

        ctk.CTkFrame(self, height=1, fg_color=DIVIDER).pack(fill="x", padx=32, pady=(14, 0))

    def _build_scroll_area(self):
        """
        Native tk.Canvas + Scrollbar for smooth 60fps scrolling on Windows.
        CTkScrollableFrame uses after() polling which causes visible lag/drag.
        Canvas mousewheel events are direct and instant.
        """
        container = ctk.CTkFrame(self, fg_color=MAIN_BG)
        container.pack(fill="both", expand=True, padx=32, pady=16)

        # Scrollbar
        self._scrollbar = ctk.CTkScrollbar(container)
        self._scrollbar.pack(side="right", fill="y")

        # Canvas
        self._canvas = tk.Canvas(
            container,
            bg=MAIN_BG,
            highlightthickness=0,
            yscrollcommand=self._scrollbar.set,
        )
        self._canvas.pack(side="left", fill="both", expand=True)
        self._scrollbar.configure(command=self._canvas.yview)

        # Inner frame that holds the cards
        self._inner = ctk.CTkFrame(self._canvas, fg_color=MAIN_BG)
        self._canvas_window = self._canvas.create_window(
            (0, 0), window=self._inner, anchor="nw"
        )

        # Resize inner frame when canvas width changes
        self._canvas.bind("<Configure>", self._on_canvas_configure)
        self._inner.bind("<Configure>", self._on_inner_configure)

        # Fast mousewheel scroll — bound to canvas directly
        self._canvas.bind_all("<MouseWheel>",
            lambda e: self._canvas.yview_scroll(-1 * (e.delta // 120), "units")
        )

    def _on_canvas_configure(self, event):
        self._canvas.itemconfig(self._canvas_window, width=event.width)

    def _on_inner_configure(self, event):
        self._canvas.configure(scrollregion=self._canvas.bbox("all"))

    def _render(self):
        for widget in self._inner.winfo_children():
            widget.destroy()

        tasks = storage.load_tasks()
        self._refresh_filter_options(tasks)

        cat    = self._cat_var.get()
        skill  = self._skill_var.get()
        status = self._status_var.get()

        if cat    != ALL: tasks = [t for t in tasks if t.category == cat]
        if skill  != ALL: tasks = [t for t in tasks if t.skill    == skill]
        if status != ALL: tasks = [t for t in tasks if t.status   == status]

        if not tasks:
            ctk.CTkLabel(
                self._inner,
                text="No tasks match the current filters.",
                font=ctk.CTkFont(family="Segoe UI", size=14),
                text_color=TEXT_MUTED,
            ).pack(pady=40)
            return

        for task in tasks:
            card = TaskCard(
                self._inner, task=task,
                on_edit=self._open_edit_modal,
                on_delete=self._handle_delete,
            )
            card.pack(fill="x", pady=5)

    def _refresh_filter_options(self, tasks):
        cats   = [ALL] + sorted({t.category for t in tasks})
        skills = [ALL] + sorted({t.skill for t in tasks})
        self._cat_menu.configure(values=cats)
        self._skill_menu.configure(values=skills)
        if self._cat_var.get()   not in cats:   self._cat_var.set(ALL)
        if self._skill_var.get() not in skills: self._skill_var.set(ALL)

    def _handle_delete(self, task_id: str):
        storage.delete_task(task_id)
        self._render()

    def _open_add_modal(self):
        from views.task_modal import TaskModal
        TaskModal(self, task=None, on_save=self._on_modal_save)

    def _open_edit_modal(self, task: Task):
        from views.task_modal import TaskModal
        TaskModal(self, task=task, on_save=self._on_modal_save)

    def _on_modal_save(self):
        self._render()
