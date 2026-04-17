"""WhatsApp integration service."""
import requests
from config import settings
import logging
from typing import Optional

logger = logging.getLogger(__name__)

WHATSAPP_API_URL = "https://graph.instagram.com/v18.0/"


async def send_text_message(phone_number: str, message_text: str) -> dict:
    """
    Send a text message via WhatsApp.

    Args:
        phone_number: Recipient phone number
        message_text: Message text

    Returns:
        Response from WhatsApp API
    """
    try:
        url = f"{WHATSAPP_API_URL}{settings.whatsapp_phone_id}/messages"

        headers = {
            "Authorization": f"Bearer {settings.whatsapp_access_token}",
            "Content-Type": "application/json"
        }

        payload = {
            "messaging_product": "whatsapp",
            "recipient_type": "individual",
            "to": phone_number,
            "type": "text",
            "text": {"body": message_text}
        }

        response = requests.post(url, json=payload, headers=headers)
        response.raise_for_status()

        logger.info(f"WhatsApp message sent to {phone_number}")
        return response.json()

    except Exception as e:
        logger.error(f"Error sending WhatsApp message: {str(e)}")
        raise


async def send_document_message(phone_number: str, document_url: str, caption: Optional[str] = None) -> dict:
    """
    Send a document via WhatsApp.

    Args:
        phone_number: Recipient phone number
        document_url: URL of the document
        caption: Optional caption

    Returns:
        Response from WhatsApp API
    """
    try:
        url = f"{WHATSAPP_API_URL}{settings.whatsapp_phone_id}/messages"

        headers = {
            "Authorization": f"Bearer {settings.whatsapp_access_token}",
            "Content-Type": "application/json"
        }

        payload = {
            "messaging_product": "whatsapp",
            "to": phone_number,
            "type": "document",
            "document": {
                "link": document_url,
                "caption": caption or "Your Financial Report"
            }
        }

        response = requests.post(url, json=payload, headers=headers)
        response.raise_for_status()

        logger.info(f"WhatsApp document sent to {phone_number}")
        return response.json()

    except Exception as e:
        logger.error(f"Error sending WhatsApp document: {str(e)}")
        raise


async def download_media(media_id: str) -> bytes:
    """
    Download media from WhatsApp.

    Args:
        media_id: Media ID from WhatsApp

    Returns:
        Media file bytes
    """
    try:
        url = f"{WHATSAPP_API_URL}{media_id}"
        headers = {
            "Authorization": f"Bearer {settings.whatsapp_access_token}"
        }

        # First, get the media URL
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        media_data = response.json()

        if "url" not in media_data:
            raise ValueError("No URL in media response")

        # Download the actual media
        media_response = requests.get(media_data["url"], headers=headers)
        media_response.raise_for_status()

        logger.info(f"Media downloaded from WhatsApp: {media_id}")
        return media_response.content

    except Exception as e:
        logger.error(f"Error downloading WhatsApp media: {str(e)}")
        raise


async def verify_webhook_signature(body: str, signature: str) -> bool:
    """
    Verify WhatsApp webhook signature.

    Args:
        body: Request body
        signature: X-Hub-Signature header

    Returns:
        True if valid, False otherwise
    """
    try:
        import hmac
        import hashlib

        # Extract the hash from signature
        hash_algorithm, hash_value = signature.split('=')

        # Create the expected signature
        expected_signature = hmac.new(
            settings.whatsapp_access_token.encode(),
            body.encode(),
            hashlib.sha1
        ).hexdigest()

        is_valid = hmac.compare_digest(hash_value, expected_signature)

        if not is_valid:
            logger.warning("Invalid WhatsApp webhook signature")

        return is_valid

    except Exception as e:
        logger.error(f"Error verifying webhook signature: {str(e)}")
        return False
