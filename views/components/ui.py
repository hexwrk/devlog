"""
views/components/ui.py — Shared design-system primitives
===========================================================
Every page composes its layout from these building blocks (buttons, cards,
badges, page headers, empty states, tables, charts) instead of hand-rolling
frames, so the whole app shares one visual language. This is the CustomTkinter
equivalent of a component library.
"""

import tkinter as tk
import customtkinter as ctk
import theme


# ── Buttons ──────────────────────────────────────────────────────────────────

def PrimaryButton(parent, text, command=None, width=140, height=36, **kwargs):
    return ctk.CTkButton(
        parent, text=text, command=command,
        width=width, height=height, corner_radius=theme.RADIUS_SM,
        fg_color=theme.PRIMARY, hover_color=theme.PRIMARY_HOVER,
        text_color="#FFFFFF", font=theme.font(13, "bold"),
        **kwargs,
    )


def SecondaryButton(parent, text, command=None, width=120, height=34, **kwargs):
    return ctk.CTkButton(
        parent, text=text, command=command,
        width=width, height=height, corner_radius=theme.RADIUS_SM,
        fg_color=theme.PANEL, hover_color=theme.CARD_HOVER,
        border_width=1, border_color=theme.BORDER,
        text_color=theme.TEXT, font=theme.FONT_BODY(),
        **kwargs,
    )


def GhostButton(parent, text, command=None, width=90, height=32, **kwargs):
    return ctk.CTkButton(
        parent, text=text, command=command,
        width=width, height=height, corner_radius=theme.RADIUS_SM,
        fg_color="transparent", hover_color=theme.PANEL,
        text_color=theme.TEXT_SECONDARY, font=theme.FONT_BODY(),
        **kwargs,
    )


def IconButton(parent, symbol, command=None, size=28, **kwargs):
    return ctk.CTkButton(
        parent, text=symbol, command=command,
        width=size, height=size, corner_radius=theme.RADIUS_SM,
        fg_color="transparent", hover_color=theme.PANEL,
        text_color=theme.TEXT_SECONDARY, font=theme.font(13),
        **kwargs,
    )


# ── Cards ────────────────────────────────────────────────────────────────────

_VARIANTS = {
    "default":     {"fg_color": theme.CARD, "border_color": theme.BORDER, "border_width": 1},
    "elevated":    {"fg_color": theme.SURFACE_ELEVATED, "border_color": theme.BORDER, "border_width": 1},
    "interactive": {"fg_color": theme.CARD, "border_color": theme.BORDER, "border_width": 1},
    "danger":      {"fg_color": theme.CARD, "border_color": theme.DANGER, "border_width": 1},
}


def Card(parent, variant="default", radius=None, **kwargs) -> ctk.CTkFrame:
    style = dict(_VARIANTS.get(variant, _VARIANTS["default"]))
    style.update(kwargs)
    frame = ctk.CTkFrame(parent, corner_radius=radius or theme.RADIUS_MD, **style)
    if variant == "interactive":
        frame.bind("<Enter>", lambda e: frame.configure(fg_color=theme.CARD_HOVER))
        frame.bind("<Leave>", lambda e: frame.configure(fg_color=theme.CARD))
    return frame


# ── Section label / divider ─────────────────────────────────────────────────

def SectionLabel(parent, text, **pack_kwargs):
    lbl = ctk.CTkLabel(
        parent, text=text.upper(),
        font=theme.font(11, "bold"), text_color=theme.TEXT_MUTED,
    )
    defaults = {"anchor": "w", "pady": (0, theme.SPACE_SM)}
    defaults.update(pack_kwargs)
    lbl.pack(**defaults)
    return lbl


def Divider(parent, **pack_kwargs):
    line = ctk.CTkFrame(parent, height=1, fg_color=theme.BORDER)
    defaults = {"fill": "x"}
    defaults.update(pack_kwargs)
    line.pack(**defaults)
    return line


# ── Breadcrumb + page header ────────────────────────────────────────────────

def Breadcrumb(parent, parts: list[str]):
    row = ctk.CTkFrame(parent, fg_color="transparent")
    for i, part in enumerate(parts):
        ctk.CTkLabel(
            row, text=part,
            font=theme.FONT_BREADCRUMB(), text_color=theme.TEXT_MUTED,
        ).pack(side="left")
        if i < len(parts) - 1:
            ctk.CTkLabel(
                row, text=f"  {theme.icon('chevron')}  ",
                font=theme.FONT_BREADCRUMB(), text_color=theme.TEXT_MUTED,
            ).pack(side="left")
    return row


def PageHeader(parent, title, breadcrumb=None, subtitle=None, action=None):
    """
    action, if given, is a dict: {"text": ..., "command": ...} rendered as a
    PrimaryButton at the top-right of the title row.
    Returns the outer container frame (caller still needs to .pack it).
    """
    container = ctk.CTkFrame(parent, fg_color="transparent")

    if breadcrumb:
        Breadcrumb(container, breadcrumb).pack(anchor="w", pady=(0, theme.SPACE_SM))

    title_row = ctk.CTkFrame(container, fg_color="transparent")
    title_row.pack(fill="x")

    title_col = ctk.CTkFrame(title_row, fg_color="transparent")
    title_col.pack(side="left", fill="x", expand=True)

    ctk.CTkLabel(
        title_col, text=title,
        font=theme.FONT_PAGE_TITLE(), text_color=theme.TEXT, anchor="w",
    ).pack(anchor="w")

    if subtitle:
        ctk.CTkLabel(
            title_col, text=subtitle,
            font=theme.FONT_PAGE_SUBTITLE(), text_color=theme.TEXT_SECONDARY, anchor="w",
        ).pack(anchor="w", pady=(2, 0))

    if action:
        PrimaryButton(
            title_row, text=action["text"], command=action.get("command"),
        ).pack(side="right", anchor="n")

    return container


# ── Badges ───────────────────────────────────────────────────────────────────

def StatusBadge(parent, status: str):
    info = theme.STATUS.get(status, theme.STATUS["Todo"])
    return ctk.CTkLabel(
        parent, text=f" {info['icon']} {status} ",
        font=theme.FONT_META(), fg_color=info["bg"],
        text_color=info["color"], corner_radius=theme.RADIUS_PILL,
    )


def CategoryDot(parent, category: str, show_label=True):
    colour = theme.CATEGORY_COLOURS.get(category, theme.TEXT_MUTED)
    text = f"●  {category}" if show_label else "●"
    return ctk.CTkLabel(
        parent, text=text,
        font=theme.FONT_META(), text_color=colour,
    )


def SkillBadge(parent, skill: str):
    return ctk.CTkLabel(
        parent, text=f" {skill} ",
        font=theme.FONT_META(), fg_color=theme.PANEL,
        text_color=theme.TEXT_MUTED, corner_radius=6,
    )


# ── Progress bar ─────────────────────────────────────────────────────────────

def ProgressBar(parent, value: float = 0.0, color=None, height=6):
    bar = ctk.CTkProgressBar(
        parent, height=height, corner_radius=height // 2,
        fg_color=theme.BORDER, progress_color=color or theme.PRIMARY,
    )
    bar.set(max(0.0, min(1.0, value)))
    return bar


# ── Empty state ──────────────────────────────────────────────────────────────

def EmptyState(parent, title, subtitle=None, action_text=None, action_command=None):
    wrap = ctk.CTkFrame(parent, fg_color="transparent")

    ctk.CTkLabel(
        wrap, text=title,
        font=theme.font(15, "bold"), text_color=theme.TEXT,
    ).pack(pady=(theme.SPACE_XL, theme.SPACE_XS))

    if subtitle:
        ctk.CTkLabel(
            wrap, text=subtitle,
            font=theme.FONT_BODY(), text_color=theme.TEXT_MUTED,
            justify="center",
        ).pack(pady=(0, theme.SPACE_LG))

    if action_text and action_command:
        PrimaryButton(wrap, text=action_text, command=action_command, width=200).pack(
            pady=(0, theme.SPACE_XL)
        )
    else:
        ctk.CTkFrame(wrap, height=theme.SPACE_LG, fg_color="transparent").pack()

    return wrap


# ── Simple table (info-dense rows, not boxed cards) ─────────────────────────

def Table(parent, columns: list[str], rows: list[list[str]], weights: list[int] | None = None):
    wrap = ctk.CTkFrame(parent, fg_color="transparent")
    weights = weights or [1] * len(columns)
    for i, w in enumerate(weights):
        wrap.grid_columnconfigure(i, weight=w)

    for c, col in enumerate(columns):
        ctk.CTkLabel(
            wrap, text=col.upper(), font=theme.font(10, "bold"),
            text_color=theme.TEXT_MUTED, anchor="w",
        ).grid(row=0, column=c, sticky="w", padx=(0, theme.SPACE_MD), pady=(0, theme.SPACE_SM))

    divider = ctk.CTkFrame(wrap, height=1, fg_color=theme.BORDER)
    divider.grid(row=1, column=0, columnspan=len(columns), sticky="ew", pady=(0, theme.SPACE_SM))

    if not rows:
        ctk.CTkLabel(
            wrap, text="Nothing to show yet.",
            font=theme.FONT_BODY(), text_color=theme.TEXT_MUTED,
        ).grid(row=2, column=0, columnspan=len(columns), sticky="w", pady=theme.SPACE_SM)
        return wrap

    for r, row_vals in enumerate(rows, start=2):
        for c, val in enumerate(row_vals):
            ctk.CTkLabel(
                wrap, text=val, font=theme.FONT_BODY(),
                text_color=theme.TEXT if c == 0 else theme.TEXT_SECONDARY, anchor="w",
            ).grid(row=r, column=c, sticky="w", padx=(0, theme.SPACE_MD), pady=theme.SPACE_XS)

    return wrap


# ── Canvas charts (no chart library dependency) ─────────────────────────────

def bar_chart(parent, values: list[int], labels: list[str] | None = None,
              color=None, width=280, height=100, bg=None):
    """A minimal bar chart drawn on a plain tk.Canvas."""
    bg = bg or theme.CARD
    color = color or theme.PRIMARY
    canvas = tk.Canvas(parent, width=width, height=height, bg=bg, highlightthickness=0)

    max_val = max(values) if values and max(values) > 0 else 1
    n = len(values) or 1
    gap = 6
    bar_w = max(4, (width - gap * (n + 1)) / n)
    label_h = 16 if labels else 0
    plot_h = height - label_h

    for i, v in enumerate(values):
        x0 = gap + i * (bar_w + gap)
        x1 = x0 + bar_w
        bar_h = (v / max_val) * (plot_h - 6) if max_val else 0
        y1 = plot_h
        y0 = plot_h - bar_h
        fill = color if v > 0 else theme.BORDER
        canvas.create_rectangle(x0, y0, x1, y1, fill=fill, outline="")
        if labels:
            canvas.create_text(
                (x0 + x1) / 2, plot_h + label_h / 2,
                text=labels[i], fill=theme.TEXT_MUTED,
                font=(theme.FONT_FAMILY, 9),
            )

    return canvas


def ring_chart(parent, percent: int, size=96, thickness=9, color=None, bg=None):
    """A completion ring."""
    color = color or theme.SUCCESS
    bg = bg or theme.CARD
    canvas = tk.Canvas(parent, width=size, height=size, bg=bg, highlightthickness=0)
    pad = thickness / 2 + 2
    bbox = (pad, pad, size - pad, size - pad)
    canvas.create_oval(*bbox, outline=theme.BORDER, width=thickness)
    if percent > 0:
        canvas.create_arc(
            *bbox, start=90, extent=-(percent / 100) * 360,
            style="arc", outline=color, width=thickness,
        )
    canvas.create_text(
        size / 2, size / 2, text=f"{percent}%",
        fill=theme.TEXT, font=(theme.FONT_FAMILY, 16, "bold"),
    )
    return canvas
