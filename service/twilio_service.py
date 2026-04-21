"""Twilio integration service."""
from twilio.rest import Client
from config import settings
import logging
from typing import Optional
import requests
from urllib.parse import urlparse
import os

logger = logging.getLogger(__name__)


def get_twilio_client() -> Client:
    """Get Twilio client instance."""
    if not settings.twilio_account_sid or not settings.twilio_auth_token:
        raise ValueError("Twilio credentials not configured in environment variables")
    
    return Client(settings.twilio_account_sid, settings.twilio_auth_token)


async def send_text_message(phone_number: str, message_text: str) -> dict:
    """
    Send a text message via Twilio.

    Args:
        phone_number: Recipient phone number (must be in E.164 format, e.g., +2341234567890)
        message_text: Message text

    Returns:
        Response with SID and status
    """
    try:
        client = get_twilio_client()
        
        # Ensure phone number is in E.164 format
        if not phone_number.startswith('+'):
            # Assuming Nigerian number if no country code
            phone_number = f"+234{phone_number.lstrip('0')}" if phone_number.startswith('0') else f"+{phone_number}"
        
        message = client.messages.create(
            body=message_text,
            from_=settings.twilio_phone_number,
            to=phone_number
        )
        
        logger.info(f"Twilio message sent to {phone_number}: {message.sid}")
        return {
            "sid": message.sid,
            "status": message.status,
            "phone_number": phone_number
        }

    except Exception as e:
        logger.error(f"Error sending Twilio message: {str(e)}")
        raise


async def send_whatsapp_message(phone_number: str, message_text: str) -> dict:
    """
    Send a WhatsApp message via Twilio.

    Args:
        phone_number: Recipient phone number (must be in E.164 format)
        message_text: Message text

    Returns:
        Response with SID and status
    """
    try:
        client = get_twilio_client()
        
        # Ensure phone number is in E.164 format or already a WhatsApp number
        if phone_number.startswith("whatsapp:"):
            to_number = phone_number
        else:
            if not phone_number.startswith('+'):
                phone_number = f"+234{phone_number.lstrip('0')}" if phone_number.startswith('0') else f"+{phone_number}"
            to_number = f"whatsapp:{phone_number}"
        
        # Format sender number for WhatsApp
        from_number = settings.twilio_whatsapp_number or settings.twilio_phone_number
        if not from_number.startswith("whatsapp:"):
            from_number = f"whatsapp:{from_number}"
        
        message = client.messages.create(
            body=message_text,
            from_=from_number,
            to=to_number
        )
        
        logger.info(f"Twilio WhatsApp message sent to {phone_number}: {message.sid}")
        return {
            "sid": message.sid,
            "status": message.status,
            "phone_number": phone_number
        }

    except Exception as e:
        logger.error(f"Error sending Twilio WhatsApp message: {str(e)}")
        raise


async def send_media_message(
    phone_number: str,
    media_url: str,
    message_text: Optional[str] = None,
    use_whatsapp: bool = True
) -> dict:
    """
    Send a media message (image, document, etc.) via Twilio.

    Args:
        phone_number: Recipient phone number
        media_url: URL of the media file
        message_text: Optional message text
        use_whatsapp: Whether to send via WhatsApp (True) or SMS (False)

    Returns:
        Response with SID and status
    """
    try:
        client = get_twilio_client()
        
        # Ensure phone number is in E.164 format
        if not phone_number.startswith('+'):
            phone_number = f"+234{phone_number.lstrip('0')}" if phone_number.startswith('0') else f"+{phone_number}"
        
        if use_whatsapp:
            from_number = f"whatsapp:{settings.twilio_whatsapp_number or settings.twilio_phone_number}"
            to_number = f"whatsapp:{phone_number}"
        else:
            from_number = settings.twilio_phone_number
            to_number = phone_number
        
        message = client.messages.create(
            body=message_text or "Media file",
            from_=from_number,
            to=to_number,
            media_url=[media_url]
        )
        
        logger.info(f"Twilio media message sent to {phone_number}: {message.sid}")
        return {
            "sid": message.sid,
            "status": message.status,
            "phone_number": phone_number
        }

    except Exception as e:
        logger.error(f"Error sending Twilio media message: {str(e)}")
        raise


async def download_media(media_sid: str, auth_token: Optional[str] = None) -> bytes:
    """
    Download media from Twilio.

    Args:
        media_sid: Media SID from incoming message
        auth_token: Optional auth token (uses config if not provided)

    Returns:
        Media file bytes
    """
    try:
        client = get_twilio_client()
        
        # Get media instance
        media = client.messages \
            .get(media_sid) \
            .media.list()[0]
        
        if not media.uri:
            raise ValueError("No URI in media response")
        
        # Construct full URL for media
        base_url = "https://api.twilio.com"
        media_url = f"{base_url}{media.uri}"
        
        # Download media with authentication
        auth = (settings.twilio_account_sid, settings.twilio_auth_token)
        response = requests.get(media_url, auth=auth)
        response.raise_for_status()
        
        logger.info(f"Media downloaded from Twilio: {media_sid}")
        return response.content

    except Exception as e:
        logger.error(f"Error downloading Twilio media: {str(e)}")
        raise


async def get_message_details(message_sid: str) -> dict:
    """
    Get details of a Twilio message.

    Args:
        message_sid: Message SID

    Returns:
        Message details
    """
    try:
        client = get_twilio_client()
        message = client.messages.get(message_sid).fetch()
        
        return {
            "sid": message.sid,
            "status": message.status,
            "to": message.to,
            "from": message.from_,
            "body": message.body,
            "date_created": str(message.date_created),
            "date_updated": str(message.date_updated),
            "error_code": message.error_code,
            "error_message": message.error_message
        }

    except Exception as e:
        logger.error(f"Error getting Twilio message details: {str(e)}")
        raise
