from typing import List
from ..models.employee import Employee, EmployeeStatus
from ..models.task import Task
from ..services.llm_service import get_ai_complexity

def update_employee_status(employee, tasks):
    if not tasks:
        employee.load_score = 0
        employee.status = "Green"
        return

    raw_total = 0
    for t in tasks:
        # Use AI to determine complexity if it's currently at a default/zero
        if t.complexity == 0:
            ai_vals = get_ai_complexity(t.title)
            t.complexity = ai_vals['complexity']
            t.context_switches = ai_vals['context_switch']
        
        # Formula from your original code
        base = (t.complexity * t.deadline_urgency)
        overhead = (t.meeting_density * t.context_switches)
        raw_total += (base + overhead)
    
    normalized = min(100, (raw_total / 250) * 100)
    employee.load_score = round(normalized, 1)
    # ... rest of your status logic (RED/YELLOW/GREEN) ...

    if employee.load_score > 85:
        employee.status = EmployeeStatus.RED
    elif employee.load_score > 60:
        employee.status = EmployeeStatus.YELLOW
    else:
        employee.status = EmployeeStatus.GREEN