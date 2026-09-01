from celery import shared_task
from django.core.mail import send_mail
from celery import shared_task
from django.utils import timezone
import logging

logger = logging.getLogger(__name__)
@shared_task
def send_email_task(subject, message, recipient_list):
    """
    Celery task to send an email asynchronously.
    recipient_list should be a list of email addresses.
    """
    send_mail(
        subject,
        message,
        from_email=None,  # uses DEFAULT_FROM_EMAIL
        recipient_list=recipient_list,
        fail_silently=False,
    )
    return f"Email sent to {recipient_list}"

@shared_task
def daily_test_task():
    logger.info(f"Celery Beat test task executed at {timezone.now()}")
    return "Daily test task completed"
