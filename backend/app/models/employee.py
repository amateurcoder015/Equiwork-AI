from enum import Enum
from typing import List
from pydantic import BaseModel

class EmployeeStatus(str, Enum):
    GREEN = "Green"    # 0-60
    YELLOW = "Yellow"  # 61-85
    RED = "Red"        # 86-100

class Employee(BaseModel):
    id: str
    name: str
    skills: List[str]
    load_score: float = 0.0
    growth_ratio: float = 0.0
    status: EmployeeStatus = EmployeeStatus.GREEN