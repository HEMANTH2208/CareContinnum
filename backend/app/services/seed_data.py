"""
Seed script to generate synthetic data for development and testing.
Run with: python -m app.services.seed_data
"""

from sqlalchemy.orm import Session
from faker import Faker
import random
from datetime import datetime, timedelta
from app.core.database import SessionLocal, engine, Base
from app.core.security import get_password_hash
from app.models.user import User, UserRole
from app.models.patient import Patient, CommunicationPreference
from app.models.appointment import Appointment, AppointmentStatus, AppointmentType
from app.models.follow_up import FollowUpPlan, FollowUpTask, Priority, TaskStatus
from app.models.consultation import Consultation, ConsultationType

fake = Faker()


def seed_users(db: Session):
    """Seed user accounts."""
    print("Seeding users...")
    
    users_data = [
        # Admin
        {
            "email": "admin@carecontinuum.com",
            "password": "admin123",
            "full_name": "Admin User",
            "role": UserRole.ADMIN,
            "department": "Administration"
        },
        # Doctors
        {
            "email": "dr.smith@carecontinuum.com",
            "password": "doctor123",
            "full_name": "Dr. Sarah Smith",
            "role": UserRole.DOCTOR,
            "department": "Cardiology",
            "license_number": "MD-12345",
            "specialization": "Cardiology",
            "employee_id": "DOC001"
        },
        {
            "email": "dr.jones@carecontinuum.com",
            "password": "doctor123",
            "full_name": "Dr. Michael Jones",
            "role": UserRole.DOCTOR,
            "department": "General Medicine",
            "license_number": "MD-12346",
            "specialization": "General Medicine",
            "employee_id": "DOC002"
        },
        # Staff
        {
            "email": "staff1@carecontinuum.com",
            "password": "staff123",
            "full_name": "Emily Johnson",
            "role": UserRole.STAFF,
            "department": "Patient Coordination",
            "employee_id": "STF001"
        },
        {
            "email": "staff2@carecontinuum.com",
            "password": "staff123",
            "full_name": "David Williams",
            "role": UserRole.STAFF,
            "department": "Laboratory",
            "employee_id": "STF002"
        }
    ]
    
    users = []
    for data in users_data:
        password = data.pop("password")
        user = User(**data, hashed_password=get_password_hash(password))
        db.add(user)
        users.append(user)
    
    db.commit()
    print(f"Created {len(users)} users")
    return users


def seed_patients(db: Session, doctors: list):
    """Seed patient records."""
    print("Seeding patients...")
    
    patients = []
    for i in range(50):
        year = datetime.now().year
        patient = Patient(
            patient_id=f"P{year}{i+1:05d}",
            full_name=fake.name(),
            date_of_birth=fake.date_of_birth(minimum_age=18, maximum_age=80),
            gender=random.choice(["Male", "Female", "Other"]),
            phone=fake.phone_number(),
            email=fake.email() if random.random() > 0.2 else None,
            address=fake.address(),
            blood_group=random.choice(["A+", "A-", "B+", "B-", "O+", "O-", "AB+", "AB-"]),
            allergies=random.choice([None, "Penicillin", "Peanuts", "None known"]),
            chronic_conditions=random.choice([None, "Hypertension", "Diabetes", "Asthma"]),
            emergency_contact_name=fake.name(),
            emergency_contact_phone=fake.phone_number(),
            assigned_doctor_id=random.choice([d.id for d in doctors if d.role == UserRole.DOCTOR]),
            communication_preference=random.choice(list(CommunicationPreference)),
            consent_for_communication=random.random() > 0.1,
            created_at=datetime.utcnow() - timedelta(days=random.randint(1, 365))
        )
        db.add(patient)
        patients.append(patient)
    
    db.commit()
    print(f"Created {len(patients)} patients")
    return patients


def seed_consultations(db: Session, patients: list, doctors: list):
    """Seed consultation records."""
    print("Seeding consultations...")
    
    consultations = []
    doctor_list = [d for d in doctors if d.role == UserRole.DOCTOR]
    
    for patient in random.sample(patients, 30):
        num_consultations = random.randint(1, 5)
        for _ in range(num_consultations):
            consultation = Consultation(
                patient_id=patient.id,
                doctor_id=random.choice(doctor_list).id,
                consultation_type=random.choice(list(ConsultationType)),
                consultation_date=datetime.utcnow() - timedelta(days=random.randint(1, 180)),
                chief_complaint=random.choice([
                    "Chest pain", "Fever", "Headache", "Cough", "Fatigue",
                    "Back pain", "Abdominal pain", "Shortness of breath"
                ]),
                diagnosis=random.choice([
                    "Viral infection", "Hypertension", "Migraine", "Gastritis",
                    "Upper respiratory infection", "Musculoskeletal pain"
                ]),
                treatment_plan=random.choice([
                    "Rest and medication", "Follow-up in 2 weeks",
                    "Laboratory tests ordered", "Lifestyle modifications"
                ]),
                temperature=round(random.uniform(36.5, 38.5), 1) if random.random() > 0.3 else None,
                blood_pressure_systolic=random.randint(110, 140) if random.random() > 0.3 else None,
                blood_pressure_diastolic=random.randint(70, 90) if random.random() > 0.3 else None,
                pulse_rate=random.randint(60, 100) if random.random() > 0.3 else None
            )
            db.add(consultation)
            consultations.append(consultation)
    
    db.commit()
    print(f"Created {len(consultations)} consultations")
    return consultations


def seed_follow_ups(db: Session, patients: list, doctors: list, staff: list):
    """Seed follow-up plans and tasks."""
    print("Seeding follow-up plans...")
    
    doctor_list = [d for d in doctors if d.role == UserRole.DOCTOR]
    staff_list = [s for s in staff if s.role == UserRole.STAFF]
    
    plans = []
    tasks = []
    
    for patient in random.sample(patients, 25):
        plan = FollowUpPlan(
            patient_id=patient.id,
            doctor_id=random.choice(doctor_list).id,
            title=random.choice([
                "Post-consultation follow-up",
                "Laboratory test tracking",
                "Medication review",
                "Chronic condition monitoring"
            ]),
            description="Regular follow-up to monitor patient progress",
            priority=random.choice(list(Priority)),
            created_at=datetime.utcnow() - timedelta(days=random.randint(1, 60))
        )
        db.add(plan)
        db.flush()
        plans.append(plan)
        
        # Add tasks to plan
        num_tasks = random.randint(1, 4)
        for i in range(num_tasks):
            days_offset = random.randint(-10, 30)  # Some overdue, some future
            task = FollowUpTask(
                plan_id=plan.id,
                title=random.choice([
                    "Blood test", "Follow-up consultation", "X-ray",
                    "Medication review", "Blood pressure check"
                ]),
                task_type=random.choice(["lab_test", "consultation", "imaging", "checkup"]),
                due_date=datetime.utcnow() + timedelta(days=days_offset),
                status=random.choice([
                    TaskStatus.PENDING, TaskStatus.SCHEDULED, TaskStatus.COMPLETED,
                    TaskStatus.IN_PROGRESS, TaskStatus.BLOCKED
                ]),
                priority=random.choice(list(Priority)),
                assigned_department=random.choice(["Laboratory", "Radiology", "Patient Coordination"]),
                assigned_staff_id=random.choice([s.id for s in staff_list]) if random.random() > 0.3 else None,
                contact_attempts=random.randint(0, 4) if random.random() > 0.5 else 0,
                is_overdue=days_offset < 0 and random.random() > 0.3
            )
            
            # Some tasks completed
            if task.status == TaskStatus.COMPLETED:
                task.completed_date = task.due_date + timedelta(days=random.randint(0, 5))
                task.result = "Completed successfully"
            
            # Some tasks escalated
            if task.is_overdue and random.random() > 0.7:
                task.status = TaskStatus.ESCALATED
                task.escalated_at = datetime.utcnow()
                task.escalation_reason = "Overdue with multiple contact attempts"
            
            db.add(task)
            tasks.append(task)
    
    db.commit()
    print(f"Created {len(plans)} follow-up plans with {len(tasks)} tasks")
    return plans, tasks


def seed_appointments(db: Session, patients: list, doctors: list, tasks: list):
    """Seed appointments."""
    print("Seeding appointments...")
    
    doctor_list = [d for d in doctors if d.role == UserRole.DOCTOR]
    appointments = []
    
    for patient in random.sample(patients, 30):
        num_appointments = random.randint(1, 3)
        for _ in range(num_appointments):
            days_offset = random.randint(-30, 30)
            appointment = Appointment(
                patient_id=patient.id,
                doctor_id=random.choice(doctor_list).id,
                appointment_type=random.choice(list(AppointmentType)),
                scheduled_date=datetime.utcnow() + timedelta(days=days_offset),
                status=random.choice([
                    AppointmentStatus.SCHEDULED, AppointmentStatus.CONFIRMED,
                    AppointmentStatus.COMPLETED, AppointmentStatus.MISSED
                ]) if days_offset < 0 else AppointmentStatus.SCHEDULED,
                department=random.choice(["Cardiology", "General Medicine", "Laboratory"]),
                reschedule_count=random.randint(0, 2),
                reminder_sent=random.random() > 0.5
            )
            
            if appointment.status == AppointmentStatus.COMPLETED:
                appointment.completed_date = appointment.scheduled_date + timedelta(hours=1)
            
            db.add(appointment)
            appointments.append(appointment)
    
    db.commit()
    print(f"Created {len(appointments)} appointments")
    return appointments


def main():
    """Run all seed functions."""
    print("Starting database seeding...")
    
    # Create tables
    Base.metadata.create_all(bind=engine)
    
    db = SessionLocal()
    
    try:
        # Check if data already exists
        if db.query(User).count() > 0:
            print("Database already contains data. Skipping seed.")
            return
        
        # Seed in order of dependencies
        users = seed_users(db)
        doctors = [u for u in users if u.role == UserRole.DOCTOR]
        staff = [u for u in users if u.role == UserRole.STAFF]
        
        patients = seed_patients(db, doctors)
        consultations = seed_consultations(db, patients, doctors)
        plans, tasks = seed_follow_ups(db, patients, doctors, staff)
        appointments = seed_appointments(db, patients, doctors, tasks)
        
        print("\n✓ Database seeding completed successfully!")
        print(f"  - Users: {len(users)}")
        print(f"  - Patients: {len(patients)}")
        print(f"  - Consultations: {len(consultations)}")
        print(f"  - Follow-up plans: {len(plans)}")
        print(f"  - Follow-up tasks: {len(tasks)}")
        print(f"  - Appointments: {len(appointments)}")
        print("\nTest credentials:")
        print("  Admin: admin@carecontinuum.com / admin123")
        print("  Doctor: dr.smith@carecontinuum.com / doctor123")
        print("  Staff: staff1@carecontinuum.com / staff123")
        
    except Exception as e:
        print(f"Error during seeding: {e}")
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    main()
