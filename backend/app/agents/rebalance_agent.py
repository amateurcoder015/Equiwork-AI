import uuid
from .base_agent import BaseAgent
from ..store.db import db
from ..services.load_score import update_employee_status
from ..models.employee import EmployeeStatus

class RebalanceAgent(BaseAgent):
    def run(self):
        # 1. Update all scores first
        employees = db.get_all_employees()
        for emp in employees:
            tasks = db.get_tasks_by_assignee(emp.id)
            update_employee_status(emp, tasks)
            db.update_employee(emp)

        # 2. Identify Burnout (RED) vs Opportunity (GREEN)
        overloaded = [e for e in employees if e.status == EmployeeStatus.RED]
        underutilized = [e for e in employees if e.status == EmployeeStatus.GREEN]

        if not overloaded:
            return {"status": "No burnout detected", "actions": 0}

        # 3. Plan Interventions
        actions_proposed = 0
        for victim in overloaded:
            # Find their hardest task
            victim_tasks = db.get_tasks_by_assignee(victim.id)
            victim_tasks.sort(key=lambda t: t.complexity, reverse=True)
            
            if not victim_tasks or not underutilized:
                continue

            task_to_move = victim_tasks[0]
            receiver = underutilized[0] # Simplest logic: pick first available

            # 4. Propose Action (Don't execute yet)
            intervention = {
                "id": str(uuid.uuid4()),
                "type": "REBALANCE",
                "description": f"Move '{task_to_move.title}' from {victim.name} (Load: {victim.load_score}) to {receiver.name} (Load: {receiver.load_score})",
                "task_id": task_to_move.id,
                "from_emp": victim.id,
                "to_emp": receiver.id
            }
            
            # Prevent duplicate proposals
            existing = [i for i in db.get_interventions() if i['task_id'] == task_to_move.id]
            if not existing:
                db.add_intervention(intervention)
                actions_proposed += 1

        return {"status": "Success", "actions_proposed": actions_proposed}