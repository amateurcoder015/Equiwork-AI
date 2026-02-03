from fastapi import APIRouter, HTTPException
from ..store.db import db
from ..agents.rebalance_agent import RebalanceAgent
from ..services.load_score import update_employee_status

router = APIRouter()
agent = RebalanceAgent()

# --- Data Endpoints ---
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

# --- Agent Endpoints ---
@router.post("/agent/run")
def run_agent():
    result = agent.run()
    return result

@router.get("/agent/interventions")
def get_interventions():
    return db.get_interventions()

@router.post("/agent/approve/{intervention_id}")
def approve_intervention(intervention_id: str):
    # Find intervention
    interventions = db.get_interventions()
    target = next((i for i in interventions if i["id"] == intervention_id), None)
    
    if not target:
        raise HTTPException(status_code=404, detail="Intervention not found")

    # EXECUTE THE PLAN
    db.update_task_assignee(target["task_id"], target["to_emp"])
    
    # Cleanup
    db.remove_intervention(intervention_id)
    return {"status": "Approved", "msg": "Workload rebalanced."}

@router.post("/agent/dismiss/{intervention_id}")
def dismiss_intervention(intervention_id: str):
    db.remove_intervention(intervention_id)
    return {"status": "Dismissed"}