from enum import Enum
from pydantic import BaseModel
from typing import Optional

class TaskType(str, Enum):
    GROWTH = "growth"
    MAINTENANCE = "maintenance"

class Task(BaseModel):
    id: str
    title: str
    description: str  # <--- NEW FIELD
    complexity: int             
    deadline_urgency: int       
    meeting_density: int = 0    
    context_switches: int = 0   
    visibility: int             
    type: TaskType
    assignee_id: Optional[str] = None
    
    @property
    def is_high_visibility(self) -> bool:
        return self.visibility >= 8