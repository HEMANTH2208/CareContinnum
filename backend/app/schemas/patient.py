from pydantic import BaseModel, EmailStr
from typing import Optional, List
from datetime import datetime, date
from app.models.patient import CommunicationPreference


class PatientBase(BaseModel):
    full_name: str
    date_of_birth: date
    gender: str
    phone: str
    email: Optional[EmailStr] = None
    address: Optional[str] = None
    blood_group: Optional[str] = None
    allergies: Optional[str] = None
    chronic_conditions: Optional[str] = None
    emergency_contact_name: Optional[str] = None
    emergency_contact_phone: Optional[str] = None
    communication_preference: CommunicationPreference = CommunicationPreference.ALL
    consent_for_communication: bool = True


class PatientCreate(PatientBase):
    assigned_doctor_id: Optional[int] = None


class PatientUpdate(BaseModel):
    full_name: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[EmailStr] = None
    address: Optional[str] = None
    allergies: Optional[str] = None
    chronic_conditions: Optional[str] = None
    emergency_contact_name: Optional[str] = None
    emergency_contact_phone: Optional[str] = None
    assigned_doctor_id: Optional[int] = None
    communication_preference: Optional[CommunicationPreference] = None
    consent_for_communication: Optional[bool] = None


class PatientResponse(PatientBase):
    id: int
    patient_id: str
    assigned_doctor_id: Optional[int] = None
    is_active: bool
    created_at: datetime
    updated_at: Optional[datetime] = None
    last_visit_date: Optional[datetime] = None

    class Config:
        from_attributes = True


class TimelineEvent(BaseModel):
    event_type: str  # "consultation", "appointment", "follow_up", "prescription"
    event_date: datetime
    title: str
    description: Optional[str] = None
    details: dict


class PatientTimeline(BaseModel):
    patient: PatientResponse
    events: List[TimelineEvent]
