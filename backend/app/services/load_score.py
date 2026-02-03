from typing import List
from ..models.employee import Employee, EmployeeStatus
from ..models.task import Task

def calculate_single_task_load(task: Task) -> float:
    # Formula: (Complexity * Deadline) + (Meeting * Switches) + (HighVis * 1.5)
    base = (task.complexity * task.deadline_urgency)
    overhead = (task.meeting_density * task.context_switches)
    vis = (task.visibility * 1.5) if task.is_high_visibility else task.visibility
    return base + overhead + vis

def update_employee_status(employee: Employee, tasks: List[Task]):
    if not tasks:
        employee.load_score = 0
        employee.status = EmployeeStatus.GREEN
        return

    raw_total = sum(calculate_single_task_load(t) for t in tasks)
    
    # Normalize: We assume ~250 is max possible load for one person
    normalized = min(100, (raw_total / 250) * 100)
    
    employee.load_score = round(normalized, 1)

    if employee.load_score > 85:
        employee.status = EmployeeStatus.RED
    elif employee.load_score > 60:
        employee.status = EmployeeStatus.YELLOW
    else:
        employee.status = EmployeeStatus.GREEN