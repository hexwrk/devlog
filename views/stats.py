"""
views/stats.py — Stats placeholder view
"""

import customtkinter as ctk
import theme


class StatsView(ctk.CTkFrame):
    def __init__(self, parent):
        super().__init__(parent, fg_color=theme.BG)
        frame = ctk.CTkFrame(self, fg_color="transparent")
        frame.pack(fill="both", expand=True, padx=theme.SPACE_3XL, pady=theme.SPACE_3XL)

        ctk.CTkLabel(
            frame, text="Stats",
            font=theme.FONT_PAGE_TITLE(),
            text_color=theme.TEXT,
        ).pack(anchor="w")

        ctk.CTkLabel(
            frame,
            text="Progress graphs and skill breakdowns",
            font=theme.FONT_BODY(),
            text_color=theme.TEXT_SECONDARY,
        ).pack(anchor="w", pady=(2, theme.SPACE_2XL))

        card = ctk.CTkFrame(
            frame, fg_color=theme.CARD, corner_radius=12,
            border_width=1, border_color=theme.BORDER,
        )
        card.pack(fill="x")

        ctk.CTkLabel(
            card,
            text="Coming soon",
            font=theme.FONT_SECTION(),
            text_color=theme.TEXT,
        ).pack(anchor="w", padx=theme.SPACE_LG, pady=(theme.SPACE_LG, theme.SPACE_XS))

        ctk.CTkLabel(
            card,
            text="Weekly velocity charts and skill-level breakdowns will live here.",
            font=theme.FONT_BODY(),
            text_color=theme.TEXT_MUTED,
        ).pack(anchor="w", padx=theme.SPACE_LG, pady=(0, theme.SPACE_LG))
