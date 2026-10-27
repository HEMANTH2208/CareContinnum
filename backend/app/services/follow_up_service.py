from sqlalchemy.orm import Session
from sqlalchemy import and_, or_
from fastapi import HTTPException
from typing import List, Optional
from datetime import datetime, timedelta
from app.models.follow_up import FollowUpPlan, FollowUpTask, TaskStatus, Priority
from app.schemas.follow_up import FollowUpPlanCreate, FollowUpTaskCreate, FollowUpTaskUpdate
from app.core.config import settings


def create_follow_up_plan(db: Session, plan_data: FollowUpPlanCreate) -> FollowUpPlan:
    """Create a new follow-up plan with tasks."""
    db_plan = FollowUpPlan(
        patient_id=plan_data.patient_id,
        doctor_id=plan_data.doctor_id,
        consultation_id=plan_data.consultation_id,
        title=plan_data.title,
        description=plan_data.description,
        priority=plan_data.priority
    )
    
    db.add(db_plan)
    db.flush()  # Get the plan ID
    
    # Create tasks if provided
    if plan_data.tasks:
        for task_data in plan_data.tasks:
            db_task = FollowUpTask(
                plan_id=db_plan.id,
                title=task_data.title,
                description=task_data.description,
                task_type=task_data.task_type,
                due_date=task_data.due_date,
                priority=task_data.priority,
                assigned_department=task_data.assigned_department,
                assigned_staff_id=task_data.assigned_staff_id,
                depends_on_task_id=task_data.depends_on_task_id
            )
            db.add(db_task)
    
    db.commit()
    db.refresh(db_plan)
    
    return db_plan


def update_task_status(db: Session, task_id: int, update_data: FollowUpTaskUpdate) -> FollowUpTask:
    """Update follow-up task status and related fields."""
    task = db.query(FollowUpTask).filter(FollowUpTask.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    
    update_dict = update_data.model_dump(exclude_unset=True)
    
    # If status is completed, set completion date
    if update_data.status == TaskStatus.COMPLETED and not update_data.completed_date:
        update_dict['completed_date'] = datetime.utcnow()
    
    for field, value in update_dict.items():
        setattr(task, field, value)
    
    db.commit()
    db.refresh(task)
    
    return task


def get_overdue_tasks(db: Session) -> List[FollowUpTask]:
    """Get all overdue tasks that are not completed or cancelled."""
    now = datetime.utcnow()
    return db.query(FollowUpTask).filter(
        and_(
            FollowUpTask.due_date < now,
            FollowUpTask.status.in_([TaskStatus.PENDING, TaskStatus.SCHEDULED, TaskStatus.IN_PROGRESS]),
            FollowUpTask.is_overdue == False
        )
    ).all()


def mark_tasks_overdue(db: Session) -> int:
    """Mark overdue tasks and return count."""
    overdue_tasks = get_overdue_tasks(db)
    
    for task in overdue_tasks:
        task.is_overdue = True
    
    db.commit()
    return len(overdue_tasks)


def escalate_task(db: Session, task_id: int, reason: str) -> FollowUpTask:
    """Escalate a task due to failure conditions."""
    task = db.query(FollowUpTask).filter(FollowUpTask.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    
    task.status = TaskStatus.ESCALATED
    task.escalated_at = datetime.utcnow()
    task.escalation_reason = reason
    
    db.commit()
    db.refresh(task)
    
    return task


def get_priority_worklist(db: Session, department: Optional[str] = None) -> List[dict]:
    """Get prioritized list of unresolved cases with explanation."""
    # Get all unresolved tasks
    query = db.query(FollowUpTask).filter(
        FollowUpTask.status.in_([
            TaskStatus.PENDING,
            TaskStatus.SCHEDULED,
            TaskStatus.IN_PROGRESS,
            TaskStatus.BLOCKED,
            TaskStatus.ESCALATED
        ])
    )
    
    if department:
        query = query.filter(FollowUpTask.assigned_department == department)
    
    tasks = query.all()
    
    # Calculate priority scores and reasons
    worklist = []
    now = datetime.utcnow()
    
    for task in tasks:
        score = 0
        reasons = []
        
        # Escalated tasks get highest priority
        if task.status == TaskStatus.ESCALATED:
            score += 100
            reasons.append(f"Escalated: {task.escalation_reason}")
        
        # Overdue duration
        if task.is_overdue:
            days_overdue = (now - task.due_date).days
            score += days_overdue * 10
            reasons.append(f"Overdue by {days_overdue} days")
        
        # Approaching deadline
        elif task.due_date:
            days_until_due = (task.due_date - now).days
            if days_until_due <= 3:
                score += (4 - days_until_due) * 5
                reasons.append(f"Due in {days_until_due} days")
        
        # Contact attempts
        if task.contact_attempts >= settings.MAX_CONTACT_ATTEMPTS - 1:
            score += 30
            reasons.append(f"High contact attempts: {task.contact_attempts}")
        
        # Blocked tasks
        if task.status == TaskStatus.BLOCKED:
            score += 20
            reasons.append("Task is blocked")
        
        # Priority level
        priority_scores = {
            Priority.LOW: 1,
            Priority.MEDIUM: 5,
            Priority.HIGH: 15,
            Priority.URGENT: 30
        }
        score += priority_scores.get(task.priority, 0)
        reasons.append(f"Priority: {task.priority.value}")
        
        worklist.append({
            "task": task,
            "priority_score": score,
            "priority_reasons": reasons,
            "next_action": _get_next_action(task)
        })
    
    # Sort by priority score (highest first)
    worklist.sort(key=lambda x: x["priority_score"], reverse=True)
    
    return worklist


def _get_next_action(task: FollowUpTask) -> str:
    """Determine next operational action for a task."""
    if task.status == TaskStatus.ESCALATED:
        return "Review escalation and assign resolution"
    elif task.status == TaskStatus.BLOCKED:
        return "Resolve blocking issue"
    elif task.is_overdue:
        return "Contact patient immediately"
    elif not task.assigned_staff_id:
        return "Assign to staff member"
    elif task.status == TaskStatus.PENDING:
        return "Schedule appointment"
    elif task.status == TaskStatus.SCHEDULED:
        return "Send reminder"
    else:
        return "Follow up with patient"


def record_contact_attempt(db: Session, task_id: int) -> FollowUpTask:
    """Record a contact attempt for a task."""
    task = db.query(FollowUpTask).filter(FollowUpTask.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    
    task.contact_attempts += 1
    task.last_contact_date = datetime.utcnow()
    
    # Check if limit reached
    if task.contact_attempts >= settings.MAX_CONTACT_ATTEMPTS:
        task = escalate_task(db, task_id, f"Maximum contact attempts ({settings.MAX_CONTACT_ATTEMPTS}) reached")
    else:
        db.commit()
        db.refresh(task)
    
    return task
