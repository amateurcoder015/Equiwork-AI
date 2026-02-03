import uuid
import json
from .base_agent import BaseAgent
from ..store.db import db
from ..services.llm_service import ask_llm

class RebalanceAgent(BaseAgent):
    def run(self):
        employees = db.get_all_employees()
        overloaded = [e for e in employees if e.status == "Red"]
        underutilized = [e for e in employees if e.status == "Green"]

        if not overloaded or not underutilized:
            return {"status": "Team is balanced.", "actions_proposed": 0}

        # Context for AI
        context = {
            "overloaded": [{"name": e.name, "tasks": [{"id": t.id, "title": t.title} for t in db.get_tasks_by_assignee(e.id)]} for e in overloaded],
            "available": [{"id": e.id, "name": e.name, "skills": e.skills} for e in underutilized]
        }

        prompt = f"Balance this team workload. Return ONLY JSON: {{\"task_id\": \"id\", \"to_emp_id\": \"id\", \"reason\": \"why\"}}. Data: {json.dumps(context)}"

        try:
            raw = ask_llm(prompt)
            start, end = raw.find('{'), raw.rfind('}') + 1
            plan = json.loads(raw[start:end])
            
            intervention = {
                "id": str(uuid.uuid4()),
                "type": "REBALANCE",
                "description": f"AI Suggestion: {plan['reason']}",
                "task_id": plan['task_id'],
                "from_emp": overloaded[0].id,
                "to_emp": plan['to_emp_id']
            }
            db.add_intervention(intervention)
            return {"status": "Success", "actions_proposed": 1}
        except:
            # SAFETY FALLBACK: If AI fails, use the first available person
            victim_tasks = db.get_tasks_by_assignee(overloaded[0].id)
            if victim_tasks:
                fallback = {
                    "id": str(uuid.uuid4()),
                    "type": "REBALANCE",
                    "description": "Rule-based Fallback: Moving task to balance load.",
                    "task_id": victim_tasks[0].id,
                    "from_emp": overloaded[0].id,
                    "to_emp": underutilized[0].id
                }
                db.add_intervention(fallback)
                return {"status": "Success (Fallback Logic)", "actions_proposed": 1}
            return {"status": "Error creating intervention", "actions_proposed": 0}