"""
views/analytics.py — Analytics page
======================================
A dedicated data-oriented page: headline metrics, a weekly velocity chart,
and per-category task performance. Built entirely from models/analytics.py
functions plus the previously-unused Task.duration_minutes field.
"""

import customtkinter as ctk
import storage
import theme
from models import analytics
from views.components import ui


def _format_minutes(minutes: int) -> str:
    hours, mins = divmod(minutes, 60)
    if hours and mins:
        return f"{hours}h {mins}m"
    if hours:
        return f"{hours}h"
    return f"{mins}m"


class AnalyticsView(ctk.CTkFrame):

    def __init__(self, parent):
        super().__init__(parent, fg_color=theme.BG)

        self._scroll = ctk.CTkScrollableFrame(self, fg_color=theme.BG, scrollbar_button_color=theme.BORDER)
        self._scroll.pack(fill="both", expand=True, padx=theme.SPACE_3XL, pady=theme.SPACE_3XL)

        self._body = ctk.CTkFrame(self._scroll, fg_color="transparent")
        self._body.pack(fill="both", expand=True)

        self.refresh()

    def refresh(self):
        for w in self._body.winfo_children():
            w.destroy()

        tasks = storage.load_tasks()

        header = ui.PageHeader(
            self._body, title="Analytics",
            breadcrumb=["Workspace", "Analytics"],
            subtitle="Track your progress and performance across categories.",
        )
        header.pack(fill="x")

        done_count = sum(1 for t in tasks if t.status == "Done")
        if done_count == 0:
            ui.EmptyState(
                self._body,
                title="No completed tasks yet",
                subtitle="Finish a task and its performance will show up here.",
            ).pack(fill="x", pady=theme.SPACE_3XL)
            return

        self._build_metric_row(tasks)
        self._build_velocity_section(tasks)
        self._build_performance_table(tasks)

    # ── Metrics ──────────────────────────────────────────────────────────────

    def _build_metric_row(self, tasks):
        row = ctk.CTkFrame(self._body, fg_color="transparent")
        row.pack(fill="x", pady=(theme.SPACE_2XL, 0))

        metrics = [
            ("Total Time", _format_minutes(analytics.get_total_time_minutes(tasks))),
            ("Tasks Completed", str(sum(1 for t in tasks if t.status == "Done"))),
            ("Completion Rate", f"{analytics.get_completion_rate(tasks)}%"),
            ("Current Streak", f"{analytics.get_streak(tasks)} days"),
        ]

        for i, (label, value) in enumerate(metrics):
            col = ctk.CTkFrame(row, fg_color="transparent")
            col.pack(side="left", fill="x", expand=True, padx=(0 if i == 0 else theme.SPACE_LG, 0))
            ctk.CTkLabel(
                col, text=label, font=theme.FONT_META(), text_color=theme.TEXT_MUTED, anchor="w",
            ).pack(anchor="w")
            ctk.CTkLabel(
                col, text=value, font=theme.font(24, "bold"), text_color=theme.TEXT, anchor="w",
            ).pack(anchor="w", pady=(2, 0))

        ui.Divider(self._body, pady=(theme.SPACE_2XL, 0))

    # ── Weekly velocity chart ────────────────────────────────────────────────

    def _build_velocity_section(self, tasks):
        wrap = ctk.CTkFrame(self._body, fg_color="transparent")
        wrap.pack(fill="x", pady=(theme.SPACE_2XL, 0))

        ui.SectionLabel(wrap, "Time Tracked")
        card = ui.Card(wrap)
        card.pack(fill="x")

        velocity = analytics.get_weekly_velocity(tasks, weeks=8)
        labels = [f"W{i+1}" for i in range(len(velocity))]
        ui.bar_chart(card, velocity, labels=labels, width=760, height=140).pack(
            fill="x", padx=theme.SPACE_LG, pady=theme.SPACE_LG
        )

    # ── Category performance table ──────────────────────────────────────────

    def _build_performance_table(self, tasks):
        wrap = ctk.CTkFrame(self._body, fg_color="transparent")
        wrap.pack(fill="x", pady=(theme.SPACE_2XL, 0))

        ui.SectionLabel(wrap, "Task Performance")

        performance = analytics.get_category_performance(tasks)
        rows = []
        for category, stats in sorted(performance.items(), key=lambda kv: -kv[1]["completed"]):
            rows.append([category, str(stats["completed"]), _format_minutes(stats["time_minutes"])])

        ui.Table(wrap, ["Category", "Completed", "Time"], rows, weights=[2, 1, 1])
