"""Twilio message sending task."""
import logging
from service.twilio_service import send_text_message, send_whatsapp_message

logger = logging.getLogger(__name__)


async def send_sms_message(phone_number: str, message_text: str):
    """
    Send SMS message via Twilio.

    Args:
        phone_number: Recipient phone number
        message_text: Message text

    Returns:
        Response from Twilio API
    """
    try:
        response = await send_text_message(phone_number, message_text)
        logger.info(f"SMS message sent to {phone_number}")
        return response

    except Exception as e:
        logger.error(f"Error sending SMS message: {str(e)}")
        raise


async def send_message(phone_number: str, message_text: str, use_whatsapp: bool = True):
    """
    Send message via Twilio (SMS or WhatsApp).

    Args:
        phone_number: Recipient phone number
        message_text: Message text
        use_whatsapp: Whether to use WhatsApp (True) or SMS (False)

    Returns:
        Response from Twilio API
    """
    try:
        if use_whatsapp:
            response = await send_whatsapp_message(phone_number, message_text)
            logger.info(f"WhatsApp message sent to {phone_number}")
        else:
            response = await send_text_message(phone_number, message_text)
            logger.info(f"SMS message sent to {phone_number}")
        return response

    except Exception as e:
        logger.error(f"Error sending message: {str(e)}")
        raise
