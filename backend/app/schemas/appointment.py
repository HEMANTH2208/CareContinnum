from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from app.models.appointment import AppointmentStatus, AppointmentType


class AppointmentBase(BaseModel):
    patient_id: int
    doctor_id: int
    appointment_type: AppointmentType
    scheduled_date: datetime
    department: Optional[str] = None
    notes: Optional[str] = None


class AppointmentCreate(AppointmentBase):
    follow_up_task_id: Optional[int] = None


class AppointmentUpdate(BaseModel):
    status: Optional[AppointmentStatus] = None
    scheduled_date: Optional[datetime] = None
    notes: Optional[str] = None
    cancellation_reason: Optional[str] = None
    confirmation_received: Optional[bool] = None


class AppointmentResponse(AppointmentBase):
    id: int
    follow_up_task_id: Optional[int] = None
    status: AppointmentStatus
    completed_date: Optional[datetime] = None
    reschedule_count: int
    reminder_sent: bool
    confirmation_received: bool
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True
