"""
views/task_modal.py — Add / Edit Task Modal
Includes: repo URL field + drag & drop file attachments
"""

import os
from pathlib import Path
import customtkinter as ctk
import tkinter as tk
from tkinter import filedialog
import storage
import theme
from models import CATEGORIES, DIFFICULTIES, Task

_ICON_PATH = Path(__file__).resolve().parent.parent / "devlog.ico"

MODAL_BG     = theme.PANEL
INPUT_BG     = theme.CARD
TEXT_PRIMARY = theme.TEXT
TEXT_MUTED   = theme.TEXT_MUTED
ACCENT       = theme.PRIMARY
ERROR_RED    = theme.DANGER
DROP_BG      = theme.CARD
DROP_HOVER   = theme.CARD_HOVER

SKILLS     = ["Python", "Git", "SQL", "CustomTkinter", "HTML", "CSS",
              "JavaScript", "Docker", "Linux", "Networking", "Web Security",
              "Cryptography", "Reverse Engineering", "Other"]
STATUSES   = ["Todo", "In Progress", "Done", "Blocked"]
COLOURS = theme.CATEGORY_COLOURS


class TaskModal(ctk.CTkToplevel):

    def __init__(self, parent, task: Task | None, on_save):
        super().__init__(parent)

        self._task        = task
        self._on_save     = on_save
        self._mode        = "edit" if task else "add"
        self._attachments = list(task.attachments) if task else []

        title = "Edit Task" if self._mode == "edit" else "Add Task"
        self.title(title)
        self.geometry("500x680")
        self.minsize(500, 600)
        self.resizable(False, True)
        self.configure(fg_color=MODAL_BG)
        self.after(200, self._set_icon)

        self.grab_set()
        self.focus_set()

        self._build()
        if self._mode == "edit":
            self._prefill()

    def _set_icon(self):
        try:
            self.iconbitmap(str(_ICON_PATH))
        except Exception:
            pass

    # ── UI ────────────────────────────────────────────────────────────────────

    def _build(self):
        scroll = ctk.CTkScrollableFrame(
            self, fg_color=MODAL_BG, scrollbar_button_color=theme.BORDER
        )
        scroll.pack(fill="both", expand=True)

        pad = {"padx": 28}

        ctk.CTkLabel(
            scroll,
            text="Edit Task" if self._mode == "edit" else "New Task",
            font=ctk.CTkFont(family="Segoe UI", size=20, weight="bold"),
            text_color=TEXT_PRIMARY,
        ).pack(anchor="w", pady=(24, 16), **pad)

        self._title_entry = self._field(scroll, "Title", pad)
        self._dropdown(scroll, "Category", CATEGORIES, pad)
        self._dropdown(scroll, "Skill",    SKILLS,      pad)
        self._dropdown(scroll, "Status",   STATUSES,    pad)
        self._dropdown(scroll, "Difficulty", DIFFICULTIES, pad)

        # ── Resource URLs ─────────────────────────────────────────────────────
        ctk.CTkLabel(scroll, text="Resource URLs (one per line)",
                     font=ctk.CTkFont(size=12), text_color=TEXT_MUTED,
                     ).pack(anchor="w", pady=(10, 2), **pad)

        self._resources_box = ctk.CTkTextbox(
            scroll, height=58, corner_radius=8,
            fg_color=INPUT_BG, border_color=theme.BORDER,
            text_color=TEXT_PRIMARY,
            font=ctk.CTkFont(family="Segoe UI", size=13),
        )
        self._resources_box.pack(fill="x", **pad)

        # ── Drag & Drop zone ──────────────────────────────────────────────────
        ctk.CTkLabel(scroll, text="Attachments",
                     font=ctk.CTkFont(size=12), text_color=TEXT_MUTED,
                     ).pack(anchor="w", pady=(14, 2), **pad)

        # Drop zone frame
        self._drop_frame = ctk.CTkFrame(
            scroll, fg_color=DROP_BG, corner_radius=10,
            border_color=theme.BORDER, border_width=1,
        )
        self._drop_frame.pack(fill="x", pady=(0, 4), **pad)

        self._drop_label = ctk.CTkLabel(
            self._drop_frame,
            text="📂  Drop files here  or",
            font=ctk.CTkFont(family="Segoe UI", size=13),
            text_color=TEXT_MUTED,
        )
        self._drop_label.pack(side="left", padx=(16, 8), pady=14)

        ctk.CTkButton(
            self._drop_frame,
            text="Browse",
            width=80, height=28, corner_radius=6,
            fg_color=ACCENT, hover_color=theme.PRIMARY_HOVER,
            text_color="#FFFFFF",
            font=ctk.CTkFont(size=12),
            command=self._browse_files,
        ).pack(side="left", pady=14)

        # Register drag & drop via tkinterdnd2 if available, else show hint
        self._register_drop(self._drop_frame)

        # Attachment list
        self._attach_list_frame = ctk.CTkFrame(scroll, fg_color="transparent")
        self._attach_list_frame.pack(fill="x", **pad)
        self._refresh_attachment_list()

        # Notes
        ctk.CTkLabel(scroll, text="Notes (optional)",
                     font=ctk.CTkFont(size=12), text_color=TEXT_MUTED,
                     ).pack(anchor="w", pady=(10, 2), **pad)
        self._notes_box = ctk.CTkTextbox(
            scroll, width=444, height=80, corner_radius=8,
            fg_color=INPUT_BG, text_color=TEXT_PRIMARY,
            font=ctk.CTkFont(family="Segoe UI", size=13),
        )
        self._notes_box.pack(**pad)

        # Error
        self._error_label = ctk.CTkLabel(
            scroll, text="", text_color=ERROR_RED,
            font=ctk.CTkFont(size=12),
        )
        self._error_label.pack(pady=(6, 0))

        # Buttons
        btn_row = ctk.CTkFrame(scroll, fg_color="transparent")
        btn_row.pack(fill="x", padx=28, pady=(16, 28))

        ctk.CTkButton(
            btn_row, text="Cancel",
            width=100, height=38, corner_radius=8,
            fg_color=theme.CARD, hover_color=theme.BORDER,
            text_color=TEXT_PRIMARY,
            command=self.destroy,
        ).pack(side="left")

        ctk.CTkButton(
            btn_row,
            text="Save" if self._mode == "edit" else "Add Task",
            width=130, height=38, corner_radius=8,
            fg_color=ACCENT, hover_color=theme.PRIMARY_HOVER,
            text_color="#FFFFFF",
            font=ctk.CTkFont(weight="bold"),
            command=self._save,
        ).pack(side="right")

    def _field(self, parent, label, pad) -> ctk.CTkEntry:
        ctk.CTkLabel(parent, text=label, font=ctk.CTkFont(size=12),
                     text_color=TEXT_MUTED).pack(anchor="w", pady=(10, 2), **pad)
        entry = ctk.CTkEntry(
            parent, height=36, corner_radius=8,
            fg_color=INPUT_BG, border_color=theme.BORDER,
            text_color=TEXT_PRIMARY,
            font=ctk.CTkFont(family="Segoe UI", size=13),
        )
        entry.pack(fill="x", **pad)
        return entry

    def _dropdown(self, parent, label, values, pad):
        ctk.CTkLabel(parent, text=label, font=ctk.CTkFont(size=12),
                     text_color=TEXT_MUTED).pack(anchor="w", pady=(10, 2), **pad)
        var = ctk.StringVar(value=values[0])
        setattr(self, f"_{label.lower()}_var", var)
        ctk.CTkOptionMenu(
            parent, variable=var, values=values,
            height=36, corner_radius=8,
            fg_color=INPUT_BG, button_color=theme.BORDER,
            text_color=TEXT_PRIMARY,
        ).pack(fill="x", **pad)

    # ── Drag & drop ───────────────────────────────────────────────────────────

    def _register_drop(self, widget):
        """
        Try to use tkinterdnd2 for native drag & drop.
        Falls back gracefully if not installed — Browse button still works.
        """
        try:
            from tkinterdnd2 import DND_FILES
            widget.drop_target_register(DND_FILES)
            widget.dnd_bind("<<Drop>>", self._on_drop)
            widget.dnd_bind("<<DragEnter>>",
                lambda e: self._drop_frame.configure(fg_color=DROP_HOVER))
            widget.dnd_bind("<<DragLeave>>",
                lambda e: self._drop_frame.configure(fg_color=DROP_BG))
        except Exception:
            # tkinterdnd2 not installed — browse still works
            pass

    def _on_drop(self, event):
        """Parse dropped file paths from the event data string."""
        self._drop_frame.configure(fg_color=DROP_BG)
        # tkinterdnd2 returns paths wrapped in {} if they contain spaces
        raw = event.data
        paths = self._parse_drop_paths(raw)
        for p in paths:
            if p and p not in self._attachments:
                self._attachments.append(p)
        self._refresh_attachment_list()

    def _parse_drop_paths(self, raw: str) -> list[str]:
        """Handle both space-separated and {brace-wrapped} path formats."""
        import re
        paths = re.findall(r'\{([^}]+)\}|(\S+)', raw)
        return [p[0] or p[1] for p in paths]

    def _browse_files(self):
        paths = filedialog.askopenfilenames(
            title="Attach files",
            parent=self,
        )
        for p in paths:
            if p not in self._attachments:
                self._attachments.append(p)
        self._refresh_attachment_list()

    def _refresh_attachment_list(self):
        """Rebuild the attachment list UI."""
        for w in self._attach_list_frame.winfo_children():
            w.destroy()

        if not self._attachments:
            ctk.CTkLabel(
                self._attach_list_frame,
                text="No files attached yet.",
                font=ctk.CTkFont(size=11),
                text_color=TEXT_MUTED,
            ).pack(anchor="w", pady=(4, 0))
            return

        for path in self._attachments:
            row = ctk.CTkFrame(self._attach_list_frame, fg_color=theme.CARD, corner_radius=6)
            row.pack(fill="x", pady=2)

            filename = os.path.basename(path)
            ctk.CTkLabel(
                row, text=f"📄  {filename}",
                font=ctk.CTkFont(size=12), text_color=TEXT_PRIMARY,
                anchor="w",
            ).pack(side="left", padx=10, pady=6, fill="x", expand=True)

            # Open file button
            ctk.CTkButton(
                row, text="↗", width=28, height=24, corner_radius=4,
                fg_color="transparent", hover_color=theme.BORDER,
                text_color=TEXT_MUTED,
                command=lambda p=path: self._open_attachment(p),
            ).pack(side="right", padx=(0, 4))

            # Remove button
            ctk.CTkButton(
                row, text="✕", width=28, height=24, corner_radius=4,
                fg_color="transparent", hover_color=theme.STATUS["Blocked"]["bg"],
                text_color=theme.DANGER,
                command=lambda p=path: self._remove_attachment(p),
            ).pack(side="right", padx=(0, 2))

    def _remove_attachment(self, path: str):
        if path in self._attachments:
            self._attachments.remove(path)
        self._refresh_attachment_list()

    def _open_attachment(self, path: str):
        import subprocess
        if hasattr(os, "startfile"):
            os.startfile(path)
        else:
            subprocess.Popen(["xdg-open", path], stdout=subprocess.DEVNULL,
                             stderr=subprocess.DEVNULL)

    def _open_repo(self):
        urls = self._resources_box.get("1.0", "end").splitlines()
        url = urls[0].strip() if urls else ""
        from urllib.parse import urlparse
        if urlparse(url).scheme in {"http", "https"} and urlparse(url).netloc:
            import webbrowser
            webbrowser.open(url)

    # ── Prefill ───────────────────────────────────────────────────────────────

    def _prefill(self):
        t = self._task
        self._title_entry.insert(0, t.title)
        if t.category in CATEGORIES: self._category_var.set(t.category)
        if t.skill    in SKILLS:     self._skill_var.set(t.skill)
        if t.status   in STATUSES:   self._status_var.set(t.status)
        if t.resources:
            self._resources_box.insert("1.0", "\n".join(t.resources))
        if t.notes:
            self._notes_box.insert("1.0", t.notes)

    # ── Save ──────────────────────────────────────────────────────────────────

    def _save(self):
        title = self._title_entry.get().strip()
        if not title:
            self._error_label.configure(text="⚠  Title cannot be empty.")
            return

        notes    = self._notes_box.get("1.0", "end").strip()
        cat      = self._category_var.get()
        resources = [url.strip() for url in self._resources_box.get("1.0", "end").splitlines() if url.strip()]

        if self._mode == "add":
            try:
                task = Task(
                    id=storage.next_id(), title=title, category=cat,
                    category_colour=COLOURS.get(cat, theme.TEXT_MUTED),
                    skill=self._skill_var.get(), status=self._status_var.get(),
                    notes=notes, resources=resources, attachments=self._attachments,
                    difficulty=self._difficulty_var.get(),
                )
                storage.save_task(task)
            except ValueError as exc:
                self._error_label.configure(text=str(exc))
                return
        else:
            self._task.title           = title
            self._task.category        = cat
            self._task.category_colour = COLOURS.get(cat, theme.TEXT_MUTED)
            self._task.skill           = self._skill_var.get()
            self._task.status          = self._status_var.get()
            self._task.notes           = notes
            self._task.resources       = resources
            self._task.attachments     = self._attachments
            self._task.difficulty      = self._difficulty_var.get()
            try:
                Task(**vars(self._task))
                storage.update_task(self._task)
            except ValueError as exc:
                self._error_label.configure(text=str(exc))
                return

        self._on_save()
        self.destroy()
