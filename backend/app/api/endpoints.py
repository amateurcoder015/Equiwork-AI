from fastapi import APIRouter, HTTPException
from ..store.db import db
from ..agents.rebalance_agent import RebalanceAgent
from ..services.load_score import update_employee_status
from ..models.task import Task, TaskType
from ..seed.demo_data import seed_data
import uuid

router = APIRouter()
agent = RebalanceAgent()

@router.post("/reset")
def reset_database():
    """Wipes the current state and re-seeds the demo scenario."""
    db.employees.clear()
    db.tasks.clear()
    db.interventions.clear()
    seed_data()
    return {"status": "Database reset successful"}

@router.post("/sync/jira")
def sync_jira():
    """Simulates fetching new high-priority tasks from Jira for Alice (e1)"""
    new_tasks = [
        Task(
            id=str(uuid.uuid4()),
            title="Emergency Server Patch",
            description="Patching a critical zero-day vulnerability. Requires immediate attention.",
            complexity=9,
            deadline_urgency=10,
            visibility=10, 
            type=TaskType.MAINTENANCE,
            assignee_id="e1" 
        ),
        Task(
            id=str(uuid.uuid4()),
            title="Fix Memory Leak",
            description="Investigating memory leak in auth module.",
            complexity=8,
            deadline_urgency=8,
            visibility=5,
            type=TaskType.MAINTENANCE,
            assignee_id="e1"
        )
    ]
    for t in new_tasks:
        db.tasks[t.id] = t
    return {"status": "Synced", "new_tasks": len(new_tasks)}

@router.get("/team")
def get_team():
    # Refresh scores before returning
    for emp in db.get_all_employees():
        tasks = db.get_tasks_by_assignee(emp.id)
        update_employee_status(emp, tasks)
    return db.get_all_employees()

@router.get("/tasks")
def get_tasks():
    return list(db.tasks.values())

@router.post("/agent/run")
def run_agent():
    result = agent.run()
    return result

@router.get("/agent/interventions")
def get_interventions():
    return db.get_interventions()

@router.post("/agent/approve/{intervention_id}")
def approve_intervention(intervention_id: str):
    interventions = db.get_interventions()
    target = next((i for i in interventions if i["id"] == intervention_id), None)
    
    if not target:
        raise HTTPException(status_code=404, detail="Intervention not found")

    db.update_task_assignee(target["task_id"], target["to_emp"])
    db.remove_intervention(intervention_id)
    return {"status": "Approved", "msg": "Workload rebalanced."}

@router.post("/agent/dismiss/{intervention_id}")
def dismiss_intervention(intervention_id: str):
    db.remove_intervention(intervention_id)
    return {"status": "Dismissed"}