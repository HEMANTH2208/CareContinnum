from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_
from typing import List, Optional
from datetime import datetime, timedelta
from app.core.database import get_db
from app.core.dependencies import get_current_user, require_staff_or_doctor
from app.schemas.appointment import AppointmentCreate, AppointmentUpdate, AppointmentResponse
from app.models.appointment import Appointment, AppointmentStatus
from app.models.user import User
from app.core.config import settings

router = APIRouter()


@router.get("/", response_model=List[AppointmentResponse])
def list_appointments(
    skip: int = 0,
    limit: int = 100,
    patient_id: Optional[int] = None,
    doctor_id: Optional[int] = None,
    status: Optional[AppointmentStatus] = None,
    from_date: Optional[datetime] = None,
    to_date: Optional[datetime] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """List appointments with filters."""
    query = db.query(Appointment)
    
    if patient_id:
        query = query.filter(Appointment.patient_id == patient_id)
    if doctor_id:
        query = query.filter(Appointment.doctor_id == doctor_id)
    if status:
        query = query.filter(Appointment.status == status)
    if from_date:
        query = query.filter(Appointment.scheduled_date >= from_date)
    if to_date:
        query = query.filter(Appointment.scheduled_date <= to_date)
    
    appointments = query.order_by(Appointment.scheduled_date).offset(skip).limit(limit).all()
    return appointments


@router.post("/", response_model=AppointmentResponse, status_code=status.HTTP_201_CREATED)
def create_appointment(
    appointment_data: AppointmentCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_staff_or_doctor)
):
    """Create new appointment."""
    appointment = Appointment(
        patient_id=appointment_data.patient_id,
        doctor_id=appointment_data.doctor_id,
        follow_up_task_id=appointment_data.follow_up_task_id,
        appointment_type=appointment_data.appointment_type,
        scheduled_date=appointment_data.scheduled_date,
        department=appointment_data.department,
        notes=appointment_data.notes
    )
    
    db.add(appointment)
    db.commit()
    db.refresh(appointment)
    return appointment


@router.get("/{appointment_id}", response_model=AppointmentResponse)
def get_appointment(
    appointment_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get appointment by ID."""
    appointment = db.query(Appointment).filter(Appointment.id == appointment_id).first()
    if not appointment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Appointment not found"
        )
    return appointment


@router.patch("/{appointment_id}", response_model=AppointmentResponse)
def update_appointment(
    appointment_id: int,
    appointment_data: AppointmentUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_staff_or_doctor)
):
    """Update appointment."""
    appointment = db.query(Appointment).filter(Appointment.id == appointment_id).first()
    if not appointment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Appointment not found"
        )
    
    # Track status changes
    old_status = appointment.status
    
    for field, value in appointment_data.model_dump(exclude_unset=True).items():
        setattr(appointment, field, value)
    
    # Handle completion
    if appointment_data.status == AppointmentStatus.COMPLETED and old_status != AppointmentStatus.COMPLETED:
        appointment.completed_date = datetime.utcnow()
    
    db.commit()
    db.refresh(appointment)
    return appointment


@router.post("/{appointment_id}/reschedule", response_model=AppointmentResponse)
def reschedule_appointment(
    appointment_id: int,
    new_date: datetime,
    notes: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_staff_or_doctor)
):
    """Reschedule an appointment."""
    appointment = db.query(Appointment).filter(Appointment.id == appointment_id).first()
    if not appointment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Appointment not found"
        )
    
    # Check reschedule limit
    if appointment.reschedule_count >= settings.MAX_RESCHEDULE_ATTEMPTS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Maximum reschedule attempts ({settings.MAX_RESCHEDULE_ATTEMPTS}) reached. Escalation required."
        )
    
    # Create new appointment
    new_appointment = Appointment(
        patient_id=appointment.patient_id,
        doctor_id=appointment.doctor_id,
        follow_up_task_id=appointment.follow_up_task_id,
        appointment_type=appointment.appointment_type,
        scheduled_date=new_date,
        department=appointment.department,
        notes=notes or appointment.notes,
        reschedule_count=appointment.reschedule_count + 1,
        original_appointment_id=appointment.original_appointment_id or appointment.id
    )
    
    # Mark old appointment as rescheduled
    appointment.status = AppointmentStatus.RESCHEDULED
    
    db.add(new_appointment)
    db.commit()
    db.refresh(new_appointment)
    return new_appointment


@router.get("/missed/list", response_model=List[AppointmentResponse])
def list_missed_appointments(
    days_ago: int = 7,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_staff_or_doctor)
):
    """List missed appointments for escalation."""
    cutoff_date = datetime.utcnow() - timedelta(days=days_ago)
    
    missed = db.query(Appointment).filter(
        and_(
            Appointment.scheduled_date < datetime.utcnow(),
            Appointment.status.in_([AppointmentStatus.SCHEDULED, AppointmentStatus.CONFIRMED]),
            Appointment.scheduled_date >= cutoff_date
        )
    ).all()
    
    # Auto-update to missed status
    for appointment in missed:
        appointment.status = AppointmentStatus.MISSED
    
    db.commit()
    return missed
