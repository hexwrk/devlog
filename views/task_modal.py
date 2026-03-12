"""
views/task_modal.py — Add / Edit Task Modal
Includes: repo URL field + drag & drop file attachments
"""

import os
import customtkinter as ctk
import tkinter as tk
from tkinter import filedialog
import storage
from models import Task

MODAL_BG     = "#1C1C1E"
INPUT_BG     = "#2C2C2E"
TEXT_PRIMARY = "#F5F5F7"
TEXT_MUTED   = "#6E6E73"
ACCENT       = "#7C5CFC"
ERROR_RED    = "#FC5C7D"
DROP_BG      = "#242426"
DROP_HOVER   = "#2A2A4A"

CATEGORIES = ["Setup", "Frontend", "Backend", "DevOps", "Design", "Testing", "Other"]
SKILLS     = ["Python", "Git", "SQL", "CustomTkinter", "HTML", "CSS",
              "JavaScript", "Docker", "Other"]
STATUSES   = ["Todo", "In Progress", "Done", "Blocked"]
COLOURS    = {
    "Setup":    "#7C5CFC", "Frontend": "#43E97B", "Backend":  "#FC5C7D",
    "DevOps":   "#F7B731", "Design":   "#00D4FF", "Testing":  "#FF9500",
    "Other":    "#888888",
}


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
        self.after(200, lambda: self.iconbitmap("devlog.ico"))

        self.grab_set()
        self.focus_set()

        self._build()
        if self._mode == "edit":
            self._prefill()

    # ── UI ────────────────────────────────────────────────────────────────────

    def _build(self):
        scroll = ctk.CTkScrollableFrame(
            self, fg_color=MODAL_BG, scrollbar_button_color="#3A3A3C"
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

        # ── Repo URL ──────────────────────────────────────────────────────────
        ctk.CTkLabel(scroll, text="GitHub / Repo URL",
                     font=ctk.CTkFont(size=12), text_color=TEXT_MUTED,
                     ).pack(anchor="w", pady=(10, 2), **pad)

        repo_row = ctk.CTkFrame(scroll, fg_color="transparent")
        repo_row.pack(fill="x", **pad)

        self._repo_entry = ctk.CTkEntry(
            repo_row, height=36, corner_radius=8,
            fg_color=INPUT_BG, border_color="#3A3A3C",
            text_color=TEXT_PRIMARY,
            placeholder_text="https://github.com/user/repo",
            font=ctk.CTkFont(family="Segoe UI", size=13),
        )
        self._repo_entry.pack(side="left", fill="x", expand=True, padx=(0, 8))

        # Open repo button
        ctk.CTkButton(
            repo_row, text="🔗", width=36, height=36, corner_radius=8,
            fg_color="#2C2C2E", hover_color="#3A3A3C",
            text_color=TEXT_PRIMARY,
            command=self._open_repo,
        ).pack(side="right")

        # ── Drag & Drop zone ──────────────────────────────────────────────────
        ctk.CTkLabel(scroll, text="Attachments",
                     font=ctk.CTkFont(size=12), text_color=TEXT_MUTED,
                     ).pack(anchor="w", pady=(14, 2), **pad)

        # Drop zone frame
        self._drop_frame = ctk.CTkFrame(
            scroll, fg_color=DROP_BG, corner_radius=10,
            border_color="#3A3A3C", border_width=1,
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
            fg_color=ACCENT, hover_color="#5A3FD4",
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
            fg_color="#2C2C2E", hover_color="#3A3A3C",
            text_color=TEXT_PRIMARY,
            command=self.destroy,
        ).pack(side="left")

        ctk.CTkButton(
            btn_row,
            text="Save" if self._mode == "edit" else "Add Task",
            width=130, height=38, corner_radius=8,
            fg_color=ACCENT, hover_color="#5A3FD4",
            text_color="#FFFFFF",
            font=ctk.CTkFont(weight="bold"),
            command=self._save,
        ).pack(side="right")

    def _field(self, parent, label, pad) -> ctk.CTkEntry:
        ctk.CTkLabel(parent, text=label, font=ctk.CTkFont(size=12),
                     text_color=TEXT_MUTED).pack(anchor="w", pady=(10, 2), **pad)
        entry = ctk.CTkEntry(
            parent, height=36, corner_radius=8,
            fg_color=INPUT_BG, border_color="#3A3A3C",
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
            fg_color=INPUT_BG, button_color="#3A3A3C",
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
            row = ctk.CTkFrame(self._attach_list_frame, fg_color="#2C2C2E", corner_radius=6)
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
                fg_color="transparent", hover_color="#3A3A3C",
                text_color=TEXT_MUTED,
                command=lambda p=path: os.startfile(p),
            ).pack(side="right", padx=(0, 4))

            # Remove button
            ctk.CTkButton(
                row, text="✕", width=28, height=24, corner_radius=4,
                fg_color="transparent", hover_color="#4A1A1A",
                text_color="#FC5C7D",
                command=lambda p=path: self._remove_attachment(p),
            ).pack(side="right", padx=(0, 2))

    def _remove_attachment(self, path: str):
        if path in self._attachments:
            self._attachments.remove(path)
        self._refresh_attachment_list()

    def _open_repo(self):
        url = self._repo_entry.get().strip()
        if url:
            import webbrowser
            webbrowser.open(url)

    # ── Prefill ───────────────────────────────────────────────────────────────

    def _prefill(self):
        t = self._task
        self._title_entry.insert(0, t.title)
        if t.category in CATEGORIES: self._category_var.set(t.category)
        if t.skill    in SKILLS:     self._skill_var.set(t.skill)
        if t.status   in STATUSES:   self._status_var.set(t.status)
        if t.repo_url:
            self._repo_entry.insert(0, t.repo_url)
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
        repo_url = self._repo_entry.get().strip()

        if self._mode == "add":
            task = Task(
                id=storage.next_id(),
                title=title,
                category=cat,
                category_colour=COLOURS.get(cat, "#888888"),
                skill=self._skill_var.get(),
                status=self._status_var.get(),
                notes=notes,
                repo_url=repo_url,
                attachments=self._attachments,
            )
            storage.save_task(task)
        else:
            self._task.title           = title
            self._task.category        = cat
            self._task.category_colour = COLOURS.get(cat, "#888888")
            self._task.skill           = self._skill_var.get()
            self._task.status          = self._status_var.get()
            self._task.notes           = notes
            self._task.repo_url        = repo_url
            self._task.attachments     = self._attachments
            storage.update_task(self._task)

        self._on_save()
        self.destroy()
