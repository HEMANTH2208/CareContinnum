from sqlalchemy import Column, Integer, String, DateTime, Boolean, ForeignKey, Text, Enum as SQLEnum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base
import enum


class Priority(str, enum.Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    URGENT = "urgent"


class TaskStatus(str, enum.Enum):
    PENDING = "pending"
    SCHEDULED = "scheduled"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    BLOCKED = "blocked"
    ESCALATED = "escalated"
    CANCELLED = "cancelled"


class FollowUpPlan(Base):
    __tablename__ = "follow_up_plans"

    id = Column(Integer, primary_key=True, index=True)
    patient_id = Column(Integer, ForeignKey("patients.id"), nullable=False, index=True)
    doctor_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    consultation_id = Column(Integer, ForeignKey("consultations.id"), nullable=True)
    
    title = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    priority = Column(SQLEnum(Priority), default=Priority.MEDIUM)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    completed_at = Column(DateTime(timezone=True), nullable=True)
    
    is_active = Column(Boolean, default=True)
    
    # Relationships
    patient = relationship("Patient", back_populates="follow_up_plans")
    doctor = relationship("User", foreign_keys=[doctor_id])
    consultation = relationship("Consultation", back_populates="follow_up_plans")
    tasks = relationship("FollowUpTask", back_populates="plan", cascade="all, delete-orphan")


class FollowUpTask(Base):
    __tablename__ = "follow_up_tasks"

    id = Column(Integer, primary_key=True, index=True)
    plan_id = Column(Integer, ForeignKey("follow_up_plans.id"), nullable=False, index=True)
    
    title = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    task_type = Column(String, nullable=False)  # e.g., "lab_test", "imaging", "consultation", "procedure"
    
    status = Column(SQLEnum(TaskStatus), default=TaskStatus.PENDING, index=True)
    priority = Column(SQLEnum(Priority), default=Priority.MEDIUM)
    
    due_date = Column(DateTime(timezone=True), nullable=False, index=True)
    completed_date = Column(DateTime(timezone=True), nullable=True)
    
    # Assignment
    assigned_department = Column(String, nullable=True)
    assigned_staff_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    
    # Dependencies
    depends_on_task_id = Column(Integer, ForeignKey("follow_up_tasks.id"), nullable=True)
    
    # Escalation tracking
    is_overdue = Column(Boolean, default=False, index=True)
    escalated_at = Column(DateTime(timezone=True), nullable=True)
    escalation_reason = Column(Text, nullable=True)
    
    # Contact attempts
    contact_attempts = Column(Integer, default=0)
    last_contact_date = Column(DateTime(timezone=True), nullable=True)
    
    # Results/notes
    result = Column(Text, nullable=True)
    notes = Column(Text, nullable=True)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    plan = relationship("FollowUpPlan", back_populates="tasks")
    assigned_staff = relationship("User", foreign_keys=[assigned_staff_id])
    depends_on_task = relationship("FollowUpTask", remote_side=[id], foreign_keys=[depends_on_task_id])
    appointment = relationship("Appointment", back_populates="follow_up_task", uselist=False)
