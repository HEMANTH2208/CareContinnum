from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime, timedelta
import json
from app.core.database import get_db
from app.core.dependencies import get_current_user, require_doctor
from app.schemas.consultation import (
    ConsultationCreate, ConsultationUpdate, ConsultationResponse,
    PrescriptionCreate, PrescriptionUpdate, PrescriptionResponse
)
from app.models.consultation import Consultation, Prescription, PrescriptionStatus
from app.models.user import User
from app.services.prescription_service import generate_prescription_pdf
from app.services.ai_service import generate_patient_summary

router = APIRouter()


@router.get("/", response_model=List[ConsultationResponse])
def list_consultations(
    skip: int = 0,
    limit: int = 100,
    patient_id: Optional[int] = None,
    doctor_id: Optional[int] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """List consultations."""
    query = db.query(Consultation)
    
    if patient_id:
        query = query.filter(Consultation.patient_id == patient_id)
    if doctor_id:
        query = query.filter(Consultation.doctor_id == doctor_id)
    
    consultations = query.order_by(Consultation.consultation_date.desc()).offset(skip).limit(limit).all()
    return consultations


@router.post("/", response_model=ConsultationResponse, status_code=status.HTTP_201_CREATED)
def create_consultation(
    consultation_data: ConsultationCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_doctor)
):
    """Create new consultation record."""
    consultation = Consultation(
        patient_id=consultation_data.patient_id,
        doctor_id=consultation_data.doctor_id,
        appointment_id=consultation_data.appointment_id,
        consultation_type=consultation_data.consultation_type,
        consultation_date=consultation_data.consultation_date,
        chief_complaint=consultation_data.chief_complaint,
        present_illness=consultation_data.present_illness,
        examination_findings=consultation_data.examination_findings,
        diagnosis=consultation_data.diagnosis,
        treatment_plan=consultation_data.treatment_plan,
        notes=consultation_data.notes,
        next_visit_date=consultation_data.next_visit_date,
        temperature=consultation_data.temperature,
        blood_pressure_systolic=consultation_data.blood_pressure_systolic,
        blood_pressure_diastolic=consultation_data.blood_pressure_diastolic,
        pulse_rate=consultation_data.pulse_rate,
        respiratory_rate=consultation_data.respiratory_rate,
        oxygen_saturation=consultation_data.oxygen_saturation
    )
    
    db.add(consultation)
    db.commit()
    db.refresh(consultation)
    
    # Update patient's last visit date
    from app.models.patient import Patient
    patient = db.query(Patient).filter(Patient.id == consultation_data.patient_id).first()
    if patient:
        patient.last_visit_date = consultation_data.consultation_date
        db.commit()
    
    return consultation


@router.get("/{consultation_id}", response_model=ConsultationResponse)
def get_consultation(
    consultation_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get consultation by ID."""
    consultation = db.query(Consultation).filter(Consultation.id == consultation_id).first()
    if not consultation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Consultation not found"
        )
    return consultation


@router.patch("/{consultation_id}", response_model=ConsultationResponse)
def update_consultation(
    consultation_id: int,
    consultation_data: ConsultationUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_doctor)
):
    """Update consultation record."""
    consultation = db.query(Consultation).filter(Consultation.id == consultation_id).first()
    if not consultation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Consultation not found"
        )
    
    for field, value in consultation_data.model_dump(exclude_unset=True).items():
        setattr(consultation, field, value)
    
    db.commit()
    db.refresh(consultation)
    return consultation


@router.post("/{consultation_id}/ai-summary")
def generate_ai_summary(
    consultation_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_doctor)
):
    """Generate AI summary for consultation (optional, doctor-reviewed)."""
    consultation = db.query(Consultation).filter(Consultation.id == consultation_id).first()
    if not consultation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Consultation not found"
        )
    
    # Generate AI summary
    summary = generate_patient_summary(db, consultation.patient_id)
    consultation.ai_summary = summary
    consultation.ai_summary_reviewed = False
    
    db.commit()
    return {"summary": summary, "reviewed": False}


@router.post("/prescriptions", response_model=PrescriptionResponse, status_code=status.HTTP_201_CREATED)
def create_prescription(
    prescription_data: PrescriptionCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_doctor)
):
    """Create new prescription."""
    # Generate unique prescription number
    year = datetime.now().year
    last_rx = db.query(Prescription).filter(
        Prescription.prescription_number.like(f"RX{year}%")
    ).order_by(Prescription.id.desc()).first()
    
    if last_rx:
        last_num = int(last_rx.prescription_number[6:])
        new_num = last_num + 1
    else:
        new_num = 1
    
    rx_number = f"RX{year}{new_num:06d}"
    
    # Convert medications to JSON
    medications_json = json.dumps([med.model_dump() for med in prescription_data.medications])
    
    prescription = Prescription(
        consultation_id=prescription_data.consultation_id,
        patient_id=prescription_data.patient_id,
        doctor_id=prescription_data.doctor_id,
        prescription_number=rx_number,
        medications=medications_json,
        general_instructions=prescription_data.general_instructions,
        dietary_advice=prescription_data.dietary_advice,
        valid_until=prescription_data.valid_until or (datetime.utcnow() + timedelta(days=30))
    )
    
    db.add(prescription)
    db.commit()
    db.refresh(prescription)
    
    # Generate PDF
    try:
        pdf_path = generate_prescription_pdf(db, prescription.id)
        prescription.pdf_generated = True
        prescription.pdf_path = pdf_path
        db.commit()
    except Exception as e:
        # Log error but don't fail the request
        print(f"PDF generation failed: {e}")
    
    return prescription


@router.get("/prescriptions/{prescription_id}", response_model=PrescriptionResponse)
def get_prescription(
    prescription_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get prescription by ID."""
    prescription = db.query(Prescription).filter(Prescription.id == prescription_id).first()
    if not prescription:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Prescription not found"
        )
    return prescription


@router.patch("/prescriptions/{prescription_id}", response_model=PrescriptionResponse)
def update_prescription(
    prescription_id: int,
    prescription_data: PrescriptionUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_doctor)
):
    """Update prescription status."""
    prescription = db.query(Prescription).filter(Prescription.id == prescription_id).first()
    if not prescription:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Prescription not found"
        )
    
    for field, value in prescription_data.model_dump(exclude_unset=True).items():
        setattr(prescription, field, value)
    
    db.commit()
    db.refresh(prescription)
    return prescription


@router.get("/prescriptions/{prescription_id}/pdf")
def download_prescription_pdf(
    prescription_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Download prescription PDF."""
    prescription = db.query(Prescription).filter(Prescription.id == prescription_id).first()
    if not prescription:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Prescription not found"
        )
    
    if not prescription.pdf_generated or not prescription.pdf_path:
        # Generate if not exists
        pdf_path = generate_prescription_pdf(db, prescription.id)
        prescription.pdf_generated = True
        prescription.pdf_path = pdf_path
        db.commit()
    
    from fastapi.responses import FileResponse
    return FileResponse(
        prescription.pdf_path,
        media_type="application/pdf",
        filename=f"prescription_{prescription.prescription_number}.pdf"
    )
