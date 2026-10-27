from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
from app.models.consultation import ConsultationType, PrescriptionStatus


class MedicationItem(BaseModel):
    name: str
    dosage: str
    frequency: str
    duration: str
    instructions: Optional[str] = None


class ConsultationBase(BaseModel):
    patient_id: int
    doctor_id: int
    consultation_type: ConsultationType
    consultation_date: datetime
    chief_complaint: Optional[str] = None
    present_illness: Optional[str] = None
    examination_findings: Optional[str] = None
    diagnosis: Optional[str] = None
    treatment_plan: Optional[str] = None
    notes: Optional[str] = None
    next_visit_date: Optional[datetime] = None


class ConsultationCreate(ConsultationBase):
    appointment_id: Optional[int] = None
    temperature: Optional[float] = None
    blood_pressure_systolic: Optional[int] = None
    blood_pressure_diastolic: Optional[int] = None
    pulse_rate: Optional[int] = None
    respiratory_rate: Optional[int] = None
    oxygen_saturation: Optional[float] = None


class ConsultationUpdate(BaseModel):
    chief_complaint: Optional[str] = None
    examination_findings: Optional[str] = None
    diagnosis: Optional[str] = None
    treatment_plan: Optional[str] = None
    notes: Optional[str] = None
    ai_summary_reviewed: Optional[bool] = None


class ConsultationResponse(ConsultationBase):
    id: int
    appointment_id: Optional[int] = None
    temperature: Optional[float] = None
    blood_pressure_systolic: Optional[int] = None
    blood_pressure_diastolic: Optional[int] = None
    pulse_rate: Optional[int] = None
    respiratory_rate: Optional[int] = None
    oxygen_saturation: Optional[float] = None
    ai_summary: Optional[str] = None
    ai_summary_reviewed: bool
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class PrescriptionBase(BaseModel):
    consultation_id: int
    patient_id: int
    doctor_id: int
    medications: List[MedicationItem]
    general_instructions: Optional[str] = None
    dietary_advice: Optional[str] = None
    valid_until: Optional[datetime] = None


class PrescriptionCreate(PrescriptionBase):
    pass


class PrescriptionUpdate(BaseModel):
    status: Optional[PrescriptionStatus] = None
    dispensed_date: Optional[datetime] = None


class PrescriptionResponse(BaseModel):
    id: int
    consultation_id: int
    patient_id: int
    doctor_id: int
    prescription_number: str
    status: PrescriptionStatus
    medications: str  # JSON string
    general_instructions: Optional[str] = None
    dietary_advice: Optional[str] = None
    issued_date: datetime
    valid_until: Optional[datetime] = None
    dispensed_date: Optional[datetime] = None
    pdf_generated: bool
    pdf_path: Optional[str] = None
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True
