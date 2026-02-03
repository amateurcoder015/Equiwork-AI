import uuid
import json
import traceback
from .base_agent import BaseAgent
from ..store.db import db
from ..services.llm_service import ask_llm
from ..services.load_score import update_employee_status

class RebalanceAgent(BaseAgent):
    def run(self):
        try:
            # 1. FORCE REFRESH: Recalculate scores for everyone
            employees = db.get_all_employees()
            for emp in employees:
                tasks = db.get_tasks_by_assignee(emp.id)
                update_employee_status(emp, tasks)
                db.update_employee(emp)

            # 2. Identify Burnout
            overloaded = [e for e in employees if e.status == "Red"]
            underutilized = [e for e in employees if e.status == "Green"]

            if not overloaded or not underutilized:
                return {"status": "Team is balanced.", "actions_proposed": 0}

            # 3. Context for AI
            context = {
                "overloaded": [{
                    "name": e.name, 
                    "role": e.skills[0] if e.skills else "General", # Give AI a hint about role
                    "tasks": [{"id": t.id, "title": t.title, "desc": t.description} for t in db.get_tasks_by_assignee(e.id)]
                } for e in overloaded],
                "available": [{
                    "id": e.id, 
                    "name": e.name, 
                    "skills": e.skills
                } for e in underutilized]
            }

            prompt = f"""
            You are a Technical Project Manager.
            Team Data: {json.dumps(context)}
            
            Task: Move ONE task from an overloaded person to the BEST MATCH available person.
            
            CRITICAL RULES:
            1. STRICTLY MATCH SKILLS. Do not give "Backend" tasks to "Designers".
            2. If task mentions "Python/DB", assign to Python/AWS skills.
            3. If task mentions "UI/Figma", assign to React/Design skills.
            
            Return ONLY JSON:
            {{
                "task_id": "id",
                "to_emp_id": "id",
                "reason": "Explain the skill match (e.g. 'Matched Python task to Python developer')"
            }}
            """

            # 4. AI Call
            raw = ask_llm(prompt)
            if not raw:
                raise ValueError("AI returned empty response")

            clean_raw = raw.replace("```json", "").replace("```", "").strip()
            start, end = clean_raw.find('{'), clean_raw.rfind('}') + 1
            plan = json.loads(clean_raw[start:end])
            
            # Validate Task ID exists
            task_check = db.get_task(plan['task_id'])
            if not task_check:
                 raise ValueError("AI hallucinated a task ID")

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

        except Exception as e:
            print(f"Agent Fallback triggered: {e}")
            
            # --- SMART FALLBACK LOGIC ---
            # If AI fails, we solve it with code.
            
            # Get fresh data again
            employees = db.get_all_employees()
            overloaded = [e for e in employees if e.status == "Red"]
            underutilized = [e for e in employees if e.status == "Green"]

            if overloaded and underutilized:
                victim = overloaded[0]
                victim_tasks = db.get_tasks_by_assignee(victim.id)
                
                # Sort tasks by complexity (move the hardest one first)
                victim_tasks.sort(key=lambda t: t.complexity, reverse=True)
                task_to_move = victim_tasks[0]

                # Find best candidate based on keyword matching
                best_candidate = None
                best_score = -1

                task_keywords = set(task_to_move.title.lower().split() + task_to_move.description.lower().split())
                
                for candidate in underutilized:
                    # Simple score: how many candidate skills appear in the task text?
                    candidate_skills = set(s.lower() for s in candidate.skills)
                    # Check partial matches (e.g. "sql" in "postgresql")
                    score = 0
                    for skill in candidate_skills:
                        for word in task_keywords:
                            if skill in word or word in skill:
                                score += 1
                    
                    if score > best_score:
                        best_score = score
                        best_candidate = candidate
                
                # If no skills matched (score 0), just pick the person with lowest load
                if not best_candidate or best_score == 0:
                    best_candidate = min(underutilized, key=lambda e: e.load_score)
                    reason = "Rule-based: Picked least loaded member (No skill match found)."
                else:
                    reason = f"Rule-based: Matched skills ({', '.join(best_candidate.skills)}) to task."

                fallback = {
                    "id": str(uuid.uuid4()),
                    "type": "REBALANCE",
                    "description": reason,
                    "task_id": task_to_move.id,
                    "from_emp": victim.id,
                    "to_emp": best_candidate.id
                }
                db.add_intervention(fallback)
                return {"status": "Success (Smart Fallback)", "actions_proposed": 1}
            
            return {"status": f"Error: {str(e)}", "actions_proposed": 0}
            