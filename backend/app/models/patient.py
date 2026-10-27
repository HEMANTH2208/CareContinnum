from sqlalchemy import Column, Integer, String, DateTime, Boolean, Date, ForeignKey, Text, Enum as SQLEnum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base
import enum


class CommunicationPreference(str, enum.Enum):
    EMAIL = "email"
    SMS = "sms"
    PHONE = "phone"
    ALL = "all"


class Patient(Base):
    __tablename__ = "patients"

    id = Column(Integer, primary_key=True, index=True)
    patient_id = Column(String, unique=True, index=True, nullable=False)  # Hospital-assigned ID
    
    # Personal info
    full_name = Column(String, nullable=False, index=True)
    date_of_birth = Column(Date, nullable=False)
    gender = Column(String, nullable=False)
    phone = Column(String, nullable=False)
    email = Column(String, nullable=True)
    address = Column(Text, nullable=True)
    
    # Medical info
    blood_group = Column(String, nullable=True)
    allergies = Column(Text, nullable=True)
    chronic_conditions = Column(Text, nullable=True)
    emergency_contact_name = Column(String, nullable=True)
    emergency_contact_phone = Column(String, nullable=True)
    
    # System fields
    assigned_doctor_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    communication_preference = Column(SQLEnum(CommunicationPreference), default=CommunicationPreference.ALL)
    consent_for_communication = Column(Boolean, default=True)
    is_active = Column(Boolean, default=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    last_visit_date = Column(DateTime(timezone=True), nullable=True)
    
    # Relationships
    assigned_doctor = relationship("User", foreign_keys=[assigned_doctor_id])
    appointments = relationship("Appointment", back_populates="patient")
    follow_up_plans = relationship("FollowUpPlan", back_populates="patient")
    consultations = relationship("Consultation", back_populates="patient")
