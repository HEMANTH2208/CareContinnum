from sqlalchemy import Column, Integer, String, DateTime, Boolean, ForeignKey, Text, Enum as SQLEnum, Float
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base
import enum


class ConsultationType(str, enum.Enum):
    IN_PERSON = "in_person"
    ONLINE = "online"
    EMERGENCY = "emergency"
    FOLLOW_UP = "follow_up"


class PrescriptionStatus(str, enum.Enum):
    DRAFT = "draft"
    ACTIVE = "active"
    DISPENSED = "dispensed"
    EXPIRED = "expired"
    CANCELLED = "cancelled"


class Consultation(Base):
    __tablename__ = "consultations"

    id = Column(Integer, primary_key=True, index=True)
    patient_id = Column(Integer, ForeignKey("patients.id"), nullable=False, index=True)
    doctor_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    appointment_id = Column(Integer, ForeignKey("appointments.id"), nullable=True)
    
    consultation_type = Column(SQLEnum(ConsultationType), nullable=False)
    consultation_date = Column(DateTime(timezone=True), nullable=False, index=True)
    
    # Clinical information
    chief_complaint = Column(Text, nullable=True)
    present_illness = Column(Text, nullable=True)
    examination_findings = Column(Text, nullable=True)
    diagnosis = Column(Text, nullable=True)
    treatment_plan = Column(Text, nullable=True)
    
    # Vital signs (stored as JSON or separate fields)
    temperature = Column(Float, nullable=True)
    blood_pressure_systolic = Column(Integer, nullable=True)
    blood_pressure_diastolic = Column(Integer, nullable=True)
    pulse_rate = Column(Integer, nullable=True)
    respiratory_rate = Column(Integer, nullable=True)
    oxygen_saturation = Column(Float, nullable=True)
    
    # Additional notes
    notes = Column(Text, nullable=True)
    next_visit_date = Column(DateTime(timezone=True), nullable=True)
    
    # AI summary
    ai_summary = Column(Text, nullable=True)
    ai_summary_reviewed = Column(Boolean, default=False)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    patient = relationship("Patient", back_populates="consultations")
    doctor = relationship("User", foreign_keys=[doctor_id])
    appointment = relationship("Appointment")
    prescriptions = relationship("Prescription", back_populates="consultation")
    follow_up_plans = relationship("FollowUpPlan", back_populates="consultation")


class Prescription(Base):
    __tablename__ = "prescriptions"

    id = Column(Integer, primary_key=True, index=True)
    consultation_id = Column(Integer, ForeignKey("consultations.id"), nullable=False, index=True)
    patient_id = Column(Integer, ForeignKey("patients.id"), nullable=False, index=True)
    doctor_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    prescription_number = Column(String, unique=True, nullable=False, index=True)
    status = Column(SQLEnum(PrescriptionStatus), default=PrescriptionStatus.ACTIVE)
    
    # Medications (stored as JSON array in production, or separate table)
    medications = Column(Text, nullable=False)  # JSON string: [{"name": "...", "dosage": "...", ...}]
    
    # Instructions
    general_instructions = Column(Text, nullable=True)
    dietary_advice = Column(Text, nullable=True)
    
    # Dates
    issued_date = Column(DateTime(timezone=True), server_default=func.now())
    valid_until = Column(DateTime(timezone=True), nullable=True)
    dispensed_date = Column(DateTime(timezone=True), nullable=True)
    
    # PDF
    pdf_generated = Column(Boolean, default=False)
    pdf_path = Column(String, nullable=True)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    consultation = relationship("Consultation", back_populates="prescriptions")
    patient = relationship("Patient")
    doctor = relationship("User", foreign_keys=[doctor_id])
