from typing import List
from ..models.employee import Employee, EmployeeStatus
from ..models.task import Task
from ..services.llm_service import get_ai_complexity

def calculate_single_task_load(task: Task) -> float:
    # Formula: (Complexity * Deadline) + (Meeting * Switches) + (HighVis * 1.5)
    base = (task.complexity * task.deadline_urgency)
    overhead = (task.meeting_density * task.context_switches)
    vis = (task.visibility * 1.5) if task.is_high_visibility else task.visibility
    return base + overhead + vis

def update_employee_status(employee: Employee, tasks: List[Task]):
    if not tasks:
        employee.load_score = 0.0
        employee.status = EmployeeStatus.GREEN
        return

    raw_total = 0.0
    for t in tasks:
        # Use AI to determine complexity if it's currently at a default/zero
        if t.complexity == 0:
            ai_vals = get_ai_complexity(t.title)
            t.complexity = ai_vals['complexity']
            t.context_switches = ai_vals['context_switch']
        
        raw_total += calculate_single_task_load(t)
    
    # --- CRITICAL FIX: Lowered denominator to 150 to make burnout easier to detect ---
    # Old: 250 (Too hard to reach Red). New: 150.
    normalized = min(100.0, (raw_total / 150.0) * 100.0)
    
    employee.load_score = round(normalized, 1)

    if employee.load_score > 85:
        employee.status = EmployeeStatus.RED
    elif employee.load_score > 60:
        employee.status = EmployeeStatus.YELLOW
    else:
        employee.status = EmployeeStatus.GREEN