from dataclasses import dataclass, field
from typing import Literal, Optional
from urllib.parse import urlparse

StatusType = Literal["Todo", "In Progress", "Done", "Blocked"]
CategoryType = Literal["Lab", "Study", "Project", "CTF", "Reading", "Revision"]
DifficultyType = Literal["Easy", "Medium", "Hard"]

CATEGORIES = ("Lab", "Study", "Project", "CTF", "Reading", "Revision")
DIFFICULTIES = ("Easy", "Medium", "Hard")


def _valid_url(value: str) -> bool:
    parsed = urlparse(value)
    return parsed.scheme in {"http", "https"} and bool(parsed.netloc)


@dataclass
class Task:
    id: str
    title: str
    category: CategoryType
    category_colour: str
    skill: str
    status: StatusType = "Todo"
    notes: str = ""
    completed_at: Optional[str] = None
    due_date: Optional[str] = None
    resources: list[str] = field(default_factory=list)
    attachments: list[str] = field(default_factory=list)
    difficulty: DifficultyType = "Medium"
    duration_minutes: int = 60

    def __post_init__(self):
        if self.category not in CATEGORIES:
            raise ValueError(f"category must be one of {CATEGORIES}")
        if self.status not in ("Todo", "In Progress", "Done", "Blocked"):
            raise ValueError("invalid task status")
        if self.difficulty not in DIFFICULTIES:
            raise ValueError(f"difficulty must be one of {DIFFICULTIES}")
        if not self.title.strip() or not self.skill.strip():
            raise ValueError("title and skill cannot be empty")
        if self.duration_minutes < 1:
            raise ValueError("duration_minutes must be positive")
        if any(not isinstance(url, str) or not _valid_url(url) for url in self.resources):
            raise ValueError("resources must contain absolute http(s) URLs")
