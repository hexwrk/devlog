import json
from dataclasses import dataclass, asdict
from datetime import datetime
from typing import Optional

@dataclass
class Task:
    id: str
    title: str
    category: str
    skill: str
    status: str = "pending"
    priority: str = "medium"
    resource_url: Optional[str] = None
    created_at: str = datetime.now().isoformat()
    completed_at: Optional[str] = None

# Storage Handling
DB_FILE = "tasks.json"

def load_tasks() -> list[Task]:
    try:
        with open(DB_FILE, "r") as f:
            data = json.load(f)
            return [Task(**t) for t in data]
    except (FileNotFoundError, json.JSONDecodeError):
        return []

def save_tasks(tasks: list[Task]) -> None:
    with open(DB_FILE, "w") as f:
        # Converts list of Task objects back to list of dicts for JSON
        json.dump([asdict(t) for t in tasks], f, indent=4)

def add_task(task: Task) -> None:
    tasks = load_tasks()
    tasks.append(task)
    save_tasks(tasks)
