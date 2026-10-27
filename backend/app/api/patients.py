from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import or_, func
from typing import List, Optional
from datetime import datetime
from app.core.database import get_db
from app.core.dependencies import get_current_user, require_staff_or_doctor
from app.schemas.patient import PatientCreate, PatientUpdate, PatientResponse, PatientTimeline, TimelineEvent
from app.models.patient import Patient
from app.models.user import User
from app.models.consultation import Consultation
from app.models.appointment import Appointment
from app.models.follow_up import FollowUpPlan
from app.models.consultation import Prescription

router = APIRouter()


def generate_patient_id(db: Session) -> str:
    """Generate unique patient ID."""
    # Simple implementation - use year + sequential number
    year = datetime.now().year
    last_patient = db.query(Patient).filter(
        Patient.patient_id.like(f"P{year}%")
    ).order_by(Patient.id.desc()).first()
    
    if last_patient:
        last_num = int(last_patient.patient_id[5:])
        new_num = last_num + 1
    else:
        new_num = 1
    
    return f"P{year}{new_num:05d}"


@router.get("/", response_model=List[PatientResponse])
def list_patients(
    skip: int = 0,
    limit: int = 100,
    search: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_staff_or_doctor)
):
    """List all patients with optional search."""
    query = db.query(Patient).filter(Patient.is_active == True)
    
    if search:
        query = query.filter(
            or_(
                Patient.full_name.ilike(f"%{search}%"),
                Patient.patient_id.ilike(f"%{search}%"),
                Patient.phone.ilike(f"%{search}%"),
                Patient.email.ilike(f"%{search}%")
            )
        )
    
    patients = query.offset(skip).limit(limit).all()
    return patients


@router.post("/", response_model=PatientResponse, status_code=status.HTTP_201_CREATED)
def create_patient(
    patient_data: PatientCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_staff_or_doctor)
):
    """Register new patient."""
    # Check for potential duplicates
    existing = db.query(Patient).filter(
        Patient.full_name == patient_data.full_name,
        Patient.date_of_birth == patient_data.date_of_birth,
        Patient.phone == patient_data.phone
    ).first()
    
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Potential duplicate patient found: {existing.patient_id}. Please verify."
        )
    
    patient = Patient(
        patient_id=generate_patient_id(db),
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
    
    db.add(patient)
    db.commit()
    db.refresh(patient)
    return patient


@router.get("/{patient_id}", response_model=PatientResponse)
def get_patient(
    patient_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get patient by ID."""
    patient = db.query(Patient).filter(Patient.id == patient_id).first()
    if not patient:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Patient not found"
        )
    return patient


@router.patch("/{patient_id}", response_model=PatientResponse)
def update_patient(
    patient_id: int,
    patient_data: PatientUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_staff_or_doctor)
):
    """Update patient information."""
    patient = db.query(Patient).filter(Patient.id == patient_id).first()
    if not patient:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Patient not found"
        )
    
    for field, value in patient_data.model_dump(exclude_unset=True).items():
        setattr(patient, field, value)
    
    db.commit()
    db.refresh(patient)
    return patient


@router.get("/{patient_id}/timeline", response_model=PatientTimeline)
def get_patient_timeline(
    patient_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get patient's complete timeline of events."""
    patient = db.query(Patient).filter(Patient.id == patient_id).first()
    if not patient:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Patient not found"
        )
    
    events = []
    
    # Consultations
    consultations = db.query(Consultation).filter(
        Consultation.patient_id == patient_id
    ).all()
    for c in consultations:
        events.append(TimelineEvent(
            event_type="consultation",
            event_date=c.consultation_date,
            title=f"{c.consultation_type.value.replace('_', ' ').title()} Consultation",
            description=c.chief_complaint,
            details={
                "id": c.id,
                "doctor_id": c.doctor_id,
                "diagnosis": c.diagnosis,
                "treatment_plan": c.treatment_plan
            }
        ))
    
    # Appointments
    appointments = db.query(Appointment).filter(
        Appointment.patient_id == patient_id
    ).all()
    for a in appointments:
        events.append(TimelineEvent(
            event_type="appointment",
            event_date=a.scheduled_date,
            title=f"{a.status.value.title()} - {a.appointment_type.value.replace('_', ' ').title()}",
            description=a.notes,
            details={
                "id": a.id,
                "status": a.status.value,
                "doctor_id": a.doctor_id
            }
        ))
    
    # Follow-up plans
    plans = db.query(FollowUpPlan).filter(
        FollowUpPlan.patient_id == patient_id
    ).all()
    for p in plans:
        events.append(TimelineEvent(
            event_type="follow_up_plan",
            event_date=p.created_at,
            title=f"Follow-up Plan: {p.title}",
            description=p.description,
            details={
                "id": p.id,
                "priority": p.priority.value,
                "is_active": p.is_active
            }
        ))
    
    # Prescriptions
    prescriptions = db.query(Prescription).filter(
        Prescription.patient_id == patient_id
    ).all()
    for rx in prescriptions:
        events.append(TimelineEvent(
            event_type="prescription",
            event_date=rx.issued_date,
            title=f"Prescription: {rx.prescription_number}",
            description=rx.general_instructions,
            details={
                "id": rx.id,
                "status": rx.status.value,
                "medications": rx.medications
            }
        ))
    
    # Sort events by date (newest first)
    events.sort(key=lambda x: x.event_date, reverse=True)
    
    return PatientTimeline(patient=patient, events=events)
