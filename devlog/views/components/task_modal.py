"""
views/task_modal.py — Add / Edit Task Modal
=============================================
A CTkToplevel dialog — not a new CTk() root window.

Why CTkToplevel and not CTk()?
------------------------------
CTk() creates a second root window — tkinter only supports one root.
Having two roots causes event loop conflicts and crashes.
CTkToplevel is a child window: it shares the root's event loop,
can be made modal with grab_set(), and closes cleanly.

Two modes, one component
------------------------
task=None  → Add mode  (save calls storage.save_task)
task=Task  → Edit mode (save calls storage.update_task, fields pre-filled)
"""

import customtkinter as ctk
import storage
from models import Task

MODAL_BG     = "#1C1C1E"
INPUT_BG     = "#2C2C2E"
TEXT_PRIMARY = "#F5F5F7"
TEXT_MUTED   = "#6E6E73"
ACCENT       = "#7C5CFC"
ERROR_RED    = "#FC5C7D"

CATEGORIES = ["Setup", "Frontend", "Backend", "DevOps", "Design", "Testing", "Other"]
SKILLS     = ["Python", "Git", "SQL", "CustomTkinter", "HTML", "CSS",
              "JavaScript", "Docker", "Other"]
STATUSES   = ["Todo", "In Progress", "Done", "Blocked"]
COLOURS    = {
    "Setup":    "#7C5CFC",
    "Frontend": "#43E97B",
    "Backend":  "#FC5C7D",
    "DevOps":   "#F7B731",
    "Design":   "#00D4FF",
    "Testing":  "#FF9500",
    "Other":    "#888888",
}


class TaskModal(ctk.CTkToplevel):
    """
    Parameters
    ----------
    parent   : the BoardView frame (used to position the window)
    task     : Task to edit, or None for Add mode
    on_save  : callback() — called after successful save so board can re-render
    """

    def __init__(self, parent, task: Task | None, on_save):
        super().__init__(parent)

        self._task    = task
        self._on_save = on_save
        self._mode    = "edit" if task else "add"

        # ── Window setup ──────────────────────────────────────────────────────
        title = "Edit Task" if self._mode == "edit" else "Add Task"
        self.title(title)
        self.geometry("480x520")
        self.resizable(False, False)
        self.configure(fg_color=MODAL_BG)

        # Modal behaviour: block interaction with parent until closed
        self.grab_set()
        self.focus_set()

        self._build()

        # Pre-fill fields in edit mode
        if self._mode == "edit":
            self._prefill()

    # ── Build UI ──────────────────────────────────────────────────────────────

    def _build(self):
        pad = {"padx": 28}

        ctk.CTkLabel(
            self,
            text="Edit Task" if self._mode == "edit" else "New Task",
            font=ctk.CTkFont(family="Segoe UI", size=20, weight="bold"),
            text_color=TEXT_PRIMARY,
        ).pack(anchor="w", pady=(24, 16), **pad)

        # Title
        self._title_entry = self._field("Title", pad)

        # Category dropdown
        ctk.CTkLabel(self, text="Category", font=ctk.CTkFont(size=12),
                     text_color=TEXT_MUTED).pack(anchor="w", pady=(10, 2), **pad)
        self._cat_var = ctk.StringVar(value=CATEGORIES[0])
        ctk.CTkOptionMenu(
            self, variable=self._cat_var, values=CATEGORIES,
            width=424, height=36, corner_radius=8,
            fg_color=INPUT_BG, button_color="#3A3A3C",
            text_color=TEXT_PRIMARY,
        ).pack(**pad)

        # Skill dropdown
        ctk.CTkLabel(self, text="Skill", font=ctk.CTkFont(size=12),
                     text_color=TEXT_MUTED).pack(anchor="w", pady=(10, 2), **pad)
        self._skill_var = ctk.StringVar(value=SKILLS[0])
        ctk.CTkOptionMenu(
            self, variable=self._skill_var, values=SKILLS,
            width=424, height=36, corner_radius=8,
            fg_color=INPUT_BG, button_color="#3A3A3C",
            text_color=TEXT_PRIMARY,
        ).pack(**pad)

        # Status dropdown
        ctk.CTkLabel(self, text="Status", font=ctk.CTkFont(size=12),
                     text_color=TEXT_MUTED).pack(anchor="w", pady=(10, 2), **pad)
        self._status_var = ctk.StringVar(value="Todo")
        ctk.CTkOptionMenu(
            self, variable=self._status_var, values=STATUSES,
            width=424, height=36, corner_radius=8,
            fg_color=INPUT_BG, button_color="#3A3A3C",
            text_color=TEXT_PRIMARY,
        ).pack(**pad)

        # Notes
        ctk.CTkLabel(self, text="Notes (optional)", font=ctk.CTkFont(size=12),
                     text_color=TEXT_MUTED).pack(anchor="w", pady=(10, 2), **pad)
        self._notes_box = ctk.CTkTextbox(
            self, width=424, height=70, corner_radius=8,
            fg_color=INPUT_BG, text_color=TEXT_PRIMARY,
            font=ctk.CTkFont(family="Segoe UI", size=13),
        )
        self._notes_box.pack(**pad)

        # Error label (hidden until needed)
        self._error_label = ctk.CTkLabel(
            self, text="", text_color=ERROR_RED,
            font=ctk.CTkFont(family="Segoe UI", size=12),
        )
        self._error_label.pack(pady=(6, 0))

        # Buttons
        btn_row = ctk.CTkFrame(self, fg_color="transparent")
        btn_row.pack(fill="x", padx=28, pady=(12, 24))

        ctk.CTkButton(
            btn_row, text="Cancel",
            width=100, height=36, corner_radius=8,
            fg_color="#2C2C2E", hover_color="#3A3A3C",
            text_color=TEXT_PRIMARY,
            command=self.destroy,
        ).pack(side="left")

        ctk.CTkButton(
            btn_row,
            text="Save" if self._mode == "edit" else "Add Task",
            width=120, height=36, corner_radius=8,
            fg_color=ACCENT, hover_color="#5A3FD4",
            text_color="#FFFFFF",
            font=ctk.CTkFont(weight="bold"),
            command=self._save,
        ).pack(side="right")

    def _field(self, label: str, pad: dict) -> ctk.CTkEntry:
        ctk.CTkLabel(self, text=label, font=ctk.CTkFont(size=12),
                     text_color=TEXT_MUTED).pack(anchor="w", pady=(10, 2), **pad)
        entry = ctk.CTkEntry(
            self, width=424, height=36, corner_radius=8,
            fg_color=INPUT_BG, border_color="#3A3A3C",
            text_color=TEXT_PRIMARY,
            font=ctk.CTkFont(family="Segoe UI", size=13),
        )
        entry.pack(**pad)
        return entry

    # ── Pre-fill (edit mode) ──────────────────────────────────────────────────

    def _prefill(self):
        t = self._task
        self._title_entry.insert(0, t.title)
        if t.category in CATEGORIES: self._cat_var.set(t.category)
        if t.skill    in SKILLS:     self._skill_var.set(t.skill)
        if t.status   in STATUSES:   self._status_var.set(t.status)
        if t.notes:
            self._notes_box.insert("1.0", t.notes)

    # ── Save ─────────────────────────────────────────────────────────────────

    def _save(self):
        # ── Validation: title cannot be empty ─────────────────────────────────
        title = self._title_entry.get().strip()
        if not title:
            self._error_label.configure(text="⚠  Title cannot be empty.")
            return

        notes = self._notes_box.get("1.0", "end").strip()
        cat   = self._cat_var.get()

        if self._mode == "add":
            task = Task(
                id=storage.next_id(),
                title=title,
                category=cat,
                category_colour=COLOURS.get(cat, "#888888"),
                skill=self._skill_var.get(),
                status=self._status_var.get(),
                notes=notes,
            )
            storage.save_task(task)

        else:
            # Edit mode — update fields, keep same id
            self._task.title    = title
            self._task.category = cat
            self._task.category_colour = COLOURS.get(cat, "#888888")
            self._task.skill    = self._skill_var.get()
            self._task.status   = self._status_var.get()
            self._task.notes    = notes
            storage.update_task(self._task)
            # Note: update_task() auto-sets completed_at if status == "Done"

        self._on_save()   # tell board to re-render
        self.destroy()    # close modal