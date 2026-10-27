from sqlalchemy import Column, Integer, String, DateTime, Boolean, ForeignKey, Text, Enum as SQLEnum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base
import enum


class AppointmentStatus(str, enum.Enum):
    SCHEDULED = "scheduled"
    CONFIRMED = "confirmed"
    COMPLETED = "completed"
    MISSED = "missed"
    CANCELLED = "cancelled"
    RESCHEDULED = "rescheduled"


class AppointmentType(str, enum.Enum):
    CONSULTATION = "consultation"
    FOLLOW_UP = "follow_up"
    CHECKUP = "checkup"
    PROCEDURE = "procedure"
    ONLINE = "online"


class Appointment(Base):
    __tablename__ = "appointments"

    id = Column(Integer, primary_key=True, index=True)
    patient_id = Column(Integer, ForeignKey("patients.id"), nullable=False, index=True)
    doctor_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    follow_up_task_id = Column(Integer, ForeignKey("follow_up_tasks.id"), nullable=True)
    
    appointment_type = Column(SQLEnum(AppointmentType), nullable=False)
    status = Column(SQLEnum(AppointmentStatus), default=AppointmentStatus.SCHEDULED, index=True)
    
    scheduled_date = Column(DateTime(timezone=True), nullable=False, index=True)
    completed_date = Column(DateTime(timezone=True), nullable=True)
    
    department = Column(String, nullable=True)
    notes = Column(Text, nullable=True)
    cancellation_reason = Column(Text, nullable=True)
    
    # Rescheduling tracking
    reschedule_count = Column(Integer, default=0)
    original_appointment_id = Column(Integer, ForeignKey("appointments.id"), nullable=True)
    
    # Reminders
    reminder_sent = Column(Boolean, default=False)
    confirmation_received = Column(Boolean, default=False)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    patient = relationship("Patient", back_populates="appointments")
    doctor = relationship("User", foreign_keys=[doctor_id])
    follow_up_task = relationship("FollowUpTask", back_populates="appointment")
    original_appointment = relationship("Appointment", remote_side=[id], foreign_keys=[original_appointment_id])
