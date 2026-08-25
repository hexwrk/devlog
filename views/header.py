"""
views/header.py — Global application header
===============================================
An integrated search field + notifications + user block, shared by every
page instead of each page building its own top bar. Each page's own
breadcrumb/title lives in its body via views.components.ui.PageHeader
(see e.g. views/board.py) — the global header stays uncluttered.
"""

from typing import Callable
import customtkinter as ctk
import theme

HEADER_HEIGHT = 56


class Header(ctk.CTkFrame):

    def __init__(
        self,
        parent,
        search_var: ctk.StringVar,
        on_search_submit: Callable[[], None],
    ):
        super().__init__(parent, height=HEADER_HEIGHT, fg_color=theme.SIDEBAR, corner_radius=0)
        self.pack_propagate(False)

        user = ctk.CTkFrame(self, fg_color="transparent")
        user.pack(side="right", padx=theme.SPACE_XL)

        self._avatar = ctk.CTkLabel(
            user, text="TJ",
            width=30, height=30, corner_radius=15,
            fg_color=theme.PRIMARY, text_color="#FFFFFF",
            font=theme.font(11, "bold"),
        )
        self._avatar.pack(side="right")

        name_col = ctk.CTkFrame(user, fg_color="transparent")
        name_col.pack(side="right", padx=(0, theme.SPACE_SM))
        self._name_label = ctk.CTkLabel(
            name_col, text="Tristan",
            font=theme.font(12, "bold"), text_color=theme.TEXT, anchor="e",
        )
        self._name_label.pack(anchor="e")
        self._role_label = ctk.CTkLabel(
            name_col, text="Student",
            font=theme.font(10), text_color=theme.TEXT_MUTED, anchor="e",
        )
        self._role_label.pack(anchor="e")

        ctk.CTkLabel(
            user, text=theme.icon("bell"),
            font=theme.font(theme.ICON_SIZE_NAV), text_color=theme.TEXT_SECONDARY,
        ).pack(side="right", padx=theme.SPACE_XL)

        search_wrap = ctk.CTkFrame(self, fg_color=theme.PANEL, corner_radius=theme.RADIUS_SM)
        search_wrap.pack(side="right", pady=(theme.SPACE_MD - 2, theme.SPACE_MD - 2))

        ctk.CTkLabel(
            search_wrap, text=theme.icon("search"),
            font=theme.font(12), text_color=theme.TEXT_MUTED,
        ).pack(side="left", padx=(theme.SPACE_SM, 0))

        search = ctk.CTkEntry(
            search_wrap, placeholder_text="Search tasks, projects...",
            width=240, height=32, corner_radius=theme.RADIUS_SM,
            fg_color="transparent", border_width=0,
            text_color=theme.TEXT, font=theme.FONT_BODY(),
            textvariable=search_var,
        )
        search.pack(side="left", padx=(theme.SPACE_XS, theme.SPACE_SM))
        search.bind("<Return>", lambda e: on_search_submit())
        self._search_entry = search

    def set_user(self, display_name: str, role: str):
        first_name = display_name.split()[0] if display_name.split() else display_name
        self._name_label.configure(text=first_name)
        self._role_label.configure(text=role)
        initials = "".join(part[0] for part in display_name.split()[:2]).upper() or "?"
        self._avatar.configure(text=initials)

    def focus_search(self):
        self._search_entry.focus_set()
