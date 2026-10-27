from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
from app.models.follow_up import Priority, TaskStatus


class FollowUpTaskBase(BaseModel):
    title: str
    description: Optional[str] = None
    task_type: str
    due_date: datetime
    priority: Priority = Priority.MEDIUM
    assigned_department: Optional[str] = None
    assigned_staff_id: Optional[int] = None
    depends_on_task_id: Optional[int] = None


class FollowUpTaskCreate(FollowUpTaskBase):
    pass


class FollowUpTaskUpdate(BaseModel):
    status: Optional[TaskStatus] = None
    assigned_staff_id: Optional[int] = None
    notes: Optional[str] = None
    result: Optional[str] = None
    completed_date: Optional[datetime] = None


class FollowUpTaskResponse(FollowUpTaskBase):
    id: int
    plan_id: int
    status: TaskStatus
    completed_date: Optional[datetime] = None
    is_overdue: bool
    escalated_at: Optional[datetime] = None
    escalation_reason: Optional[str] = None
    contact_attempts: int
    last_contact_date: Optional[datetime] = None
    result: Optional[str] = None
    notes: Optional[str] = None
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class FollowUpPlanBase(BaseModel):
    patient_id: int
    doctor_id: int
    title: str
    description: Optional[str] = None
    priority: Priority = Priority.MEDIUM


class FollowUpPlanCreate(FollowUpPlanBase):
    consultation_id: Optional[int] = None
    tasks: Optional[List[FollowUpTaskCreate]] = None


class FollowUpPlanUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    priority: Optional[Priority] = None
    is_active: Optional[bool] = None


class FollowUpPlanResponse(FollowUpPlanBase):
    id: int
    consultation_id: Optional[int] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    is_active: bool
    tasks: List[FollowUpTaskResponse] = []

    class Config:
        from_attributes = True
