"""
models.py — Core data structures for DevLog
Keep this file for backwards compatibility.
The models package (models/) is the new home.
"""

from dataclasses import dataclass, field
from typing import Literal, Optional

StatusType = Literal["Todo", "In Progress", "Done", "Blocked"]


@dataclass
class Task:
    id: str
    title: str
    category: str
    category_colour: str
    skill: str
    status: StatusType = "Todo"
    notes: str = ""
    completed_at: Optional[str] = None
    due_date: Optional[str] = None
    repo_url: str = ""
    attachments: list = field(default_factory=list)
