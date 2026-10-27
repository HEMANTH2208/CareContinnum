from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from app.core.database import SessionLocal
from app.models.follow_up import FollowUpTask, TaskStatus
from app.models.appointment import Appointment, AppointmentStatus
from app.models.notification import Notification, NotificationStatus
from app.services.notification_service import send_notification, schedule_appointment_reminder
from app.core.config import settings
import logging

logger = logging.getLogger(__name__)

scheduler = BackgroundScheduler()


def get_db():
    """Get database session for scheduler tasks."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def check_overdue_tasks():
    """Check for overdue follow-up tasks and flag them."""
    logger.info("Checking for overdue tasks...")
    db = next(get_db())
    
    try:
        now = datetime.utcnow()
        overdue_tasks = db.query(FollowUpTask).filter(
            FollowUpTask.due_date < now,
            FollowUpTask.status.in_([TaskStatus.PENDING, TaskStatus.SCHEDULED]),
            FollowUpTask.is_overdue == False
        ).all()
        
        for task in overdue_tasks:
            task.is_overdue = True
            days_overdue = (now - task.due_date).days
            
            # Check if escalation is needed
            if days_overdue >= 3 or task.contact_attempts >= settings.MAX_CONTACT_ATTEMPTS:
                task.status = TaskStatus.ESCALATED
                task.escalated_at = now
                task.escalation_reason = f"Overdue by {days_overdue} days, {task.contact_attempts} contact attempts"
                logger.warning(f"Task {task.id} escalated: {task.escalation_reason}")
        
        db.commit()
        logger.info(f"Flagged {len(overdue_tasks)} overdue tasks")
        
    except Exception as e:
        logger.error(f"Error checking overdue tasks: {e}")
        db.rollback()
    finally:
        db.close()


def check_missed_appointments():
    """Check for missed appointments and update status."""
    logger.info("Checking for missed appointments...")
    db = next(get_db())
    
    try:
        now = datetime.utcnow()
        missed = db.query(Appointment).filter(
            Appointment.scheduled_date < now - timedelta(hours=1),
            Appointment.status.in_([AppointmentStatus.SCHEDULED, AppointmentStatus.CONFIRMED])
        ).all()
        
        for appointment in missed:
            appointment.status = AppointmentStatus.MISSED
            logger.info(f"Appointment {appointment.id} marked as missed")
            
            # Check reschedule limit
            if appointment.reschedule_count >= settings.MAX_RESCHEDULE_ATTEMPTS:
                # Escalate associated task if exists
                if appointment.follow_up_task_id:
                    task = db.query(FollowUpTask).filter(
                        FollowUpTask.id == appointment.follow_up_task_id
                    ).first()
                    if task and task.status != TaskStatus.ESCALATED:
                        task.status = TaskStatus.ESCALATED
                        task.escalated_at = now
                        task.escalation_reason = f"Missed appointment, reschedule limit reached ({settings.MAX_RESCHEDULE_ATTEMPTS})"
                        logger.warning(f"Task {task.id} escalated due to missed appointment")
        
        db.commit()
        logger.info(f"Marked {len(missed)} missed appointments")
        
    except Exception as e:
        logger.error(f"Error checking missed appointments: {e}")
        db.rollback()
    finally:
        db.close()


def process_pending_notifications():
    """Process pending notifications."""
    logger.info("Processing pending notifications...")
    db = next(get_db())
    
    try:
        now = datetime.utcnow()
        pending = db.query(Notification).filter(
            Notification.status == NotificationStatus.PENDING,
            Notification.scheduled_for <= now,
            Notification.attempt_count < Notification.max_attempts
        ).limit(50).all()
        
        for notification in pending:
            send_notification(db, notification.id)
        
        logger.info(f"Processed {len(pending)} pending notifications")
        
    except Exception as e:
        logger.error(f"Error processing notifications: {e}")
        db.rollback()
    finally:
        db.close()


def schedule_upcoming_reminders():
    """Schedule reminders for upcoming appointments."""
    logger.info("Scheduling upcoming appointment reminders...")
    db = next(get_db())
    
    try:
        # Get appointments in next 2 days that don't have reminders
        from_date = datetime.utcnow()
        to_date = datetime.utcnow() + timedelta(days=2)
        
        appointments = db.query(Appointment).filter(
            Appointment.scheduled_date.between(from_date, to_date),
            Appointment.status.in_([AppointmentStatus.SCHEDULED, AppointmentStatus.CONFIRMED]),
            Appointment.reminder_sent == False
        ).all()
        
        for appointment in appointments:
            # Check if reminder already exists
            existing = db.query(Notification).filter(
                Notification.appointment_id == appointment.id,
                Notification.notification_type == "appointment_reminder"
            ).first()
            
            if not existing:
                schedule_appointment_reminder(db, appointment.id, hours_before=24)
                appointment.reminder_sent = True
                logger.info(f"Scheduled reminder for appointment {appointment.id}")
        
        db.commit()
        logger.info(f"Scheduled reminders for {len(appointments)} appointments")
        
    except Exception as e:
        logger.error(f"Error scheduling reminders: {e}")
        db.rollback()
    finally:
        db.close()


def start_scheduler():
    """Start the background scheduler."""
    
    # Check overdue tasks every hour
    scheduler.add_job(
        check_overdue_tasks,
        trigger=IntervalTrigger(hours=1),
        id='check_overdue_tasks',
        name='Check overdue follow-up tasks',
        replace_existing=True
    )
    
    # Check missed appointments every 30 minutes
    scheduler.add_job(
        check_missed_appointments,
        trigger=IntervalTrigger(minutes=30),
        id='check_missed_appointments',
        name='Check missed appointments',
        replace_existing=True
    )
    
    # Process notifications every 5 minutes
    scheduler.add_job(
        process_pending_notifications,
        trigger=IntervalTrigger(minutes=5),
        id='process_notifications',
        name='Process pending notifications',
        replace_existing=True
    )
    
    # Schedule reminders every 6 hours
    scheduler.add_job(
        schedule_upcoming_reminders,
        trigger=IntervalTrigger(hours=6),
        id='schedule_reminders',
        name='Schedule appointment reminders',
        replace_existing=True
    )
    
    scheduler.start()
    logger.info("Scheduler started with 4 jobs")


def stop_scheduler():
    """Stop the background scheduler."""
    scheduler.shutdown()
    logger.info("Scheduler stopped")
