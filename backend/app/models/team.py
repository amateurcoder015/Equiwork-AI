from typing import List
from pydantic import BaseModel
from .employee import Employee

class Team(BaseModel):
    id: str
    name: str
    members: List[Employee] = []
    equity_score: float = 100.0