from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import func, and_, or_
from typing import Optional
from datetime import datetime, timedelta
from app.core.database import get_db
from app.core.dependencies import get_current_user, require_admin
from app.models.user import User
from app.models.appointment import Appointment, AppointmentStatus
from app.models.follow_up import FollowUpTask, TaskStatus
from app.models.notification import Notification, NotificationStatus
from app.models.patient import Patient

router = APIRouter()


@router.get("/dashboard")
def get_dashboard_analytics(
    from_date: Optional[datetime] = None,
    to_date: Optional[datetime] = None,
    department: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get comprehensive dashboard analytics."""
    
    if not from_date:
        from_date = datetime.utcnow() - timedelta(days=30)
    if not to_date:
        to_date = datetime.utcnow()
    
    # Total patients
    total_patients = db.query(func.count(Patient.id)).filter(Patient.is_active == True).scalar()
    
    # Appointments metrics
    total_appointments = db.query(func.count(Appointment.id)).filter(
        Appointment.scheduled_date.between(from_date, to_date)
    ).scalar()
    
    completed_appointments = db.query(func.count(Appointment.id)).filter(
        and_(
            Appointment.scheduled_date.between(from_date, to_date),
            Appointment.status == AppointmentStatus.COMPLETED
        )
    ).scalar()
    
    missed_appointments = db.query(func.count(Appointment.id)).filter(
        and_(
            Appointment.scheduled_date.between(from_date, to_date),
            Appointment.status == AppointmentStatus.MISSED
        )
    ).scalar()
    
    # Follow-up metrics
    total_follow_up_tasks = db.query(func.count(FollowUpTask.id)).filter(
        FollowUpTask.created_at.between(from_date, to_date)
    ).scalar()
    
    completed_follow_ups = db.query(func.count(FollowUpTask.id)).filter(
        and_(
            FollowUpTask.created_at.between(from_date, to_date),
            FollowUpTask.status == TaskStatus.COMPLETED
        )
    ).scalar()
    
    overdue_tasks = db.query(func.count(FollowUpTask.id)).filter(
        and_(
            FollowUpTask.due_date < datetime.utcnow(),
            FollowUpTask.status.in_([TaskStatus.PENDING, TaskStatus.SCHEDULED])
        )
    ).scalar()
    
    escalated_tasks = db.query(func.count(FollowUpTask.id)).filter(
        FollowUpTask.status == TaskStatus.ESCALATED
    ).scalar()
    
    # Notification metrics
    total_notifications = db.query(func.count(Notification.id)).filter(
        Notification.scheduled_for.between(from_date, to_date)
    ).scalar()
    
    delivered_notifications = db.query(func.count(Notification.id)).filter(
        and_(
            Notification.scheduled_for.between(from_date, to_date),
            Notification.status == NotificationStatus.DELIVERED
        )
    ).scalar()
    
    failed_notifications = db.query(func.count(Notification.id)).filter(
        and_(
            Notification.scheduled_for.between(from_date, to_date),
            Notification.status == NotificationStatus.FAILED
        )
    ).scalar()
    
    # Calculate rates
    appointment_completion_rate = (completed_appointments / total_appointments * 100) if total_appointments > 0 else 0
    missed_appointment_rate = (missed_appointments / total_appointments * 100) if total_appointments > 0 else 0
    follow_up_completion_rate = (completed_follow_ups / total_follow_up_tasks * 100) if total_follow_up_tasks > 0 else 0
    notification_delivery_rate = (delivered_notifications / total_notifications * 100) if total_notifications > 0 else 0
    
    # Average resolution time for completed tasks
    avg_resolution = db.query(
        func.avg(
            func.extract('epoch', FollowUpTask.completed_date - FollowUpTask.created_at) / 86400
        )
    ).filter(
        and_(
            FollowUpTask.status == TaskStatus.COMPLETED,
            FollowUpTask.completed_date.isnot(None),
            FollowUpTask.created_at.between(from_date, to_date)
        )
    ).scalar()
    
    # Staff workload by department
    staff_workload = db.query(
        FollowUpTask.assigned_department,
        func.count(FollowUpTask.id).label('task_count')
    ).filter(
        FollowUpTask.status.in_([TaskStatus.PENDING, TaskStatus.SCHEDULED, TaskStatus.IN_PROGRESS])
    ).group_by(FollowUpTask.assigned_department).all()
    
    return {
        "period": {
            "from": from_date.isoformat(),
            "to": to_date.isoformat()
        },
        "patients": {
            "total": total_patients
        },
        "appointments": {
            "total": total_appointments,
            "completed": completed_appointments,
            "missed": missed_appointments,
            "completion_rate": round(appointment_completion_rate, 2),
            "missed_rate": round(missed_appointment_rate, 2)
        },
        "follow_ups": {
            "total": total_follow_up_tasks,
            "completed": completed_follow_ups,
            "overdue": overdue_tasks,
            "escalated": escalated_tasks,
            "completion_rate": round(follow_up_completion_rate, 2),
            "avg_resolution_days": round(avg_resolution or 0, 1)
        },
        "notifications": {
            "total": total_notifications,
            "delivered": delivered_notifications,
            "failed": failed_notifications,
            "delivery_rate": round(notification_delivery_rate, 2)
        },
        "staff_workload": [
            {"department": dept or "Unassigned", "active_tasks": count}
            for dept, count in staff_workload
        ]
    }


@router.get("/unresolved-cases")
def get_unresolved_cases(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get count of unresolved cases awaiting intervention."""
    
    # Overdue tasks
    overdue = db.query(func.count(FollowUpTask.id)).filter(
        and_(
            FollowUpTask.due_date < datetime.utcnow(),
            FollowUpTask.status.in_([TaskStatus.PENDING, TaskStatus.SCHEDULED])
        )
    ).scalar()
    
    # Escalated tasks
    escalated = db.query(func.count(FollowUpTask.id)).filter(
        FollowUpTask.status == TaskStatus.ESCALATED
    ).scalar()
    
    # Blocked tasks
    blocked = db.query(func.count(FollowUpTask.id)).filter(
        FollowUpTask.status == TaskStatus.BLOCKED
    ).scalar()
    
    # Missed appointments not rescheduled
    missed_not_rescheduled = db.query(func.count(Appointment.id)).filter(
        and_(
            Appointment.status == AppointmentStatus.MISSED,
            Appointment.scheduled_date > datetime.utcnow() - timedelta(days=7)
        )
    ).scalar()
    
    # Tasks with high contact attempts
    high_contact_attempts = db.query(func.count(FollowUpTask.id)).filter(
        and_(
            FollowUpTask.contact_attempts >= 3,
            FollowUpTask.status.in_([TaskStatus.PENDING, TaskStatus.SCHEDULED])
        )
    ).scalar()
    
    return {
        "overdue_tasks": overdue,
        "escalated_tasks": escalated,
        "blocked_tasks": blocked,
        "missed_appointments": missed_not_rescheduled,
        "high_contact_attempts": high_contact_attempts,
        "total_unresolved": overdue + escalated + blocked + missed_not_rescheduled
    }


@router.get("/trends")
def get_trends(
    days: int = 30,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """Get daily trends for key metrics."""
    
    from_date = datetime.utcnow() - timedelta(days=days)
    
    # Daily appointment counts
    daily_appointments = db.query(
        func.date(Appointment.scheduled_date).label('date'),
        func.count(Appointment.id).label('count')
    ).filter(
        Appointment.scheduled_date >= from_date
    ).group_by(func.date(Appointment.scheduled_date)).all()
    
    # Daily completion counts
    daily_completions = db.query(
        func.date(FollowUpTask.completed_date).label('date'),
        func.count(FollowUpTask.id).label('count')
    ).filter(
        and_(
            FollowUpTask.completed_date >= from_date,
            FollowUpTask.status == TaskStatus.COMPLETED
        )
    ).group_by(func.date(FollowUpTask.completed_date)).all()
    
    return {
        "daily_appointments": [
            {"date": str(date), "count": count}
            for date, count in daily_appointments
        ],
        "daily_completions": [
            {"date": str(date), "count": count}
            for date, count in daily_completions
        ]
    }
