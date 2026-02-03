from ..models.employee import Employee
from ..models.task import Task, TaskType
from ..store.db import db

def seed_data():
    """Injects an expanded team scenario for better AI testing."""
    # 1. Employees with diverse skillsets
    db.employees = {
        "e1": Employee(id="e1", name="Alice", skills=["Python", "PostgreSQL"], load_score=0),
        "e2": Employee(id="e2", name="Bob", skills=["React", "TypeScript", "Figma"], load_score=0),
        "e3": Employee(id="e3", name="Charlie", skills=["Python", "Docker", "AWS"], load_score=0),
        "e4": Employee(id="e4", name="Dana", skills=["UI/UX", "Tailwind"], load_score=0)
    }

    # 2. Diverse Task List
    db.tasks = {
        "t1": Task(
            id="t1", title="Database Sharding", 
            description="Migrating the user table to a sharded PostgreSQL cluster. High-risk maintenance.",
            complexity=10, deadline_urgency=10, visibility=9, 
            type=TaskType.MAINTENANCE, assignee_id="e1"
        ),
        "t2": Task(
            id="t2", title="Internal API Docs", 
            description="Updating Swagger docs for internal endpoints. Repetitive low-visibility chore.",
            complexity=3, deadline_urgency=4, visibility=2, 
            type=TaskType.MAINTENANCE, assignee_id="e1"
        ),
        "t3": Task(
            id="t3", title="OAuth2 Login UI", 
            description="Creating the new frontend login flow for mobile users. High-visibility growth task.",
            complexity=5, deadline_urgency=5, visibility=8, 
            type=TaskType.GROWTH, assignee_id="e2"
        )
    }
    print("✅ Rich Seed Data Loaded: Team expanded to 4 members.")