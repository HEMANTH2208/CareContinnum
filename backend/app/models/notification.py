from sqlalchemy import Column, Integer, String, DateTime, Boolean, ForeignKey, Text, Enum as SQLEnum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base
import enum


class NotificationType(str, enum.Enum):
    APPOINTMENT_REMINDER = "appointment_reminder"
    APPOINTMENT_CONFIRMATION = "appointment_confirmation"
    APPOINTMENT_CANCELLED = "appointment_cancelled"
    FOLLOW_UP_DUE = "follow_up_due"
    PRESCRIPTION_READY = "prescription_ready"
    RESULT_AVAILABLE = "result_available"
    GENERAL = "general"


class NotificationChannel(str, enum.Enum):
    EMAIL = "email"
    SMS = "sms"
    PHONE = "phone"
    IN_APP = "in_app"


class NotificationStatus(str, enum.Enum):
    PENDING = "pending"
    SENT = "sent"
    DELIVERED = "delivered"
    FAILED = "failed"
    CANCELLED = "cancelled"


class Notification(Base):
    __tablename__ = "notifications"

    id = Column(Integer, primary_key=True, index=True)
    patient_id = Column(Integer, ForeignKey("patients.id"), nullable=False, index=True)
    appointment_id = Column(Integer, ForeignKey("appointments.id"), nullable=True)
    follow_up_task_id = Column(Integer, ForeignKey("follow_up_tasks.id"), nullable=True)
    
    notification_type = Column(SQLEnum(NotificationType), nullable=False)
    channel = Column(SQLEnum(NotificationChannel), nullable=False)
    status = Column(SQLEnum(NotificationStatus), default=NotificationStatus.PENDING, index=True)
    
    subject = Column(String, nullable=True)
    message = Column(Text, nullable=False)
    
    scheduled_for = Column(DateTime(timezone=True), nullable=False, index=True)
    sent_at = Column(DateTime(timezone=True), nullable=True)
    delivered_at = Column(DateTime(timezone=True), nullable=True)
    
    attempt_count = Column(Integer, default=0)
    max_attempts = Column(Integer, default=3)
    
    error_message = Column(Text, nullable=True)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    patient = relationship("Patient")
    appointment = relationship("Appointment")
    follow_up_task = relationship("FollowUpTask")
    attempts = relationship("NotificationAttempt", back_populates="notification", cascade="all, delete-orphan")


class NotificationAttempt(Base):
    __tablename__ = "notification_attempts"

    id = Column(Integer, primary_key=True, index=True)
    notification_id = Column(Integer, ForeignKey("notifications.id"), nullable=False, index=True)
    
    attempted_at = Column(DateTime(timezone=True), server_default=func.now())
    status = Column(String, nullable=False)  # "sent", "failed", "delivered"
    error_message = Column(Text, nullable=True)
    delivery_details = Column(Text, nullable=True)  # JSON string with provider response
    
    # Relationships
    notification = relationship("Notification", back_populates="attempts")
