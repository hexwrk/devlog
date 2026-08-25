"""
views/task_modal.py — Add / Edit Task Modal
Includes: resource URLs, due date, and drag & drop file attachments.
"""

import os
import re
from pathlib import Path
from datetime import date
import customtkinter as ctk
import tkinter as tk
from tkinter import filedialog
import storage
import theme
from models import CATEGORIES, DIFFICULTIES, Task
from views.components import ui

_ICON_PATH = Path(__file__).resolve().parent.parent / "devlog.ico"

INPUT_BG = theme.CARD
DROP_BG    = theme.CARD
DROP_HOVER = theme.CARD_HOVER

SKILLS     = ["Python", "Git", "SQL", "CustomTkinter", "HTML", "CSS",
              "JavaScript", "Docker", "Linux", "Networking", "Web Security",
              "Cryptography", "Reverse Engineering", "Other"]
STATUSES   = ["Todo", "In Progress", "Done", "Blocked"]
COLOURS = theme.CATEGORY_COLOURS


class TaskModal(ctk.CTkToplevel):

    def __init__(self, parent, task: Task | None, on_save, default_category: str | None = None):
        super().__init__(parent)

        self._task        = task
        self._on_save     = on_save
        self._mode        = "edit" if task else "add"
        self._attachments = list(task.attachments) if task else []

        title = "Edit Task" if self._mode == "edit" else "Add Task"
        self.title(title)
        self.geometry("500x720")
        self.minsize(500, 620)
        self.resizable(False, True)
        self.configure(fg_color=theme.PANEL)
        self.after(200, self._set_icon)

        self.grab_set()
        self.focus_set()

        self._build()
        if self._mode == "edit":
            self._prefill()
        elif default_category and default_category in CATEGORIES:
            self._category_var.set(default_category)

    def _set_icon(self):
        try:
            self.iconbitmap(str(_ICON_PATH))
        except Exception:
            pass

    # ── UI ────────────────────────────────────────────────────────────────────

    def _build(self):
        scroll = ctk.CTkScrollableFrame(
            self, fg_color=theme.PANEL, scrollbar_button_color=theme.BORDER
        )
        scroll.pack(fill="both", expand=True)

        pad = {"padx": 28}

        ctk.CTkLabel(
            scroll,
            text="Edit Task" if self._mode == "edit" else "New Task",
            font=theme.font(20, "bold"),
            text_color=theme.TEXT,
        ).pack(anchor="w", pady=(24, 16), **pad)

        self._title_entry = self._field(scroll, "Title", pad)
        self._dropdown(scroll, "Category", CATEGORIES, pad)
        self._dropdown(scroll, "Skill",    SKILLS,      pad)
        self._dropdown(scroll, "Status",   STATUSES,    pad)
        self._dropdown(scroll, "Difficulty", DIFFICULTIES, pad)
        self._due_date_entry = self._field(scroll, "Due Date (YYYY-MM-DD, optional)", pad)

        # ── Resource URLs ─────────────────────────────────────────────────────
        ctk.CTkLabel(scroll, text="Resource URLs (one per line)",
                     font=theme.FONT_META(), text_color=theme.TEXT_MUTED,
                     ).pack(anchor="w", pady=(10, 2), **pad)

        self._resources_box = ctk.CTkTextbox(
            scroll, height=58, corner_radius=theme.RADIUS_SM,
            fg_color=INPUT_BG, border_color=theme.BORDER,
            text_color=theme.TEXT,
            font=theme.FONT_BODY(),
        )
        self._resources_box.pack(fill="x", **pad)

        # ── Drag & Drop zone ──────────────────────────────────────────────────
        ctk.CTkLabel(scroll, text="Attachments",
                     font=theme.FONT_META(), text_color=theme.TEXT_MUTED,
                     ).pack(anchor="w", pady=(14, 2), **pad)

        self._drop_frame = ctk.CTkFrame(
            scroll, fg_color=DROP_BG, corner_radius=theme.RADIUS_MD,
            border_color=theme.BORDER, border_width=1,
        )
        self._drop_frame.pack(fill="x", pady=(0, 4), **pad)

        self._drop_label = ctk.CTkLabel(
            self._drop_frame,
            text=f"{theme.icon('folder')}  Drop files here  or",
            font=theme.FONT_BODY(),
            text_color=theme.TEXT_MUTED,
        )
        self._drop_label.pack(side="left", padx=(16, 8), pady=14)

        ui.SecondaryButton(
            self._drop_frame, text="Browse", width=80, height=28,
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
                     font=theme.FONT_META(), text_color=theme.TEXT_MUTED,
                     ).pack(anchor="w", pady=(10, 2), **pad)
        self._notes_box = ctk.CTkTextbox(
            scroll, height=80, corner_radius=theme.RADIUS_SM,
            fg_color=INPUT_BG, text_color=theme.TEXT,
            font=theme.FONT_BODY(),
        )
        self._notes_box.pack(fill="x", **pad)

        # Error
        self._error_label = ctk.CTkLabel(
            scroll, text="", text_color=theme.DANGER,
            font=theme.FONT_META(),
        )
        self._error_label.pack(pady=(6, 0))

        # Buttons
        btn_row = ctk.CTkFrame(scroll, fg_color="transparent")
        btn_row.pack(fill="x", padx=28, pady=(16, 28))

        ctk.CTkButton(
            btn_row, text="Cancel",
            width=100, height=38, corner_radius=theme.RADIUS_SM,
            fg_color=theme.CARD, hover_color=theme.BORDER,
            text_color=theme.TEXT, font=theme.FONT_BODY(),
            command=self.destroy,
        ).pack(side="left")

        ui.PrimaryButton(
            btn_row,
            text="Save" if self._mode == "edit" else "Add Task",
            width=130, height=38,
            command=self._save,
        ).pack(side="right")

    def _field(self, parent, label, pad) -> ctk.CTkEntry:
        ctk.CTkLabel(parent, text=label, font=theme.FONT_META(),
                     text_color=theme.TEXT_MUTED).pack(anchor="w", pady=(10, 2), **pad)
        entry = ctk.CTkEntry(
            parent, height=36, corner_radius=theme.RADIUS_SM,
            fg_color=INPUT_BG, border_color=theme.BORDER,
            text_color=theme.TEXT,
            font=theme.FONT_BODY(),
        )
        entry.pack(fill="x", **pad)
        return entry

    def _dropdown(self, parent, label, values, pad):
        ctk.CTkLabel(parent, text=label, font=theme.FONT_META(),
                     text_color=theme.TEXT_MUTED).pack(anchor="w", pady=(10, 2), **pad)
        var = ctk.StringVar(value=values[0])
        setattr(self, f"_{label.lower()}_var", var)
        ctk.CTkOptionMenu(
            parent, variable=var, values=values,
            height=36, corner_radius=theme.RADIUS_SM,
            fg_color=INPUT_BG, button_color=theme.BORDER,
            text_color=theme.TEXT, font=theme.FONT_BODY(),
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
        raw = event.data
        paths = self._parse_drop_paths(raw)
        for p in paths:
            if p and p not in self._attachments:
                self._attachments.append(p)
        self._refresh_attachment_list()

    def _parse_drop_paths(self, raw: str) -> list[str]:
        """Handle both space-separated and {brace-wrapped} path formats."""
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
                font=theme.FONT_META(),
                text_color=theme.TEXT_MUTED,
            ).pack(anchor="w", pady=(4, 0))
            return

        for path in self._attachments:
            row = ctk.CTkFrame(self._attach_list_frame, fg_color=theme.CARD, corner_radius=6)
            row.pack(fill="x", pady=2)

            filename = os.path.basename(path)
            ctk.CTkLabel(
                row, text=f"{theme.icon('file')}  {filename}",
                font=theme.FONT_META(), text_color=theme.TEXT,
                anchor="w",
            ).pack(side="left", padx=10, pady=6, fill="x", expand=True)

            ui.IconButton(row, theme.icon("external"), lambda p=path: self._open_attachment(p), size=26).pack(
                side="right", padx=(0, 4)
            )
            close_btn = ui.IconButton(row, theme.icon("close"), lambda p=path: self._remove_attachment(p), size=26)
            close_btn.configure(text_color=theme.DANGER, hover_color=theme.STATUS["Blocked"]["bg"])
            close_btn.pack(side="right", padx=(0, 2))

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

    # ── Prefill ───────────────────────────────────────────────────────────────

    def _prefill(self):
        t = self._task
        self._title_entry.insert(0, t.title)
        if t.category in CATEGORIES: self._category_var.set(t.category)
        if t.skill    in SKILLS:     self._skill_var.set(t.skill)
        if t.status   in STATUSES:   self._status_var.set(t.status)
        if t.difficulty in DIFFICULTIES: self._difficulty_var.set(t.difficulty)
        if t.due_date:
            self._due_date_entry.insert(0, t.due_date)
        if t.resources:
            self._resources_box.insert("1.0", "\n".join(t.resources))
        if t.notes:
            self._notes_box.insert("1.0", t.notes)

    # ── Save ──────────────────────────────────────────────────────────────────

    def _valid_due_date(self, value: str) -> bool:
        if not value:
            return True
        try:
            date.fromisoformat(value)
            return True
        except ValueError:
            return False

    def _save(self):
        title = self._title_entry.get().strip()
        if not title:
            self._error_label.configure(text=f"{theme.icon('close')}  Title cannot be empty.")
            return

        due_date = self._due_date_entry.get().strip()
        if not self._valid_due_date(due_date):
            self._error_label.configure(text=f"{theme.icon('close')}  Due date must look like YYYY-MM-DD.")
            return
        due_date = due_date or None

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
                    difficulty=self._difficulty_var.get(), due_date=due_date,
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
            self._task.due_date        = due_date
            try:
                Task(**vars(self._task))
                storage.update_task(self._task)
            except ValueError as exc:
                self._error_label.configure(text=str(exc))
                return

        self._on_save()
        self.destroy()
