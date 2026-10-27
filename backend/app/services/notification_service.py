from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from typing import Optional
from app.models.notification import Notification, NotificationAttempt, NotificationType, NotificationChannel, NotificationStatus
from app.models.patient import Patient
from app.models.appointment import Appointment
from app.core.config import settings
import logging

logger = logging.getLogger(__name__)


def schedule_appointment_reminder(
    db: Session,
    appointment_id: int,
    hours_before: int = 24
) -> Notification:
    """Schedule appointment reminder notification."""
    
    appointment = db.query(Appointment).filter(Appointment.id == appointment_id).first()
    if not appointment:
        raise ValueError("Appointment not found")
    
    patient = db.query(Patient).filter(Patient.id == appointment.patient_id).first()
    if not patient or not patient.consent_for_communication:
        logger.info(f"Skipping reminder for patient {patient.id} - no consent")
        return None
    
    # Determine channel based on preference
    channel = _get_preferred_channel(patient)
    
    # Schedule time
    scheduled_time = appointment.scheduled_date - timedelta(hours=hours_before)
    
    # Create message
    message = f"""
Dear {patient.full_name},

This is a reminder for your upcoming appointment:
Date: {appointment.scheduled_date.strftime('%B %d, %Y at %I:%M %p')}
Type: {appointment.appointment_type.value.replace('_', ' ').title()}
Department: {appointment.department or 'General'}

Please confirm your attendance or contact us to reschedule.

{settings.HOSPITAL_NAME}
{settings.HOSPITAL_PHONE}
    """.strip()
    
    notification = Notification(
        patient_id=patient.id,
        appointment_id=appointment_id,
        notification_type=NotificationType.APPOINTMENT_REMINDER,
        channel=channel,
        subject="Appointment Reminder",
        message=message,
        scheduled_for=scheduled_time,
        max_attempts=settings.MAX_REMINDER_ATTEMPTS
    )
    
    db.add(notification)
    db.commit()
    db.refresh(notification)
    
    return notification


def send_notification(db: Session, notification_id: int) -> bool:
    """
    Send notification through appropriate channel.
    
    NOTE: This is a placeholder. In production, integrate with actual
    email/SMS providers (SendGrid, Twilio, etc.)
    """
    
    notification = db.query(Notification).filter(Notification.id == notification_id).first()
    if not notification:
        return False
    
    # Check if already sent or max attempts reached
    if notification.status in [NotificationStatus.DELIVERED, NotificationStatus.CANCELLED]:
        return False
    
    if notification.attempt_count >= notification.max_attempts:
        notification.status = NotificationStatus.FAILED
        notification.error_message = "Maximum delivery attempts reached"
        db.commit()
        return False
    
    # Create attempt record
    attempt = NotificationAttempt(
        notification_id=notification.id,
        status="attempting"
    )
    db.add(attempt)
    notification.attempt_count += 1
    
    try:
        # Simulate sending based on channel
        if notification.channel == NotificationChannel.EMAIL:
            success = _send_email(notification)
        elif notification.channel == NotificationChannel.SMS:
            success = _send_sms(notification)
        elif notification.channel == NotificationChannel.PHONE:
            success = _make_call(notification)
        else:
            success = True  # In-app notifications are always "sent"
        
        if success:
            notification.status = NotificationStatus.DELIVERED
            notification.sent_at = datetime.utcnow()
            notification.delivered_at = datetime.utcnow()
            attempt.status = "delivered"
            logger.info(f"Notification {notification.id} delivered successfully")
        else:
            attempt.status = "failed"
            attempt.error_message = "Delivery failed"
            logger.warning(f"Notification {notification.id} delivery failed")
        
    except Exception as e:
        attempt.status = "failed"
        attempt.error_message = str(e)
        notification.error_message = str(e)
        logger.error(f"Notification {notification.id} error: {e}")
    
    db.commit()
    return notification.status == NotificationStatus.DELIVERED


def _get_preferred_channel(patient: Patient) -> NotificationChannel:
    """Determine preferred notification channel for patient."""
    pref = patient.communication_preference
    
    if pref == "email" and patient.email:
        return NotificationChannel.EMAIL
    elif pref == "sms" and patient.phone:
        return NotificationChannel.SMS
    elif pref == "phone" and patient.phone:
        return NotificationChannel.PHONE
    elif patient.email:
        return NotificationChannel.EMAIL
    elif patient.phone:
        return NotificationChannel.SMS
    else:
        return NotificationChannel.IN_APP


def _send_email(notification: Notification) -> bool:
    """Send email notification (placeholder)."""
    # In production, integrate with SendGrid, AWS SES, etc.
    logger.info(f"[PLACEHOLDER] Sending email: {notification.subject}")
    return True


def _send_sms(notification: Notification) -> bool:
    """Send SMS notification (placeholder)."""
    # In production, integrate with Twilio, AWS SNS, etc.
    logger.info(f"[PLACEHOLDER] Sending SMS: {notification.message[:50]}...")
    return True


def _make_call(notification: Notification) -> bool:
    """Make phone call (placeholder)."""
    # In production, integrate with Twilio Voice API, etc.
    logger.info(f"[PLACEHOLDER] Making call for notification {notification.id}")
    return True
