"""
DevLog — App Shell
======================
Sidebar + Header + a single-page-at-a-time router (Overview, Board,
Analytics, Projects, Settings). Every page shares the Sidebar/Header shell
and the views.components.ui design system.
"""

import customtkinter as ctk
import tkinter as tk
from pathlib import Path
import theme
import storage
import settings_store
from models import analytics
from views.sidebar import Sidebar
from views.header import Header
from views.board import BoardView
from views.overview import OverviewPage
from views.analytics import AnalyticsView
from views.projects import ProjectsView
from views.settings import SettingsView

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")


class DevLogApp(ctk.CTk):

    def __init__(self):
        super().__init__()
        self._base_dir = Path(__file__).resolve().parent
        self.title("DevLog")
        self.after(200, self._set_icon)
        self.geometry("1440x820")
        self.minsize(1300, 680)
        self.configure(fg_color=theme.BG)

        self._settings = settings_store.load_settings()
        self._search_var = ctk.StringVar(value="")
        self._current_page: str | None = None

        self._build_shell()
        self._build_pages()
        self._bind_shortcuts()

        self._apply_settings(self._settings)
        self._show_page("overview")

    def _set_icon(self):
        try:
            self.iconbitmap(str(self._base_dir / "devlog.ico"))
        except Exception:
            pass

    # ── Shell ─────────────────────────────────────────────────────────────────

    def _build_shell(self):
        self._sidebar = Sidebar(
            self,
            on_nav=self._show_page,
            on_category=self._open_project,
            on_settings=lambda: self._show_page("settings"),
        )
        self._sidebar.pack(side="left", fill="y")

        main_area = ctk.CTkFrame(self, fg_color=theme.BG, corner_radius=0)
        main_area.pack(side="left", fill="both", expand=True)

        self._header = Header(
            main_area, search_var=self._search_var,
            on_search_submit=lambda: self._show_page("board"),
        )
        self._header.pack(side="top", fill="x")

        self._page_area = ctk.CTkFrame(main_area, fg_color=theme.BG, corner_radius=0)
        self._page_area.pack(side="top", fill="both", expand=True)

    def _build_pages(self):
        self._pages = {
            "overview": OverviewPage(
                self._page_area, weekly_streak_goal=self._settings["weekly_streak_goal"],
            ),
            "board": BoardView(
                self._page_area, search_var=self._search_var,
                default_view=self._settings["default_board_view"],
            ),
            "analytics": AnalyticsView(self._page_area),
            "projects": ProjectsView(
                self._page_area, on_category_change=self._on_project_category_change,
            ),
            "settings": SettingsView(self._page_area, on_settings_saved=self._apply_settings),
        }

    # ── Navigation ────────────────────────────────────────────────────────────

    def _show_page(self, key: str, category: str | None = None):
        if key not in self._pages:
            return

        if key != self._current_page:
            if self._current_page:
                self._pages[self._current_page].pack_forget()
            self._pages[key].pack(fill="both", expand=True)
            self._current_page = key

        self._refresh_page(key, category=category)

        if category:
            self._sidebar.set_active_category(category)
        else:
            self._sidebar.set_active(key)
        self._refresh_streak()

    def _refresh_page(self, key: str, category: str | None = None):
        page = self._pages[key]
        if key == "overview":
            page.refresh(display_name=self._settings["display_name"])
        elif key == "projects":
            if category:
                page.show_category(category)
            else:
                page.show_list()
        elif hasattr(page, "refresh"):
            page.refresh()

    def _open_project(self, category: str):
        self._show_page("projects", category=category)

    def _on_project_category_change(self, category: str | None):
        """Keeps the sidebar in sync when navigation happens inside the Projects page itself."""
        if category:
            self._sidebar.set_active_category(category)
        else:
            self._sidebar.set_active("projects")

    # ── Settings propagation ─────────────────────────────────────────────────

    def _apply_settings(self, settings: dict):
        self._settings = settings
        self._sidebar.set_user(settings["display_name"], settings["role"])
        self._header.set_user(settings["display_name"], settings["role"])
        self._pages["overview"].set_display_name(settings["display_name"])
        self._pages["overview"].set_weekly_streak_goal(settings["weekly_streak_goal"])
        self._pages["board"].set_view_mode(settings["default_board_view"])
        self._refresh_streak()

    def _refresh_streak(self):
        streak = analytics.get_streak(storage.load_tasks())
        self._sidebar.set_streak(streak, self._settings["weekly_streak_goal"])

    # ── Global keyboard shortcuts ────────────────────────────────────────────

    def _bind_shortcuts(self):
        self.bind_all("<KeyPress>", self._handle_shortcut, add="+")

    def _handle_shortcut(self, event):
        if isinstance(event.widget, (tk.Entry, tk.Text)):
            return
        key = event.keysym.lower()
        if key == "n":
            self._open_quick_add()
        elif key == "slash":
            self._header.focus_search()
        elif key == "b":
            self._show_page("board")
        elif key == "o":
            self._show_page("overview")
        elif key == "a":
            self._show_page("analytics")
        elif key == "escape":
            self.focus_set()

    def _open_quick_add(self):
        from views.task_modal import TaskModal
        TaskModal(self, task=None, on_save=self._on_task_changed)

    def _on_task_changed(self):
        if self._current_page:
            self._refresh_page(self._current_page)
        self._refresh_streak()


if __name__ == "__main__":
    app = DevLogApp()
    app.mainloop()
