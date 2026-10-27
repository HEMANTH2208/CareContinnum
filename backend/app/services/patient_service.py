from sqlalchemy.orm import Session
from sqlalchemy import or_
from fastapi import HTTPException, status
from typing import List, Optional
from datetime import datetime
from app.models.patient import Patient
from app.models.appointment import Appointment
from app.models.consultation import Consultation
from app.models.follow_up import FollowUpPlan
from app.schemas.patient import PatientCreate, PatientUpdate, TimelineEvent
import random
import string


def generate_patient_id(db: Session) -> str:
    """Generate unique patient ID."""
    while True:
        # Format: P-YYYYMMDD-XXXX
        date_part = datetime.now().strftime("%Y%m%d")
        random_part = ''.join(random.choices(string.digits, k=4))
        patient_id = f"P-{date_part}-{random_part}"
        
        # Check if exists
        existing = db.query(Patient).filter(Patient.patient_id == patient_id).first()
        if not existing:
            return patient_id


def create_patient(db: Session, patient_data: PatientCreate) -> Patient:
    """Create a new patient record."""
    # Generate unique patient ID
    patient_id = generate_patient_id(db)
    
    # Check for potential duplicates
    potential_duplicates = db.query(Patient).filter(
        or_(
            Patient.phone == patient_data.phone,
            Patient.email == patient_data.email
        )
    ).all()
    
    if potential_duplicates:
        # In production, flag for review; for now, allow creation
        pass
    
    db_patient = Patient(
        patient_id=patient_id,
        full_name=patient_data.full_name,
        date_of_birth=patient_data.date_of_birth,
        gender=patient_data.gender,
        phone=patient_data.phone,
        email=patient_data.email,
        address=patient_data.address,
        blood_group=patient_data.blood_group,
        allergies=patient_data.allergies,
        chronic_conditions=patient_data.chronic_conditions,
        emergency_contact_name=patient_data.emergency_contact_name,
        emergency_contact_phone=patient_data.emergency_contact_phone,
        assigned_doctor_id=patient_data.assigned_doctor_id,
        communication_preference=patient_data.communication_preference,
        consent_for_communication=patient_data.consent_for_communication
    )
    
    db.add(db_patient)
    db.commit()
    db.refresh(db_patient)
    
    return db_patient


def get_patient_by_id(db: Session, patient_id: int) -> Optional[Patient]:
    """Get patient by database ID."""
    return db.query(Patient).filter(Patient.id == patient_id).first()


def search_patients(db: Session, query: str, limit: int = 20) -> List[Patient]:
    """Search patients by name, patient ID, or phone."""
    search_pattern = f"%{query}%"
    return db.query(Patient).filter(
        or_(
            Patient.full_name.ilike(search_pattern),
            Patient.patient_id.ilike(search_pattern),
            Patient.phone.ilike(search_pattern)
        )
    ).limit(limit).all()


def update_patient(db: Session, patient_id: int, patient_data: PatientUpdate) -> Patient:
    """Update patient information."""
    patient = get_patient_by_id(db, patient_id)
    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")
    
    update_data = patient_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(patient, field, value)
    
    db.commit()
    db.refresh(patient)
    
    return patient


def get_patient_timeline(db: Session, patient_id: int) -> List[TimelineEvent]:
    """Get chronological timeline of patient events."""
    patient = get_patient_by_id(db, patient_id)
    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")
    
    events = []
    
    # Get consultations
    consultations = db.query(Consultation).filter(
        Consultation.patient_id == patient_id
    ).order_by(Consultation.consultation_date.desc()).all()
    
    for consultation in consultations:
        events.append(TimelineEvent(
            event_type="consultation",
            event_date=consultation.consultation_date,
            title=f"Consultation - {consultation.consultation_type.value}",
            description=consultation.chief_complaint,
            details={
                "id": consultation.id,
                "doctor_id": consultation.doctor_id,
                "diagnosis": consultation.diagnosis
            }
        ))
    
    # Get appointments
    appointments = db.query(Appointment).filter(
        Appointment.patient_id == patient_id
    ).order_by(Appointment.scheduled_date.desc()).all()
    
    for appointment in appointments:
        events.append(TimelineEvent(
            event_type="appointment",
            event_date=appointment.scheduled_date,
            title=f"Appointment - {appointment.status.value}",
            description=appointment.notes,
            details={
                "id": appointment.id,
                "doctor_id": appointment.doctor_id,
                "status": appointment.status.value
            }
        ))
    
    # Get follow-up plans
    follow_ups = db.query(FollowUpPlan).filter(
        FollowUpPlan.patient_id == patient_id
    ).order_by(FollowUpPlan.created_at.desc()).all()
    
    for follow_up in follow_ups:
        events.append(TimelineEvent(
            event_type="follow_up",
            event_date=follow_up.created_at,
            title=f"Follow-up Plan - {follow_up.title}",
            description=follow_up.description,
            details={
                "id": follow_up.id,
                "priority": follow_up.priority.value,
                "is_active": follow_up.is_active
            }
        ))
    
    # Sort all events by date (most recent first)
    events.sort(key=lambda x: x.event_date, reverse=True)
    
    return events
