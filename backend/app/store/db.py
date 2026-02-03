from typing import List, Dict, Optional
from ..models.employee import Employee
from ..models.task import Task
from ..models.team import Team

class InMemoryDB:
    def __init__(self):
        self.employees: Dict[str, Employee] = {}
        self.tasks: Dict[str, Task] = {}
        self.teams: Dict[str, Team] = {}
        self.interventions: List[Dict] = [] # Pending agent actions

    # --- Data Access Methods ---
    def get_all_employees(self) -> List[Employee]:
        return list(self.employees.values())

    def get_employee(self, emp_id: str) -> Optional[Employee]:
        return self.employees.get(emp_id)

    def update_employee(self, employee: Employee):
        self.employees[employee.id] = employee

    def get_tasks_by_assignee(self, assignee_id: str) -> List[Task]:
        return [t for t in self.tasks.values() if t.assignee_id == assignee_id]

    def get_task(self, task_id: str) -> Optional[Task]:
        return self.tasks.get(task_id)

    def update_task_assignee(self, task_id: str, new_assignee_id: str):
        if task_id in self.tasks:
            self.tasks[task_id].assignee_id = new_assignee_id

    # --- Intervention Methods ---
    def add_intervention(self, intervention: Dict):
        self.interventions.append(intervention)

    def get_interventions(self) -> List[Dict]:
        return self.interventions

    def remove_intervention(self, intervention_id: str):
        self.interventions = [i for i in self.interventions if i.get("id") != intervention_id]

# Singleton Instance
db = InMemoryDB()