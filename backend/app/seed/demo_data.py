from ..models.employee import Employee
from ..models.task import Task, TaskType
from ..models.team import Team
from ..store.db import db

def seed_data():
    """Injects a burnout scenario: Alice (Overloaded), Bob (Free)."""
    
    # 1. Employees
    alice = Employee(id="e1", name="Alice", skills=["Python"], load_score=0)
    bob = Employee(id="e2", name="Bob", skills=["React"], load_score=0)
    
    db.employees = {"e1": alice, "e2": bob}

    # 2. Tasks - Alice is crushed
    t1 = Task(id="t1", title="Critical DB Migration", complexity=10, deadline_urgency=10, 
              meeting_density=8, context_switches=8, visibility=9, type=TaskType.MAINTENANCE, assignee_id="e1")
    
    t2 = Task(id="t2", title="API Gateway Refactor", complexity=8, deadline_urgency=9, 
              meeting_density=5, context_switches=5, visibility=8, type=TaskType.MAINTENANCE, assignee_id="e1")

    # Bob has very light work
    t3 = Task(id="t3", title="Update Footer Logo", complexity=1, deadline_urgency=2, 
              visibility=1, type=TaskType.MAINTENANCE, assignee_id="e2")

    db.tasks = {"t1": t1, "t2": t2, "t3": t3}

    # 3. Team
    team = Team(id="team1", name="Product Team", members=[alice, bob])
    db.teams = {"team1": team}
    
    print("✅ Seed Data Loaded: Alice is set to burnout.")