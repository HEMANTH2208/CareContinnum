from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from sqlalchemy.orm import Session
import json
import os
from datetime import datetime
from app.models.consultation import Prescription
from app.models.patient import Patient
from app.models.user import User
from app.core.config import settings


def generate_prescription_pdf(db: Session, prescription_id: int) -> str:
    """Generate PDF for prescription."""
    
    prescription = db.query(Prescription).filter(Prescription.id == prescription_id).first()
    if not prescription:
        raise ValueError("Prescription not found")
    
    patient = db.query(Patient).filter(Patient.id == prescription.patient_id).first()
    doctor = db.query(User).filter(User.id == prescription.doctor_id).first()
    
    # Create directory if not exists
    pdf_dir = "prescriptions"
    os.makedirs(pdf_dir, exist_ok=True)
    
    filename = f"{pdf_dir}/prescription_{prescription.prescription_number}.pdf"
    
    # Create PDF
    doc = SimpleDocTemplate(filename, pagesize=letter)
    story = []
    styles = getSampleStyleSheet()
    
    # Custom styles
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=18,
        textColor=colors.HexColor('#1a5490'),
        spaceAfter=6,
        alignment=TA_CENTER
    )
    
    header_style = ParagraphStyle(
        'Header',
        parent=styles['Normal'],
        fontSize=10,
        alignment=TA_CENTER,
        spaceAfter=12
    )
    
    # Hospital header
    story.append(Paragraph(settings.HOSPITAL_NAME, title_style))
    story.append(Paragraph(settings.HOSPITAL_ADDRESS, header_style))
    story.append(Paragraph(f"Phone: {settings.HOSPITAL_PHONE}", header_style))
    story.append(Spacer(1, 0.3*inch))
    
    # Prescription number and date
    story.append(Paragraph(f"<b>Prescription No:</b> {prescription.prescription_number}", styles['Normal']))
    story.append(Paragraph(f"<b>Date:</b> {prescription.issued_date.strftime('%B %d, %Y')}", styles['Normal']))
    story.append(Spacer(1, 0.2*inch))
    
    # Patient information
    story.append(Paragraph("<b>Patient Information:</b>", styles['Heading2']))
    patient_data = [
        ["Name:", patient.full_name],
        ["Patient ID:", patient.patient_id],
        ["Age:", f"{(datetime.now().date() - patient.date_of_birth).days // 365} years"],
        ["Gender:", patient.gender],
    ]
    patient_table = Table(patient_data, colWidths=[1.5*inch, 4*inch])
    patient_table.setStyle(TableStyle([
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('FONTNAME', (1, 0), (1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
    ]))
    story.append(patient_table)
    story.append(Spacer(1, 0.2*inch))
    
    # Medications
    story.append(Paragraph("<b>Medications:</b>", styles['Heading2']))
    medications = json.loads(prescription.medications)
    
    med_data = [["#", "Medicine Name", "Dosage", "Frequency", "Duration"]]
    for i, med in enumerate(medications, 1):
        med_data.append([
            str(i),
            med['name'],
            med['dosage'],
            med['frequency'],
            med['duration']
        ])
    
    med_table = Table(med_data, colWidths=[0.4*inch, 2.5*inch, 1.2*inch, 1.2*inch, 1*inch])
    med_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1a5490')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 10),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 8),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 1), (-1, -1), 9),
        ('TOPPADDING', (0, 1), (-1, -1), 6),
        ('BOTTOMPADDING', (0, 1), (-1, -1), 6),
    ]))
    story.append(med_table)
    story.append(Spacer(1, 0.2*inch))
    
    # Instructions
    if prescription.general_instructions:
        story.append(Paragraph("<b>Instructions:</b>", styles['Heading2']))
        story.append(Paragraph(prescription.general_instructions, styles['Normal']))
        story.append(Spacer(1, 0.1*inch))
    
    if prescription.dietary_advice:
        story.append(Paragraph("<b>Dietary Advice:</b>", styles['Heading2']))
        story.append(Paragraph(prescription.dietary_advice, styles['Normal']))
        story.append(Spacer(1, 0.2*inch))
    
    # Doctor signature
    story.append(Spacer(1, 0.4*inch))
    story.append(Paragraph(f"<b>Dr. {doctor.full_name}</b>", styles['Normal']))
    if doctor.license_number:
        story.append(Paragraph(f"License No: {doctor.license_number}", styles['Normal']))
    if doctor.specialization:
        story.append(Paragraph(doctor.specialization, styles['Normal']))
    
    # Build PDF
    doc.build(story)
    
    return filename
