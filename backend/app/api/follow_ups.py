from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_
from typing import List, Optional
from datetime import datetime
from app.core.database import get_db
from app.core.dependencies import get_current_user, require_doctor, require_staff_or_doctor
from app.schemas.follow_up import (
    FollowUpPlanCreate, FollowUpPlanUpdate, FollowUpPlanResponse,
    FollowUpTaskCreate, FollowUpTaskUpdate, FollowUpTaskResponse
)
from app.models.follow_up import FollowUpPlan, FollowUpTask, TaskStatus, Priority
from app.models.user import User, UserRole

router = APIRouter()


@router.get("/plans", response_model=List[FollowUpPlanResponse])
def list_follow_up_plans(
    skip: int = 0,
    limit: int = 100,
    patient_id: Optional[int] = None,
    is_active: bool = True,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """List follow-up plans."""
    query = db.query(FollowUpPlan)
    
    if patient_id:
        query = query.filter(FollowUpPlan.patient_id == patient_id)
    if is_active is not None:
        query = query.filter(FollowUpPlan.is_active == is_active)
    
    plans = query.offset(skip).limit(limit).all()
    return plans


@router.post("/plans", response_model=FollowUpPlanResponse, status_code=status.HTTP_201_CREATED)
def create_follow_up_plan(
    plan_data: FollowUpPlanCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_doctor)
):
    """Create new follow-up plan (doctors only)."""
    plan = FollowUpPlan(
        patient_id=plan_data.patient_id,
        doctor_id=plan_data.doctor_id,
        consultation_id=plan_data.consultation_id,
        title=plan_data.title,
        description=plan_data.description,
        priority=plan_data.priority
    )
    
    db.add(plan)
    db.flush()
    
    # Add tasks if provided
    if plan_data.tasks:
        for task_data in plan_data.tasks:
            task = FollowUpTask(
                plan_id=plan.id,
                title=task_data.title,
                description=task_data.description,
                task_type=task_data.task_type,
                due_date=task_data.due_date,
                priority=task_data.priority,
                assigned_department=task_data.assigned_department,
                assigned_staff_id=task_data.assigned_staff_id,
                depends_on_task_id=task_data.depends_on_task_id
            )
            db.add(task)
    
    db.commit()
    db.refresh(plan)
    return plan


@router.get("/plans/{plan_id}", response_model=FollowUpPlanResponse)
def get_follow_up_plan(
    plan_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get follow-up plan by ID."""
    plan = db.query(FollowUpPlan).filter(FollowUpPlan.id == plan_id).first()
    if not plan:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Follow-up plan not found"
        )
    return plan


@router.patch("/plans/{plan_id}", response_model=FollowUpPlanResponse)
def update_follow_up_plan(
    plan_id: int,
    plan_data: FollowUpPlanUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_doctor)
):
    """Update follow-up plan."""
    plan = db.query(FollowUpPlan).filter(FollowUpPlan.id == plan_id).first()
    if not plan:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Follow-up plan not found"
        )
    
    for field, value in plan_data.model_dump(exclude_unset=True).items():
        setattr(plan, field, value)
    
    db.commit()
    db.refresh(plan)
    return plan


@router.get("/tasks", response_model=List[FollowUpTaskResponse])
def list_follow_up_tasks(
    skip: int = 0,
    limit: int = 100,
    plan_id: Optional[int] = None,
    status: Optional[TaskStatus] = None,
    assigned_staff_id: Optional[int] = None,
    is_overdue: Optional[bool] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """List follow-up tasks."""
    query = db.query(FollowUpTask)
    
    if plan_id:
        query = query.filter(FollowUpTask.plan_id == plan_id)
    if status:
        query = query.filter(FollowUpTask.status == status)
    if assigned_staff_id:
        query = query.filter(FollowUpTask.assigned_staff_id == assigned_staff_id)
    if is_overdue is not None:
        query = query.filter(FollowUpTask.is_overdue == is_overdue)
    
    tasks = query.offset(skip).limit(limit).all()
    return tasks


@router.post("/tasks", response_model=FollowUpTaskResponse, status_code=status.HTTP_201_CREATED)
def create_follow_up_task(
    task_data: FollowUpTaskCreate,
    plan_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_doctor)
):
    """Create new follow-up task."""
    task = FollowUpTask(
        plan_id=plan_id,
        title=task_data.title,
        description=task_data.description,
        task_type=task_data.task_type,
        due_date=task_data.due_date,
        priority=task_data.priority,
        assigned_department=task_data.assigned_department,
        assigned_staff_id=task_data.assigned_staff_id,
        depends_on_task_id=task_data.depends_on_task_id
    )
    
    db.add(task)
    db.commit()
    db.refresh(task)
    return task


@router.patch("/tasks/{task_id}", response_model=FollowUpTaskResponse)
def update_follow_up_task(
    task_id: int,
    task_data: FollowUpTaskUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_staff_or_doctor)
):
    """Update follow-up task."""
    task = db.query(FollowUpTask).filter(FollowUpTask.id == task_id).first()
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        )
    
    # Handle status changes
    old_status = task.status
    
    for field, value in task_data.model_dump(exclude_unset=True).items():
        setattr(task, field, value)
    
    # Auto-set completion date
    if task_data.status == TaskStatus.COMPLETED and old_status != TaskStatus.COMPLETED:
        task.completed_date = datetime.utcnow()
    
    db.commit()
    db.refresh(task)
    return task


@router.get("/worklist/priority", response_model=List[dict])
def get_priority_worklist(
    limit: int = 50,
    department: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_staff_or_doctor)
):
    """Get explainable priority worklist for staff."""
    now = datetime.utcnow()
    
    # Get unresolved tasks
    query = db.query(FollowUpTask).filter(
        FollowUpTask.status.in_([TaskStatus.PENDING, TaskStatus.SCHEDULED, TaskStatus.BLOCKED, TaskStatus.ESCALATED])
    )
    
    if department:
        query = query.filter(FollowUpTask.assigned_department == department)
    
    tasks = query.all()
    
    # Calculate priority score and reason
    priority_list = []
    for task in tasks:
        score = 0
        reasons = []
        
        # Overdue
        if task.due_date < now:
            days_overdue = (now - task.due_date).days
            score += days_overdue * 10
            reasons.append(f"Overdue by {days_overdue} days")
            task.is_overdue = True
        
        # Priority level
        priority_scores = {Priority.URGENT: 50, Priority.HIGH: 30, Priority.MEDIUM: 10, Priority.LOW: 0}
        score += priority_scores.get(task.priority, 0)
        if task.priority in [Priority.URGENT, Priority.HIGH]:
            reasons.append(f"Priority: {task.priority.value}")
        
        # Escalated
        if task.status == TaskStatus.ESCALATED:
            score += 100
            reasons.append("Escalated")
        
        # Blocked
        if task.status == TaskStatus.BLOCKED:
            score += 40
            reasons.append("Blocked - dependency issue")
        
        # Failed contact attempts
        if task.contact_attempts >= 3:
            score += task.contact_attempts * 5
            reasons.append(f"{task.contact_attempts} contact attempts")
        
        priority_list.append({
            "task": task,
            "score": score,
            "reasons": reasons,
            "next_action": _determine_next_action(task)
        })
    
    # Sort by score descending
    priority_list.sort(key=lambda x: x["score"], reverse=True)
    
    db.commit()  # Save is_overdue updates
    
    return priority_list[:limit]


def _determine_next_action(task: FollowUpTask) -> str:
    """Determine the next operational action for a task."""
    if task.status == TaskStatus.BLOCKED:
        return "Resolve dependency or escalate to doctor"
    elif task.status == TaskStatus.ESCALATED:
        return "Manager review required"
    elif task.contact_attempts >= 3:
        return "Escalate or attempt alternative contact method"
    elif task.is_overdue:
        return "Contact patient and reschedule immediately"
    elif not task.assigned_staff_id:
        return "Assign to staff member"
    else:
        return "Contact patient to schedule"
