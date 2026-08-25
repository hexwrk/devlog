"""
views/overview.py — Overview page
====================================
A real page (not a slide-out panel): weekly progress, focus insights, XP
progression, recent activity, and a compact today/status/focus summary
column. Everything here is read-only and computed from models/analytics.py.
"""

import customtkinter as ctk
import storage
import theme
from models import analytics
from views.components import ui


class OverviewPage(ctk.CTkFrame):

    def __init__(self, parent, weekly_streak_goal: int = 7):
        super().__init__(parent, fg_color=theme.BG)
        self._weekly_streak_goal = weekly_streak_goal
        self._display_name = "Tristan"

        self._scroll = ctk.CTkScrollableFrame(self, fg_color=theme.BG, scrollbar_button_color=theme.BORDER)
        self._scroll.pack(fill="both", expand=True, padx=theme.SPACE_3XL, pady=theme.SPACE_3XL)

        self._header_slot = ctk.CTkFrame(self._scroll, fg_color="transparent")
        self._header_slot.pack(fill="x")

        self._top_row = ctk.CTkFrame(self._scroll, fg_color="transparent")
        self._top_row.pack(fill="x", pady=(theme.SPACE_2XL, 0))

        self._bottom_row = ctk.CTkFrame(self._scroll, fg_color="transparent")
        self._bottom_row.pack(fill="both", expand=True, pady=(theme.SPACE_2XL, 0))

        self.refresh()

    def set_weekly_streak_goal(self, goal: int):
        self._weekly_streak_goal = goal

    def set_display_name(self, display_name: str):
        self._display_name = display_name

    # ── Refresh — rebuild from disk ──────────────────────────────────────────

    def refresh(self, display_name: str | None = None):
        if display_name:
            self._display_name = display_name
        display_name = self._display_name

        for w in self._header_slot.winfo_children():
            w.destroy()
        for w in self._top_row.winfo_children():
            w.destroy()
        for w in self._bottom_row.winfo_children():
            w.destroy()

        tasks = storage.load_tasks()

        header = ui.PageHeader(
            self._header_slot,
            title=f"Welcome back, {display_name.split()[0] if display_name.split() else display_name}",
            breadcrumb=["Workspace", "Overview"],
            subtitle="Here's what's happening with your productivity today.",
            action={"text": f"{theme.icon('add')}  Add Task", "command": self._open_add_modal},
        )
        header.pack(fill="x")

        self._build_top_row(tasks)
        self._build_bottom_row(tasks)

    # ── Top row: progress, velocity, XP ─────────────────────────────────────

    def _build_top_row(self, tasks):
        rate = analytics.get_completion_rate(tasks)
        velocity = analytics.get_weekly_velocity(tasks, weeks=8)
        total_xp = sum(analytics.get_skill_xp(tasks).values())
        level, xp_into, xp_needed = analytics.get_level_progress(total_xp)

        progress_card = ui.Card(self._top_row)
        progress_card.pack(side="left", fill="both", expand=True, padx=(0, theme.SPACE_LG))
        ui.SectionLabel(progress_card, "Progress", padx=theme.SPACE_LG, pady=(theme.SPACE_LG, theme.SPACE_SM))
        ui.ring_chart(progress_card, rate, color=theme.SUCCESS).pack(padx=theme.SPACE_LG, pady=(0, theme.SPACE_SM))
        ctk.CTkLabel(
            progress_card, text="Completion rate",
            font=theme.FONT_META(), text_color=theme.TEXT_MUTED,
        ).pack(padx=theme.SPACE_LG, pady=(0, theme.SPACE_LG))

        velocity_card = ui.Card(self._top_row)
        velocity_card.pack(side="left", fill="both", expand=True, padx=(0, theme.SPACE_LG))
        ui.SectionLabel(velocity_card, "Weekly Velocity", padx=theme.SPACE_LG, pady=(theme.SPACE_LG, theme.SPACE_SM))
        ui.bar_chart(velocity_card, velocity, width=220, height=90).pack(padx=theme.SPACE_LG, pady=(0, theme.SPACE_SM))
        ctk.CTkLabel(
            velocity_card, text="Tasks completed, last 8 weeks",
            font=theme.FONT_META(), text_color=theme.TEXT_MUTED,
        ).pack(padx=theme.SPACE_LG, pady=(0, theme.SPACE_LG))

        xp_card = ui.Card(self._top_row)
        xp_card.pack(side="left", fill="both", expand=True)
        ui.SectionLabel(xp_card, "XP Progress", padx=theme.SPACE_LG, pady=(theme.SPACE_LG, theme.SPACE_SM))
        top = ctk.CTkFrame(xp_card, fg_color="transparent")
        top.pack(fill="x", padx=theme.SPACE_LG)
        ctk.CTkLabel(
            top, text=f"Level {level}", font=theme.font(20, "bold"), text_color=theme.PRIMARY,
        ).pack(side="left")
        ctk.CTkLabel(
            top, text=f"{xp_into} / {xp_needed} XP", font=theme.FONT_META(), text_color=theme.TEXT_MUTED,
        ).pack(side="right")
        ui.ProgressBar(xp_card, xp_into / xp_needed if xp_needed else 0).pack(
            fill="x", padx=theme.SPACE_LG, pady=(theme.SPACE_SM, theme.SPACE_LG)
        )

    # ── Bottom row: recent activity + compact summary ───────────────────────

    def _build_bottom_row(self, tasks):
        left = ctk.CTkFrame(self._bottom_row, fg_color="transparent")
        left.pack(side="left", fill="both", expand=True, padx=(0, theme.SPACE_2XL))

        ui.SectionLabel(left, "Recent Activity")
        recent = sorted(
            (t for t in tasks if t.completed_at), key=lambda t: t.completed_at, reverse=True
        )[:8]
        if recent:
            rows = [[t.title, t.status, t.category, t.completed_at] for t in recent]
            ui.Table(left, ["Task", "Status", "Category", "Completed"], rows, weights=[3, 1, 1, 1]).pack(fill="x")
        else:
            ui.EmptyState(
                left, title="No activity yet",
                subtitle="Complete a task to see it show up here.",
            ).pack(fill="x")

        right = ctk.CTkFrame(self._bottom_row, width=260, fg_color="transparent")
        right.pack(side="right", fill="y")
        right.pack_propagate(False)
        self._build_summary_column(right, tasks)

    def _build_summary_column(self, parent, tasks):
        streak = analytics.get_streak(tasks)
        rate = analytics.get_completion_rate(tasks)
        counts = analytics.get_status_counts(tasks)
        skill = analytics.get_most_active_skill(tasks)
        due = analytics.get_due_today(tasks)

        ui.SectionLabel(parent, "Today")
        self._summary_row(parent, "Day Streak", f"{streak} / {self._weekly_streak_goal} days")
        self._summary_row(parent, "Completion", f"{rate}%")
        ui.Divider(parent, pady=theme.SPACE_LG)

        ui.SectionLabel(parent, "Status")
        for status in theme.STATUS_ORDER:
            self._summary_row(parent, status, str(counts.get(status, 0)), color=theme.STATUS[status]["color"])
        ui.Divider(parent, pady=theme.SPACE_LG)

        ui.SectionLabel(parent, "Focus")
        self._summary_row(parent, "Most Active", skill)
        self._summary_row(parent, "Due Today", str(len(due)) if due else "None")

    def _summary_row(self, parent, label, value, color=None):
        row = ctk.CTkFrame(parent, fg_color="transparent")
        row.pack(fill="x", pady=3)
        ctk.CTkLabel(
            row, text=label, font=theme.FONT_BODY(), text_color=theme.TEXT_SECONDARY, anchor="w",
        ).pack(side="left")
        ctk.CTkLabel(
            row, text=value, font=theme.font(13, "bold"), text_color=color or theme.TEXT, anchor="e",
        ).pack(side="right")

    # ── Quick add ─────────────────────────────────────────────────────────────

    def _open_add_modal(self):
        from views.task_modal import TaskModal
        TaskModal(self, task=None, on_save=self.refresh)
