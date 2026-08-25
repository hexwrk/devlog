"""
views/projects.py — Projects: list + per-project workspace
==============================================================
Projects list shows each of the six fixed task categories as a workspace
card (task count + completion). Clicking one drills into a detail view
scoped to that category, with its own breadcrumb (Projects / CTF).
"""

import customtkinter as ctk
import storage
import theme
from models import CATEGORIES, Task, analytics
from views.components import ui
from views.components.task_card import render_task_rows

CARD_COLUMNS = 3


class ProjectsView(ctk.CTkFrame):

    def __init__(self, parent, on_category_change=None):
        super().__init__(parent, fg_color=theme.BG)
        self._selected: str | None = None
        self._on_category_change = on_category_change

        self._scroll = ctk.CTkScrollableFrame(self, fg_color=theme.BG, scrollbar_button_color=theme.BORDER)
        self._scroll.pack(fill="both", expand=True, padx=theme.SPACE_3XL, pady=theme.SPACE_3XL)

        self._body = ctk.CTkFrame(self._scroll, fg_color="transparent")
        self._body.pack(fill="both", expand=True)

        self.refresh()

    def show_list(self):
        self._selected = None
        self.refresh()

    def show_category(self, category: str):
        self._selected = category
        self.refresh()

    @property
    def selected_category(self):
        return self._selected

    def refresh(self):
        for w in self._body.winfo_children():
            w.destroy()

        if self._on_category_change:
            self._on_category_change(self._selected)

        tasks = storage.load_tasks()
        if self._selected:
            self._build_detail(tasks)
        else:
            self._build_list(tasks)

    # ── List: one card per category ─────────────────────────────────────────

    def _build_list(self, tasks):
        header = ui.PageHeader(
            self._body, title="Projects",
            breadcrumb=["Projects"],
            subtitle="Your task categories as dedicated workspaces.",
        )
        header.pack(fill="x")

        grid = ctk.CTkFrame(self._body, fg_color="transparent")
        grid.pack(fill="x", pady=(theme.SPACE_2XL, 0))
        for c in range(CARD_COLUMNS):
            grid.grid_columnconfigure(c, weight=1)

        performance = analytics.get_category_performance(tasks)

        for i, category in enumerate(CATEGORIES):
            stats = performance.get(category, {"total": 0, "completed": 0, "time_minutes": 0})
            r, c = divmod(i, CARD_COLUMNS)
            self._project_card(grid, category, stats).grid(
                row=r, column=c, sticky="nsew",
                padx=(0 if c == 0 else theme.SPACE_MD, 0 if c == CARD_COLUMNS - 1 else theme.SPACE_MD),
                pady=theme.SPACE_MD,
            )

    def _project_card(self, parent, category, stats):
        card = ui.Card(parent)

        ui.CategoryDot(card, category).pack(
            anchor="w", padx=theme.SPACE_LG, pady=(theme.SPACE_LG, theme.SPACE_XS)
        )

        total, completed = stats["total"], stats["completed"]
        pct = round(completed / total * 100) if total else 0
        ctk.CTkLabel(
            card, text=f"{total} task{'s' if total != 1 else ''} · {pct}% complete",
            font=theme.FONT_META(), text_color=theme.TEXT_MUTED,
        ).pack(anchor="w", padx=theme.SPACE_LG)

        ui.ProgressBar(
            card, pct / 100, color=theme.CATEGORY_COLOURS.get(category, theme.PRIMARY),
        ).pack(fill="x", padx=theme.SPACE_LG, pady=(theme.SPACE_SM, theme.SPACE_MD))

        ui.SecondaryButton(
            card, text="View Project  ›", width=140, height=30,
            command=lambda c=category: self.show_category(c),
        ).pack(anchor="w", padx=theme.SPACE_LG, pady=(0, theme.SPACE_LG))

        return card

    # ── Detail: single category workspace ────────────────────────────────────

    def _build_detail(self, tasks):
        category = self._selected
        cat_tasks = [t for t in tasks if t.category == category]
        completed = [t for t in cat_tasks if t.status == "Done"]
        remaining = len(cat_tasks) - len(completed)
        pct = round(len(completed) / len(cat_tasks) * 100) if cat_tasks else 0

        ui.GhostButton(
            self._body, text=f"{theme.icon('back')}  Back to Projects", width=160, height=28,
            command=self.show_list,
        ).pack(anchor="w", pady=(0, theme.SPACE_MD))

        header = ui.PageHeader(
            self._body, title=category,
            breadcrumb=["Projects", category],
            subtitle=f"{len(cat_tasks)} task{'s' if len(cat_tasks) != 1 else ''} in this project.",
            action={"text": f"{theme.icon('add')}  Add Task", "command": self._open_add_modal},
        )
        header.pack(fill="x")

        progress_card = ui.Card(self._body)
        progress_card.pack(fill="x", pady=(theme.SPACE_2XL, 0))

        top = ctk.CTkFrame(progress_card, fg_color="transparent")
        top.pack(fill="x", padx=theme.SPACE_LG, pady=(theme.SPACE_LG, theme.SPACE_XS))
        ctk.CTkLabel(
            top, text="Progress", font=theme.FONT_META(), text_color=theme.TEXT_MUTED,
        ).pack(side="left")
        ctk.CTkLabel(
            top, text=f"{pct}%", font=theme.font(13, "bold"), text_color=theme.TEXT,
        ).pack(side="right")
        ui.ProgressBar(
            progress_card, pct / 100, color=theme.CATEGORY_COLOURS.get(category, theme.PRIMARY),
        ).pack(fill="x", padx=theme.SPACE_LG, pady=(0, theme.SPACE_MD))

        stats_row = ctk.CTkFrame(progress_card, fg_color="transparent")
        stats_row.pack(fill="x", padx=theme.SPACE_LG, pady=(0, theme.SPACE_LG))
        ctk.CTkLabel(
            stats_row, text=f"{len(completed)} completed",
            font=theme.FONT_BODY(), text_color=theme.TEXT_SECONDARY,
        ).pack(side="left")
        ctk.CTkLabel(
            stats_row, text=f"{remaining} remaining",
            font=theme.FONT_BODY(), text_color=theme.TEXT_SECONDARY,
        ).pack(side="left", padx=(theme.SPACE_LG, 0))

        ui.SectionLabel(self._body, "Tasks", pady=(theme.SPACE_2XL, theme.SPACE_SM))
        if not cat_tasks:
            ui.EmptyState(
                self._body,
                title="No tasks yet",
                subtitle=f"Add a task to start building the {category} project.",
                action_text=f"{theme.icon('add')}  Add your first task",
                action_command=self._open_add_modal,
            ).pack(fill="x")
        else:
            render_task_rows(
                self._body, cat_tasks,
                on_edit=self._open_edit_modal,
                on_delete=self._handle_delete,
                on_advance=self._handle_advance,
            )

    # ── Task actions ─────────────────────────────────────────────────────────

    def _open_add_modal(self):
        from views.task_modal import TaskModal
        TaskModal(self, task=None, on_save=self.refresh, default_category=self._selected)

    def _open_edit_modal(self, task: Task):
        from views.task_modal import TaskModal
        TaskModal(self, task=task, on_save=self.refresh)

    def _handle_delete(self, task_id: str):
        storage.delete_task(task_id)
        self.refresh()

    def _handle_advance(self, task: Task):
        task.status = theme.next_status(task.status)
        storage.update_task(task)
        self.refresh()
