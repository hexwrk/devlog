"""
DevLog — App Shell
"""

import customtkinter as ctk
from pathlib import Path
import theme
import storage
from models import CATEGORIES, analytics
from views.board import BoardView
from views.dashboard import DashboardPanel
from views.stats import StatsView

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

SIDEBAR_WIDTH = 250
TOPBAR_HEIGHT = 56
WEEKLY_STREAK_GOAL = 7


class DevLogApp(ctk.CTk):

    NAV_ITEMS = [
        ("Board",     "board",     "▣"),
        ("Dashboard", "dashboard", "▥"),
        ("Stats",     "stats",     "▥"),
    ]

    def __init__(self):
        super().__init__()
        self._base_dir = Path(__file__).resolve().parent
        self.title("DevLog")
        self.after(200, self._set_icon)
        self.geometry("1440x820")
        self.minsize(1300, 680)
        self.configure(fg_color=theme.BG)

        self._search_var = ctk.StringVar(value="")

        self._build_topbar()
        self._build_body()

        self._center_views: dict[str, ctk.CTkFrame] = {
            "board": BoardView(self._center_area, search_var=self._search_var),
            "stats": StatsView(self._center_area),
        }

        self._current_center: str | None = None
        self._dashboard_visible = True
        self._show_center("board")
        self._refresh_sidebar_streak()

    # ── Top bar ───────────────────────────────────────────────────────────────

    def _build_topbar(self):
        bar = ctk.CTkFrame(self, height=TOPBAR_HEIGHT, fg_color=theme.SIDEBAR, corner_radius=0)
        bar.pack(side="top", fill="x")
        bar.pack_propagate(False)

        ctk.CTkLabel(
            bar, text="⚡ DevLog",
            font=theme.font(16, "bold"), text_color=theme.TEXT,
        ).pack(side="left", padx=theme.SPACE_LG)

        user = ctk.CTkFrame(bar, fg_color="transparent")
        user.pack(side="right", padx=theme.SPACE_LG)

        avatar = ctk.CTkLabel(
            user, text="TJ",
            width=32, height=32, corner_radius=16,
            fg_color=theme.PRIMARY, text_color="#FFFFFF",
            font=theme.font(12, "bold"),
        )
        avatar.pack(side="right")

        name_col = ctk.CTkFrame(user, fg_color="transparent")
        name_col.pack(side="right", padx=(0, theme.SPACE_SM))
        ctk.CTkLabel(
            name_col, text="Tristan",
            font=theme.font(12, "bold"), text_color=theme.TEXT, anchor="e",
        ).pack(anchor="e")
        ctk.CTkLabel(
            name_col, text="Student",
            font=theme.font(10), text_color=theme.TEXT_MUTED, anchor="e",
        ).pack(anchor="e")

        ctk.CTkLabel(
            user, text="🔔",
            font=theme.font(15), text_color=theme.TEXT_SECONDARY,
        ).pack(side="right", padx=theme.SPACE_LG)

        search = ctk.CTkEntry(
            bar, placeholder_text="Search tasks...",
            width=260, height=34, corner_radius=8,
            fg_color=theme.PANEL, border_color=theme.BORDER,
            text_color=theme.TEXT, font=theme.FONT_BODY(),
            textvariable=self._search_var,
        )
        search.pack(side="right", padx=theme.SPACE_LG)

    # ── Body: sidebar | center | dashboard panel ─────────────────────────────

    def _build_body(self):
        body = ctk.CTkFrame(self, fg_color=theme.BG, corner_radius=0)
        body.pack(side="top", fill="both", expand=True)

        self._build_sidebar(body)

        self._dashboard_panel = DashboardPanel(body)
        self._dashboard_panel.pack(side="right", fill="y")

        self._center_area = ctk.CTkFrame(body, fg_color=theme.BG, corner_radius=0)
        self._center_area.pack(side="left", fill="both", expand=True)

    # ── Sidebar ───────────────────────────────────────────────────────────────

    def _build_sidebar(self, body):
        self._sidebar = ctk.CTkFrame(
            body, width=SIDEBAR_WIDTH,
            fg_color=theme.SIDEBAR, corner_radius=0,
        )
        self._sidebar.pack(side="left", fill="y")
        self._sidebar.pack_propagate(False)

        ctk.CTkFrame(self._sidebar, height=1, fg_color=theme.BORDER).pack(fill="x")

        ctk.CTkLabel(
            self._sidebar, text="MENU",
            font=theme.font(10, "bold"), text_color=theme.TEXT_MUTED,
        ).pack(anchor="w", padx=theme.SPACE_XL, pady=(theme.SPACE_XL, theme.SPACE_SM))

        self._nav_buttons: dict[str, ctk.CTkButton] = {}
        for label, key, icon in self.NAV_ITEMS:
            btn = ctk.CTkButton(
                self._sidebar,
                text=f"  {icon}   {label}",
                anchor="w",
                height=38, corner_radius=8,
                fg_color="transparent",
                hover_color=theme.PANEL,
                text_color=theme.TEXT_SECONDARY,
                font=theme.FONT_BODY(),
                command=lambda k=key: self._handle_nav_click(k),
            )
            btn.pack(fill="x", padx=theme.SPACE_MD, pady=2)
            self._nav_buttons[key] = btn

        ctk.CTkLabel(
            self._sidebar, text="PROJECTS",
            font=theme.font(10, "bold"), text_color=theme.TEXT_MUTED,
        ).pack(anchor="w", padx=theme.SPACE_XL, pady=(theme.SPACE_XL, theme.SPACE_SM))

        for category in CATEGORIES:
            colour = theme.CATEGORY_COLOURS.get(category, theme.TEXT_MUTED)
            row = ctk.CTkButton(
                self._sidebar,
                text=f"  ●   {category}",
                anchor="w",
                height=32, corner_radius=8,
                fg_color="transparent",
                hover_color=theme.PANEL,
                text_color=colour,
                font=theme.FONT_BODY(),
                command=lambda c=category: self._filter_by_category(c),
            )
            row.pack(fill="x", padx=theme.SPACE_MD, pady=1)

        self._build_consistency_card()

        ctk.CTkLabel(
            self._sidebar, text="🌙  Dark",
            font=theme.FONT_META(), text_color=theme.TEXT_MUTED,
        ).pack(side="bottom", anchor="w", padx=theme.SPACE_XL, pady=theme.SPACE_LG)

    def _build_consistency_card(self):
        card = ctk.CTkFrame(
            self._sidebar, fg_color=theme.CARD, corner_radius=12,
            border_width=1, border_color=theme.BORDER,
        )
        card.pack(side="bottom", fill="x", padx=theme.SPACE_LG, pady=(theme.SPACE_LG, 0))

        ctk.CTkLabel(
            card, text="⚡ Stay Consistent",
            font=theme.font(12, "bold"), text_color=theme.TEXT,
        ).pack(anchor="w", padx=theme.SPACE_MD, pady=(theme.SPACE_MD, theme.SPACE_XS))

        ctk.CTkLabel(
            card, text="Small daily progress leads to big results.",
            font=theme.FONT_META(), text_color=theme.TEXT_MUTED,
            wraplength=SIDEBAR_WIDTH - 2 * theme.SPACE_LG - 2 * theme.SPACE_MD,
            justify="left",
        ).pack(anchor="w", padx=theme.SPACE_MD)

        self._streak_days_label = ctk.CTkLabel(
            card, text="— / 7 days",
            font=theme.FONT_META(), text_color=theme.TEXT_SECONDARY,
        )
        self._streak_days_label.pack(anchor="w", padx=theme.SPACE_MD, pady=(theme.SPACE_SM, theme.SPACE_XS))

        self._streak_progress = ctk.CTkProgressBar(
            card, width=1, height=6, corner_radius=3,
            fg_color=theme.BORDER, progress_color=theme.PRIMARY,
        )
        self._streak_progress.pack(fill="x", padx=theme.SPACE_MD, pady=(0, theme.SPACE_MD))
        self._streak_progress.set(0)

    def _refresh_sidebar_streak(self):
        streak = analytics.get_streak(storage.load_tasks())
        self._streak_days_label.configure(text=f"{streak} / {WEEKLY_STREAK_GOAL} days")
        self._streak_progress.set(min(streak / WEEKLY_STREAK_GOAL, 1.0))

    def _filter_by_category(self, category: str):
        self._show_center("board")
        self._center_views["board"].set_category_filter(category)

    # ── Nav / view switching ──────────────────────────────────────────────────

    def _set_icon(self):
        try:
            self.iconbitmap(str(self._base_dir / "devlog.ico"))
        except Exception:
            pass

    def _handle_nav_click(self, key: str):
        if key == "dashboard":
            self._toggle_dashboard_panel()
        else:
            self._show_center(key)

    def _show_center(self, key: str):
        if key != self._current_center:
            if self._current_center:
                self._center_views[self._current_center].pack_forget()
                self._nav_buttons[self._current_center].configure(
                    fg_color="transparent", text_color=theme.TEXT_SECONDARY
                )
            self._center_views[key].pack(fill="both", expand=True)
            self._nav_buttons[key].configure(fg_color=theme.PRIMARY, text_color="#FFFFFF")
            self._current_center = key
        self._update_dashboard_nav_style()

    def _toggle_dashboard_panel(self):
        self._dashboard_visible = not self._dashboard_visible
        if self._dashboard_visible:
            self._dashboard_panel.pack(side="right", fill="y")
            self._dashboard_panel.refresh()
            self._refresh_sidebar_streak()
        else:
            self._dashboard_panel.pack_forget()
        self._update_dashboard_nav_style()

    def _update_dashboard_nav_style(self):
        active = self._dashboard_visible
        self._nav_buttons["dashboard"].configure(
            fg_color=theme.PRIMARY if active else "transparent",
            text_color="#FFFFFF" if active else theme.TEXT_SECONDARY,
        )


if __name__ == "__main__":
    app = DevLogApp()
    app.mainloop()
