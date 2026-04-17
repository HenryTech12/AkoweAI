"""Celery configuration for async task processing."""
from celery import Celery
from config import settings
import logging

logger = logging.getLogger(__name__)

# Create Celery app
celery_app = Celery(
    'akowe',
    broker=settings.celery_broker_url,
    backend=settings.celery_result_backend
)

# Configure Celery
celery_app.conf.update(
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    timezone='Africa/Lagos',
    enable_utc=True,
    task_track_started=True,
    task_time_limit=30 * 60,  # 30 minute hard limit
    task_soft_time_limit=25 * 60,  # 25 minute soft limit
)


# Voice transcription task
@celery_app.task(bind=True, max_retries=3, name='tasks.process_voice_message')
def process_voice_message_task(self, user_id: str, audio_s3_key: str, dialect: str):
    """
    Process voice message with retries.

    Args:
        user_id: User ID
        audio_s3_key: S3 key for audio file
        dialect: Detected dialect
    """
    try:
        from tasks.voice_processor import process_voice
        return process_voice(user_id, audio_s3_key, dialect)
    except Exception as exc:
        logger.error(f"Error processing voice message: {str(exc)}")
        raise self.retry(exc=exc, countdown=60 * (2 ** self.request.retries))


# Receipt image OCR task
@celery_app.task(bind=True, max_retries=3, name='tasks.process_receipt_image')
def process_receipt_image_task(self, user_id: str, image_s3_key: str):
    """
    Process receipt image with retries.

    Args:
        user_id: User ID
        image_s3_key: S3 key for image file
    """
    try:
        from tasks.image_processor import process_image
        return process_image(user_id, image_s3_key)
    except Exception as exc:
        logger.error(f"Error processing receipt image: {str(exc)}")
        raise self.retry(exc=exc, countdown=60 * (2 ** self.request.retries))


# Financial report generation task
@celery_app.task(name='tasks.generate_financial_report')
def generate_financial_report_task(user_id: str, report_type: str, start_date: str, end_date: str):
    """
    Generate financial report.

    Args:
        user_id: User ID
        report_type: Type of report
        start_date: Report start date
        end_date: Report end date
    """
    try:
        from tasks.report_generator import generate_report
        return generate_report(user_id, report_type, start_date, end_date)
    except Exception as exc:
        logger.error(f"Error generating report: {str(exc)}")
        raise


# WhatsApp message task
@celery_app.task(name='tasks.send_whatsapp_message')
def send_whatsapp_message_task(phone_number: str, message_text: str):
    """
    Send WhatsApp message.

    Args:
        phone_number: Recipient phone number
        message_text: Message text
    """
    try:
        from tasks.whatsapp_sender import send_message
        return send_message(phone_number, message_text)
    except Exception as exc:
        logger.error(f"Error sending WhatsApp message: {str(exc)}")
        raise
