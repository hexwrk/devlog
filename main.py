"""
DevLog — Phase 2 & 3 App Shell
"""

import customtkinter as ctk
from PIL import Image
from views.board import BoardView
from views.dashboard import DashboardView

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

ACCENT        = "#7C5CFC"
SIDEBAR_BG    = "#111111"
MAIN_BG       = "#161616"
TEXT_PRIMARY  = "#F5F5F7"
TEXT_MUTED    = "#6E6E73"
DIVIDER       = "#2C2C2E"


class StatsView(ctk.CTkFrame):
    def __init__(self, parent):
        super().__init__(parent, fg_color=MAIN_BG)
        frame = ctk.CTkFrame(self, fg_color="transparent")
        frame.pack(fill="both", expand=True, padx=32, pady=28)
        ctk.CTkLabel(
            frame, text="Stats",
            font=ctk.CTkFont(family="Segoe UI", size=28, weight="bold"),
            text_color=TEXT_PRIMARY,
        ).pack(anchor="w")
        ctk.CTkFrame(frame, height=1, fg_color=DIVIDER).pack(fill="x", pady=(12, 24))
        ctk.CTkLabel(
            frame,
            text="Progress graphs and skill breakdowns coming in Phase 4.",
            font=ctk.CTkFont(family="Segoe UI", size=14),
            text_color=TEXT_MUTED,
        ).pack(anchor="w")


class DevLogApp(ctk.CTk):

    SIDEBAR_WIDTH = 210
    NAV_ITEMS = [
        ("Board",     "board",     "📋"),
        ("Dashboard", "dashboard", "📊"),
        ("Stats",     "stats",     "📈"),
    ]

    def __init__(self):
        super().__init__()
        self.title("DevLog")
        self.after(200, lambda: self.iconbitmap("devlog.ico"))
        self.geometry("1100x700")
        self.minsize(900, 600)
        self.configure(fg_color=MAIN_BG)

        self._board_bg_raw   = None
        self._sidebar_bg_raw = None

        self._build_sidebar()
        self._build_main_area()

        self._views: dict[str, ctk.CTkFrame] = {
            "board":     BoardView(self._main_area),
            "dashboard": DashboardView(self._main_area),
            "stats":     StatsView(self._main_area),
        }

        self._current_view: str | None = None
        self._show_view("board")

    # ── Sidebar ───────────────────────────────────────────────────────────────

    def _build_sidebar(self):
        self._sidebar = ctk.CTkFrame(
            self, width=self.SIDEBAR_WIDTH,
            fg_color=SIDEBAR_BG, corner_radius=0,
        )
        self._sidebar.pack(side="left", fill="y")
        self._sidebar.pack_propagate(False)

        # Responsive sidebar background image
        try:
            self._sidebar_bg_raw = Image.open("sidebar_bg.png")
            self._sidebar_bg_label = ctk.CTkLabel(self._sidebar, text="")
            self._sidebar_bg_label.place(x=0, y=0, relwidth=1, relheight=1)
            self._sidebar.bind("<Configure>", self._resize_sidebar_bg)
        except Exception:
            pass

        # Logo
        logo_frame = ctk.CTkFrame(self._sidebar, fg_color="transparent")
        logo_frame.pack(fill="x", padx=20, pady=(28, 32))

        ctk.CTkLabel(
            logo_frame, text="DevLog",
            font=ctk.CTkFont(family="Segoe UI", size=20, weight="bold"),
            text_color=TEXT_PRIMARY,
        ).pack(side="left")

        ctk.CTkLabel(
            logo_frame, text="●",
            font=ctk.CTkFont(size=8),
            text_color=ACCENT,
        ).pack(side="left", padx=(4, 0), pady=(4, 0))

        ctk.CTkLabel(
            self._sidebar, text="MENU",
            font=ctk.CTkFont(family="Segoe UI", size=10, weight="bold"),
            text_color=TEXT_MUTED,
        ).pack(anchor="w", padx=20, pady=(0, 8))

        self._nav_buttons: dict[str, ctk.CTkButton] = {}

        for label, key, icon in self.NAV_ITEMS:
            btn = ctk.CTkButton(
                self._sidebar,
                text=f"  {icon}  {label}",
                anchor="w",
                height=42,
                corner_radius=10,
                fg_color="#1C1C1E",
                hover_color="#2A2A2C",
                text_color=TEXT_MUTED,
                font=ctk.CTkFont(family="Segoe UI", size=14),
                command=lambda k=key: self._show_view(k),
            )
            btn.pack(fill="x", padx=12, pady=2)
            self._nav_buttons[key] = btn

        ctk.CTkLabel(
            self._sidebar, text="v0.2.0",
            font=ctk.CTkFont(family="Segoe UI", size=11),
            text_color=TEXT_MUTED,
        ).pack(side="bottom", pady=20)

        ctk.CTkFrame(
            self, width=1, fg_color=DIVIDER, corner_radius=0
        ).pack(side="left", fill="y")

    def _resize_sidebar_bg(self, event):
        try:
            w, h = event.width, event.height
            if w < 10 or h < 10:
                return
            resized = self._sidebar_bg_raw.resize((w, h), Image.LANCZOS)
            self._sidebar_bg_ctk = ctk.CTkImage(resized, size=(w, h))
            self._sidebar_bg_label.configure(image=self._sidebar_bg_ctk)
        except Exception:
            pass

    # ── Main area ─────────────────────────────────────────────────────────────

    def _build_main_area(self):
        self._main_area = ctk.CTkFrame(self, fg_color=MAIN_BG, corner_radius=0)
        self._main_area.pack(side="left", fill="both", expand=True)

        # Responsive board background image
        try:
            self._board_bg_raw = Image.open("board_bg.png")
            self._board_bg_label = ctk.CTkLabel(self._main_area, text="")
            self._board_bg_label.place(x=0, y=0, relwidth=1, relheight=1)
            self._main_area.bind("<Configure>", self._resize_board_bg)
        except Exception:
            pass

    def _resize_board_bg(self, event):
        try:
            w, h = event.width, event.height
            if w < 10 or h < 10:
                return
            resized = self._board_bg_raw.resize((w, h), Image.LANCZOS)
            self._board_bg_ctk = ctk.CTkImage(resized, size=(w, h))
            self._board_bg_label.configure(image=self._board_bg_ctk)
        except Exception:
            pass

    # ── View switching ────────────────────────────────────────────────────────

    def _show_view(self, key: str):
        if key == self._current_view:
            return
        if self._current_view:
            self._views[self._current_view].pack_forget()
            self._nav_buttons[self._current_view].configure(
                fg_color="#1C1C1E", text_color=TEXT_MUTED
            )
        self._views[key].pack(fill="both", expand=True)
        self._nav_buttons[key].configure(fg_color=ACCENT, text_color="#FFFFFF")
        self._current_view = key
        if key == "dashboard":
            self._views["dashboard"].refresh()


if __name__ == "__main__":
    app = DevLogApp()
    app.mainloop()
