"""
views/dashboard.py — Dashboard panel (compact, always-visible right column)
=============================================================================
Reads tasks from storage, passes them to analytics, displays results.

Call chain:  DashboardPanel → analytics.py functions → storage.load_tasks()

This view is READ-ONLY. It never calls storage.save_task() or any write
function directly (Quick Add opens the same TaskModal every other entry
point uses). The panel just observes — it never mutates.

Refresh mechanism
-----------------
A "Refresh" button, plus main.py calling refresh() whenever the panel is
toggled visible, ensure it reflects the current state of tasks.json.
"""

import customtkinter as ctk
import tkinter as tk
import storage
import theme
from models import analytics

RING_SIZE = 96
RING_THICKNESS = 9

WEEKLY_STREAK_GOAL = 7


class DashboardPanel(ctk.CTkFrame):

    WIDTH = 340

    def __init__(self, parent):
        super().__init__(parent, width=self.WIDTH, fg_color=theme.PANEL, corner_radius=0)
        self.pack_propagate(False)
        self._build_static_layout()
        self.refresh()

    # ── Static layout (built once) ──────────────────────────────────────────

    def _build_static_layout(self):
        self._scroll = ctk.CTkScrollableFrame(
            self, fg_color=theme.PANEL, scrollbar_button_color=theme.BORDER,
        )
        self._scroll.pack(fill="both", expand=True, padx=theme.SPACE_LG, pady=theme.SPACE_LG)

        header = ctk.CTkFrame(self._scroll, fg_color="transparent")
        header.pack(fill="x", pady=(0, theme.SPACE_LG))

        ctk.CTkLabel(
            header, text="Dashboard",
            font=theme.font(18, "bold"), text_color=theme.TEXT,
        ).pack(side="left")

        ctk.CTkButton(
            header, text="↻",
            width=28, height=28, corner_radius=8,
            fg_color=theme.CARD, hover_color=theme.CARD_HOVER,
            text_color=theme.TEXT_SECONDARY,
            font=theme.FONT_BODY(),
            command=self.refresh,
        ).pack(side="right")

        # ── Row 1: Streak + Completion ───────────────────────────────────────
        row1 = ctk.CTkFrame(self._scroll, fg_color="transparent")
        row1.pack(fill="x", pady=(0, theme.SPACE_LG))

        self._streak_card = self._streak_widget(row1)
        self._ring_canvas = self._completion_widget(row1)

        # ── Row 2: Status overview ───────────────────────────────────────────
        self._section_label(self._scroll, "STATUS OVERVIEW")

        grid = ctk.CTkFrame(self._scroll, fg_color="transparent")
        grid.pack(fill="x", pady=(0, theme.SPACE_LG))
        grid.grid_columnconfigure((0, 1), weight=1)

        self._status_cards: dict[str, ctk.CTkLabel] = {}
        for i, status in enumerate(theme.STATUS):
            r, c = divmod(i, 2)
            tile, value_label = self._status_tile(grid, status)
            tile.grid(row=r, column=c, sticky="nsew", padx=(0 if c == 0 else 5, 5 if c == 0 else 0), pady=5)
            self._status_cards[status] = value_label

        # ── Row 3: Insights ──────────────────────────────────────────────────
        self._section_label(self._scroll, "INSIGHTS")

        self._skill_card = self._insight_card(self._scroll, "🛠", "Most Active Skill")
        self._due_card   = self._insight_card(self._scroll, "📅", "Due Today")

        # ── Row 4: XP / Level ────────────────────────────────────────────────
        self._section_label(self._scroll, "XP")
        self._xp_card = self._xp_widget(self._scroll)

        # ── Row 5: Quick add ─────────────────────────────────────────────────
        ctk.CTkFrame(self._scroll, height=1, fg_color=theme.BORDER).pack(
            fill="x", pady=(theme.SPACE_SM, theme.SPACE_LG)
        )

        ctk.CTkButton(
            self._scroll,
            text="+  Quick Add Task",
            height=40, corner_radius=10,
            fg_color=theme.PRIMARY, hover_color=theme.PRIMARY_HOVER,
            text_color="#FFFFFF",
            font=theme.font(13, "bold"),
            command=self._open_add_modal,
        ).pack(fill="x")

    # ── Widget builders ──────────────────────────────────────────────────────

    def _section_label(self, parent, text):
        ctk.CTkLabel(
            parent, text=text,
            font=theme.font(11, "bold"), text_color=theme.TEXT_MUTED,
        ).pack(anchor="w", pady=(0, theme.SPACE_SM))

    def _card(self, parent):
        return ctk.CTkFrame(
            parent, fg_color=theme.CARD, corner_radius=12,
            border_width=1, border_color=theme.BORDER,
        )

    def _streak_widget(self, parent):
        card = self._card(parent)
        card.pack(side="left", fill="both", expand=True, padx=(0, theme.SPACE_SM))

        ctk.CTkLabel(
            card, text="🔥  Day Streak",
            font=theme.FONT_META(), text_color=theme.TEXT_MUTED,
        ).pack(anchor="w", padx=theme.SPACE_MD, pady=(theme.SPACE_MD, 0))

        value_lbl = ctk.CTkLabel(
            card, text="—",
            font=theme.font(32, "bold"), text_color=theme.PRIMARY,
        )
        value_lbl.pack(anchor="w", padx=theme.SPACE_MD)

        progress = ctk.CTkProgressBar(
            card, width=1, height=6, corner_radius=3,
            fg_color=theme.BORDER, progress_color=theme.PRIMARY,
        )
        progress.pack(fill="x", padx=theme.SPACE_MD, pady=(theme.SPACE_XS, theme.SPACE_MD))
        progress.set(0)

        card.value_label = value_lbl
        card.progress_bar = progress
        return card

    def _completion_widget(self, parent):
        card = self._card(parent)
        card.pack(side="left", fill="both", expand=True)

        ctk.CTkLabel(
            card, text="◷  Completion",
            font=theme.FONT_META(), text_color=theme.TEXT_MUTED,
        ).pack(anchor="w", padx=theme.SPACE_MD, pady=(theme.SPACE_MD, theme.SPACE_XS))

        canvas = tk.Canvas(
            card, width=RING_SIZE, height=RING_SIZE,
            bg=theme.CARD, highlightthickness=0,
        )
        canvas.pack(padx=theme.SPACE_MD, pady=(0, theme.SPACE_MD))

        return canvas

    def _draw_ring(self, rate: int):
        canvas = self._ring_canvas
        canvas.delete("all")
        pad = RING_THICKNESS / 2 + 2
        bbox = (pad, pad, RING_SIZE - pad, RING_SIZE - pad)
        canvas.create_oval(*bbox, outline=theme.BORDER, width=RING_THICKNESS)
        if rate > 0:
            canvas.create_arc(
                *bbox, start=90, extent=-(rate / 100) * 360,
                style="arc", outline=theme.SUCCESS, width=RING_THICKNESS,
            )
        canvas.create_text(
            RING_SIZE / 2, RING_SIZE / 2, text=f"{rate}%",
            fill=theme.TEXT, font=(theme.FONT_FAMILY, 16, "bold"),
        )

    def _status_tile(self, parent, status: str):
        info = theme.STATUS[status]
        frame = self._card(parent)

        value_lbl = ctk.CTkLabel(
            frame, text="0",
            font=theme.font(22, "bold"), text_color=info["color"],
        )
        value_lbl.pack(pady=(theme.SPACE_SM, 0))

        ctk.CTkLabel(
            frame, text=f"{info['icon']} {status}",
            font=theme.FONT_META(), text_color=theme.TEXT_MUTED,
        ).pack(pady=(0, theme.SPACE_SM))

        return frame, value_lbl

    def _insight_card(self, parent, icon: str, label: str):
        frame = self._card(parent)
        frame.pack(fill="x", pady=(0, theme.SPACE_SM))

        ctk.CTkLabel(
            frame, text=f"{icon}  {label}",
            font=theme.FONT_META(), text_color=theme.TEXT_MUTED,
        ).pack(anchor="w", padx=theme.SPACE_MD, pady=(theme.SPACE_MD, theme.SPACE_XS))

        value_lbl = ctk.CTkLabel(
            frame, text="—",
            font=theme.font(16, "bold"), text_color=theme.TEXT,
        )
        value_lbl.pack(anchor="w", padx=theme.SPACE_MD, pady=(0, theme.SPACE_MD))

        return value_lbl

    def _xp_widget(self, parent):
        frame = self._card(parent)
        frame.pack(fill="x", pady=(0, theme.SPACE_LG))

        top = ctk.CTkFrame(frame, fg_color="transparent")
        top.pack(fill="x", padx=theme.SPACE_MD, pady=(theme.SPACE_MD, theme.SPACE_XS))

        level_lbl = ctk.CTkLabel(
            top, text="LEVEL —",
            font=theme.font(12, "bold"), text_color=theme.PRIMARY,
        )
        level_lbl.pack(side="left")

        xp_lbl = ctk.CTkLabel(
            top, text="",
            font=theme.FONT_META(), text_color=theme.TEXT_MUTED,
        )
        xp_lbl.pack(side="right")

        progress = ctk.CTkProgressBar(
            frame, width=1, height=6, corner_radius=3,
            fg_color=theme.BORDER, progress_color=theme.PRIMARY,
        )
        progress.pack(fill="x", padx=theme.SPACE_MD)
        progress.set(0)

        legend = ctk.CTkLabel(
            frame,
            text=(
                f"Easy +{analytics.XP_BY_DIFFICULTY['Easy']} XP   "
                f"Medium +{analytics.XP_BY_DIFFICULTY['Medium']} XP   "
                f"Hard +{analytics.XP_BY_DIFFICULTY['Hard']} XP"
            ),
            font=theme.FONT_META(), text_color=theme.TEXT_MUTED,
        )
        legend.pack(anchor="w", padx=theme.SPACE_MD, pady=(theme.SPACE_SM, theme.SPACE_MD))

        frame.level_label = level_lbl
        frame.xp_label = xp_lbl
        frame.progress_bar = progress
        return frame

    # ── Refresh — recompute all values from disk ────────────────────────────

    def refresh(self):
        tasks = storage.load_tasks()

        streak = analytics.get_streak(tasks)
        self._streak_card.value_label.configure(text=str(streak))
        self._streak_card.progress_bar.set(min(streak / WEEKLY_STREAK_GOAL, 1.0))

        rate = analytics.get_completion_rate(tasks)
        self._draw_ring(rate)

        counts = analytics.get_status_counts(tasks)
        for status, label in self._status_cards.items():
            label.configure(text=str(counts.get(status, 0)))

        skill = analytics.get_most_active_skill(tasks)
        self._skill_card.configure(text=skill)

        due = analytics.get_due_today(tasks)
        self._due_card.configure(text=str(len(due)) if due else "None")

        total_xp = sum(analytics.get_skill_xp(tasks).values())
        level, xp_into, xp_needed = analytics.get_level_progress(total_xp)
        self._xp_card.level_label.configure(text=f"LEVEL {level}")
        self._xp_card.xp_label.configure(text=f"{xp_into} / {xp_needed} XP")
        self._xp_card.progress_bar.set(xp_into / xp_needed)

    # ── Quick add ─────────────────────────────────────────────────────────────

    def _open_add_modal(self):
        from views.task_modal import TaskModal
        TaskModal(self, task=None, on_save=self.refresh)
