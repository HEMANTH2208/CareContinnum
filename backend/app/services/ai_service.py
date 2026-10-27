from sqlalchemy.orm import Session
from typing import Optional
from app.models.patient import Patient
from app.models.consultation import Consultation
from app.models.follow_up import FollowUpTask, TaskStatus
from app.models.appointment import Appointment


def generate_patient_summary(db: Session, patient_id: int) -> str:
    """
    Generate AI-assisted patient summary.
    
    NOTE: This is a placeholder for actual AI integration.
    In production, this would call an LLM API with proper patient data.
    The summary must be reviewed by a doctor before use.
    """
    
    patient = db.query(Patient).filter(Patient.id == patient_id).first()
    if not patient:
        return "Patient not found"
    
    # Get recent consultations
    recent_consultations = db.query(Consultation).filter(
        Consultation.patient_id == patient_id
    ).order_by(Consultation.consultation_date.desc()).limit(5).all()
    
    # Get pending follow-ups
    pending_follow_ups = db.query(FollowUpTask).filter(
        FollowUpTask.plan_id.in_(
            db.query(FollowUpTask.plan_id).join(
                FollowUpTask.plan
            ).filter(FollowUpTask.plan.has(patient_id=patient_id))
        ),
        FollowUpTask.status.in_([TaskStatus.PENDING, TaskStatus.SCHEDULED])
    ).all()
    
    # Build summary (rule-based for now)
    summary_parts = []
    
    # Patient basics
    age = (patient.date_of_birth - patient.date_of_birth).days // 365 if patient.date_of_birth else "Unknown"
    summary_parts.append(f"Patient: {patient.full_name}, {age} years, {patient.gender}")
    
    # Chronic conditions
    if patient.chronic_conditions:
        summary_parts.append(f"\nChronic Conditions: {patient.chronic_conditions}")
    
    # Allergies
    if patient.allergies:
        summary_parts.append(f"Allergies: {patient.allergies}")
    
    # Recent visits
    if recent_consultations:
        summary_parts.append(f"\n\nRecent Consultations ({len(recent_consultations)}):")
        for c in recent_consultations[:3]:
            date_str = c.consultation_date.strftime("%Y-%m-%d")
            summary_parts.append(f"- {date_str}: {c.chief_complaint or 'General consultation'}")
            if c.diagnosis:
                summary_parts.append(f"  Diagnosis: {c.diagnosis}")
    
    # Pending follow-ups
    if pending_follow_ups:
        summary_parts.append(f"\n\nPending Follow-ups ({len(pending_follow_ups)}):")
        for task in pending_follow_ups[:3]:
            summary_parts.append(f"- {task.title} (Due: {task.due_date.strftime('%Y-%m-%d')})")
    
    # Add disclaimer
    summary_parts.append("\n\n[AI-GENERATED SUMMARY - REQUIRES DOCTOR REVIEW]")
    summary_parts.append("[Sources: Patient records, consultation history, active follow-ups]")
    summary_parts.append("[Missing: Lab results pending, imaging reports not yet available]")
    
    return "\n".join(summary_parts)


def extract_tasks_from_notes(clinical_notes: str) -> list:
    """
    Extract proposed follow-up tasks from clinical notes.
    
    NOTE: This is a placeholder. In production, this would use NLP/LLM
    to intelligently extract tasks. All extracted tasks MUST be reviewed
    and approved by the doctor before activation.
    """
    
    # Simple keyword-based extraction (placeholder)
    keywords = {
        "lab_test": ["blood test", "lab work", "laboratory", "CBC", "lipid profile"],
        "imaging": ["x-ray", "CT scan", "MRI", "ultrasound", "imaging"],
        "follow_up": ["follow up", "follow-up", "revisit", "check back"],
        "referral": ["refer to", "referral", "consult", "specialist"]
    }
    
    proposed_tasks = []
    notes_lower = clinical_notes.lower()
    
    for task_type, terms in keywords.items():
        for term in terms:
            if term in notes_lower:
                proposed_tasks.append({
                    "type": task_type,
                    "detected_term": term,
                    "requires_review": True,
                    "confidence": "medium"
                })
                break
    
    return proposed_tasks
