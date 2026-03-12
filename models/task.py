from dataclasses import dataclass
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
