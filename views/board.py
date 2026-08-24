"""
views/board.py — Full Board View
Uses a manual Canvas+Scrollbar for smooth fast scrolling in List View.
CTkScrollableFrame has laggy scroll on Windows — canvas is native and instant.
"""

import customtkinter as ctk
import tkinter as tk
import storage
import theme
from models import Task
from views.components.task_card import TaskCard

ALL = "All"
KANBAN_STATUSES = ["Todo", "In Progress", "Done", "Blocked"]


class BoardView(ctk.CTkFrame):

    def __init__(self, parent, search_var: ctk.StringVar | None = None):
        super().__init__(parent, fg_color=theme.BG)

        self._search_var = search_var or ctk.StringVar(value="")
        self._search_var.trace_add("write", lambda *_: self._render())
        self._view_mode = ctk.StringVar(value="list")

        self._build_header()
        self._build_filter_bar()
        self._build_view_toggle()
        self._build_scroll_area()
        self._render()

    # ── Header ────────────────────────────────────────────────────────────────

    def _build_header(self):
        row = ctk.CTkFrame(self, fg_color="transparent")
        row.pack(fill="x", padx=theme.SPACE_3XL, pady=(theme.SPACE_3XL, 0))

        title_col = ctk.CTkFrame(row, fg_color="transparent")
        title_col.pack(side="left")

        ctk.CTkLabel(
            title_col, text="Board",
            font=theme.FONT_PAGE_TITLE(), text_color=theme.TEXT,
        ).pack(anchor="w")

        ctk.CTkLabel(
            title_col, text="Organize and track all your tasks",
            font=theme.FONT_BODY(), text_color=theme.TEXT_SECONDARY,
        ).pack(anchor="w", pady=(2, 0))

        ctk.CTkButton(
            row, text="+  Add Task",
            width=120, height=36, corner_radius=8,
            fg_color=theme.PRIMARY, hover_color=theme.PRIMARY_HOVER,
            text_color="#FFFFFF",
            font=theme.font(13, "bold"),
            command=self._open_add_modal,
        ).pack(side="right", anchor="n")

    # ── Filters ───────────────────────────────────────────────────────────────

    def _build_filter_bar(self):
        bar = ctk.CTkFrame(self, fg_color="transparent")
        bar.pack(fill="x", padx=theme.SPACE_3XL, pady=(theme.SPACE_XL, 0))

        lf = theme.FONT_META()

        ctk.CTkLabel(bar, text="Category", font=lf, text_color=theme.TEXT_MUTED).pack(side="left")
        self._cat_var = ctk.StringVar(value=ALL)
        self._cat_menu = ctk.CTkOptionMenu(
            bar, variable=self._cat_var, values=[ALL],
            width=108, height=30, corner_radius=8,
            fg_color=theme.PANEL, button_color=theme.CARD,
            button_hover_color=theme.CARD_HOVER,
            text_color=theme.TEXT, font=lf,
            command=lambda _: self._render(),
        )
        self._cat_menu.pack(side="left", padx=(6, theme.SPACE_LG))

        ctk.CTkLabel(bar, text="Skill", font=lf, text_color=theme.TEXT_MUTED).pack(side="left")
        self._skill_var = ctk.StringVar(value=ALL)
        self._skill_menu = ctk.CTkOptionMenu(
            bar, variable=self._skill_var, values=[ALL],
            width=108, height=30, corner_radius=8,
            fg_color=theme.PANEL, button_color=theme.CARD,
            button_hover_color=theme.CARD_HOVER,
            text_color=theme.TEXT, font=lf,
            command=lambda _: self._render(),
        )
        self._skill_menu.pack(side="left", padx=(6, theme.SPACE_LG))

        ctk.CTkLabel(bar, text="Status", font=lf, text_color=theme.TEXT_MUTED).pack(side="left")
        self._status_var = ctk.StringVar(value=ALL)
        self._status_menu = ctk.CTkOptionMenu(
            bar, variable=self._status_var,
            values=[ALL] + KANBAN_STATUSES,
            width=108, height=30, corner_radius=8,
            fg_color=theme.PANEL, button_color=theme.CARD,
            button_hover_color=theme.CARD_HOVER,
            text_color=theme.TEXT, font=lf,
            command=lambda _: self._render(),
        )
        self._status_menu.pack(side="left", padx=(6, theme.SPACE_LG))

        ctk.CTkButton(
            bar, text="Clear Filters",
            width=100, height=30, corner_radius=8,
            fg_color="transparent", hover_color=theme.PANEL,
            border_width=1, border_color=theme.BORDER,
            text_color=theme.TEXT_SECONDARY, font=lf,
            command=self._clear_filters,
        ).pack(side="left")

        ctk.CTkFrame(self, height=1, fg_color=theme.BORDER).pack(
            fill="x", padx=theme.SPACE_3XL, pady=(theme.SPACE_LG, 0)
        )

    def _build_view_toggle(self):
        bar = ctk.CTkFrame(self, fg_color="transparent")
        bar.pack(fill="x", padx=theme.SPACE_3XL, pady=(theme.SPACE_LG, 0))

        self._list_btn = ctk.CTkButton(
            bar, text="☷  List View",
            width=120, height=30, corner_radius=8,
            font=theme.FONT_META(),
            command=lambda: self._set_view_mode("list"),
        )
        self._list_btn.pack(side="left", padx=(0, 6))

        self._board_btn = ctk.CTkButton(
            bar, text="▦  Board View",
            width=120, height=30, corner_radius=8,
            font=theme.FONT_META(),
            command=lambda: self._set_view_mode("board"),
        )
        self._board_btn.pack(side="left")

        self._update_view_toggle_style()

    def _set_view_mode(self, mode: str):
        self._view_mode.set(mode)
        self._update_view_toggle_style()
        self._render()

    def _update_view_toggle_style(self):
        active = {"fg_color": theme.PRIMARY, "hover_color": theme.PRIMARY_HOVER, "text_color": "#FFFFFF"}
        inactive = {"fg_color": theme.PANEL, "hover_color": theme.CARD_HOVER, "text_color": theme.TEXT_SECONDARY}
        self._list_btn.configure(**(active if self._view_mode.get() == "list" else inactive))
        self._board_btn.configure(**(active if self._view_mode.get() == "board" else inactive))

    def _clear_filters(self):
        self._cat_var.set(ALL)
        self._skill_var.set(ALL)
        self._status_var.set(ALL)
        self._search_var.set("")
        self._render()

    def set_category_filter(self, category: str):
        """Called from the sidebar's category quick-filter list."""
        self._cat_var.set(category)
        self._render()

    # ── Scroll area (List View host) ─────────────────────────────────────────

    def _build_scroll_area(self):
        """
        Native tk.Canvas + Scrollbar for smooth 60fps scrolling.
        CTkScrollableFrame uses after() polling which causes visible lag/drag.
        Canvas mousewheel events are direct and instant.
        """
        self._container = ctk.CTkFrame(self, fg_color=theme.BG)
        self._container.pack(fill="both", expand=True, padx=theme.SPACE_3XL, pady=theme.SPACE_LG)

        self._scrollbar = ctk.CTkScrollbar(self._container)
        self._scrollbar.pack(side="right", fill="y")

        self._canvas = tk.Canvas(
            self._container,
            bg=theme.BG,
            highlightthickness=0,
            yscrollcommand=self._scrollbar.set,
        )
        self._canvas.pack(side="left", fill="both", expand=True)
        self._scrollbar.configure(command=self._canvas.yview)

        self._inner = ctk.CTkFrame(self._canvas, fg_color=theme.BG)
        self._canvas_window = self._canvas.create_window(
            (0, 0), window=self._inner, anchor="nw"
        )

        self._canvas.bind("<Configure>", self._on_canvas_configure)
        self._inner.bind("<Configure>", self._on_inner_configure)

        self._canvas.bind_all("<MouseWheel>",
            lambda e: self._canvas.yview_scroll(-1 * (e.delta // 120), "units")
        )

        # Kanban host — built fresh each render, packed only in board mode
        self._kanban_frame = ctk.CTkFrame(self._container, fg_color=theme.BG)

    def _on_canvas_configure(self, event):
        self._canvas.itemconfig(self._canvas_window, width=event.width)

    def _on_inner_configure(self, event):
        self._canvas.configure(scrollregion=self._canvas.bbox("all"))

    # ── Render ────────────────────────────────────────────────────────────────

    def _filtered_tasks(self):
        tasks = storage.load_tasks()
        self._refresh_filter_options(tasks)

        cat    = self._cat_var.get()
        skill  = self._skill_var.get()
        status = self._status_var.get()
        query  = self._search_var.get().strip().lower()

        if cat    != ALL: tasks = [t for t in tasks if t.category == cat]
        if skill  != ALL: tasks = [t for t in tasks if t.skill    == skill]
        if status != ALL: tasks = [t for t in tasks if t.status   == status]
        if query:         tasks = [t for t in tasks if query in t.title.lower()]

        return tasks

    def _render(self):
        tasks = self._filtered_tasks()

        if self._view_mode.get() == "list":
            self._kanban_frame.pack_forget()
            self._canvas.pack(side="left", fill="both", expand=True)
            self._scrollbar.pack(side="right", fill="y")
            self._render_list(tasks)
        else:
            self._canvas.pack_forget()
            self._scrollbar.pack_forget()
            self._kanban_frame.pack(fill="both", expand=True)
            self._render_kanban(tasks)

    def _render_list(self, tasks):
        for widget in self._inner.winfo_children():
            widget.destroy()

        if not tasks:
            ctk.CTkLabel(
                self._inner,
                text="No tasks match the current filters.",
                font=theme.FONT_BODY(), text_color=theme.TEXT_MUTED,
            ).pack(pady=40)
            return

        for task in tasks:
            card = TaskCard(
                self._inner, task=task,
                on_edit=self._open_edit_modal,
                on_delete=self._handle_delete,
            )
            card.pack(fill="x", pady=5)

    def _render_kanban(self, tasks):
        for widget in self._kanban_frame.winfo_children():
            widget.destroy()

        grouped = {status: [] for status in KANBAN_STATUSES}
        for task in tasks:
            grouped.setdefault(task.status, []).append(task)

        for i, status in enumerate(KANBAN_STATUSES):
            info = theme.STATUS[status]
            column = ctk.CTkFrame(self._kanban_frame, fg_color=theme.PANEL, corner_radius=12)
            trailing_pad = theme.SPACE_SM if i < len(KANBAN_STATUSES) - 1 else 0
            column.pack(side="left", fill="both", expand=True, padx=(0, trailing_pad))

            header = ctk.CTkFrame(column, fg_color="transparent")
            header.pack(fill="x", padx=theme.SPACE_SM, pady=(theme.SPACE_MD, theme.SPACE_SM))
            ctk.CTkLabel(
                header, text=f"{info['icon']}  {status.upper()}",
                font=theme.font(12, "bold"), text_color=info["color"],
            ).pack(side="left")
            ctk.CTkLabel(
                header, text=str(len(grouped[status])),
                font=theme.FONT_META(), text_color=theme.TEXT_MUTED,
            ).pack(side="right")

            body = ctk.CTkScrollableFrame(column, width=1, fg_color="transparent")
            body.pack(fill="both", expand=True, padx=theme.SPACE_SM, pady=(0, theme.SPACE_SM))

            for task in grouped[status]:
                card = TaskCard(
                    body, task=task,
                    on_edit=self._open_edit_modal,
                    on_delete=self._handle_delete,
                    compact=True,
                )
                card.pack(fill="x", pady=4)

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
