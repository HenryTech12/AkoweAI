"""WhatsApp message sending task."""
import logging
from service.whatsapp_service import send_text_message

logger = logging.getLogger(__name__)


async def send_message(phone_number: str, message_text: str):
    """
    Send WhatsApp message.

    Args:
        phone_number: Recipient phone number
        message_text: Message text

    Returns:
        Response from WhatsApp API
    """
    try:
        response = await send_text_message(phone_number, message_text)
        logger.info(f"WhatsApp message sent to {phone_number}")
        return response

    except Exception as e:
        logger.error(f"Error sending WhatsApp message: {str(e)}")
        raise
