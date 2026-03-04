from dataclasses import dataclass

@dataclass
class Task:
    id: str
    title: str
    category: str
    skill: str
    status: str
    priority:str
    resource_url: str
    created_at: bool = False
    completed_at: bool = False