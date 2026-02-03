from enum import Enum
from pydantic import BaseModel
from typing import Optional

class TaskType(str, Enum):
    GROWTH = "growth"
    MAINTENANCE = "maintenance"

class Task(BaseModel):
    id: str
    title: str
    complexity: int             # 1-10
    deadline_urgency: int       # 1-10
    meeting_density: int = 0    # 1-10
    context_switches: int = 0   # 1-10
    visibility: int             # 1-10
    type: TaskType
    assignee_id: Optional[str] = None
    
    @property
    def is_high_visibility(self) -> bool:
        return self.visibility >= 8