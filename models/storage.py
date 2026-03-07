"""
storage.py — JSON persistence layer for DevLog
===============================================
All reads and writes go through here. The UI never touches the file directly.

Key idea: re-render from disk, not from a local list.
If you keep a list in memory and also write to disk, they can drift apart.
Loading fresh from disk on every render guarantees the UI always reflects
the true state of the data.
"""

import json
import os
from datetime import date
from models import Task

DATA_FILE = os.path.join(os.path.dirname(__file__), "tasks.json")


def _read_raw() -> list[dict]:
    if not os.path.exists(DATA_FILE):
        return []
    with open(DATA_FILE, "r", encoding="utf-8") as f:
        try:
            return json.load(f)
        except json.JSONDecodeError:
            return []


def _write_raw(data: list[dict]) -> None:
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


def load_tasks() -> list[Task]:
    """Return all tasks from disk as Task objects."""
    return [Task(**row) for row in _read_raw()]


def save_task(task: Task) -> None:
    """Add a new task. task.id must already be set."""
    data = _read_raw()
    data.append(vars(task))
    _write_raw(data)


def update_task(updated: Task) -> None:
    """
    Replace the task with matching id.
    Automatically sets completed_at when status becomes 'Done'.
    """
    data = _read_raw()
    for i, row in enumerate(data):
        if row["id"] == updated.id:
            updated_dict = vars(updated).copy()
            # Auto-set completed_at when marked Done
            if updated.status == "Done" and not updated.completed_at:
                updated_dict["completed_at"] = date.today().isoformat()
            elif updated.status != "Done":
                updated_dict["completed_at"] = None
            data[i] = updated_dict
            break
    _write_raw(data)


def delete_task(task_id: str) -> None:
    """Remove task by id."""
    data = [row for row in _read_raw() if row["id"] != task_id]
    _write_raw(data)


def next_id() -> str:
    """Simple incrementing integer id as string."""
    data = _read_raw()
    if not data:
        return "1"
    max_id = max(int(row["id"]) for row in data)
    return str(max_id + 1)