"""Webhook endpoints for Twilio integration (WhatsApp and SMS)."""
from fastapi import APIRouter, Request, Depends, status, Form
from fastapi.responses import PlainTextResponse, JSONResponse
from sqlalchemy.orm import Session
from service.twilio_service import download_media
from model.database import get_db
from db.crud import get_user_by_phone, create_transaction
from schema.schema import TransactionCreate
from celery_app import process_voice_message_task, process_receipt_image_task
from config import settings
from datetime import datetime
from service.whatsapp_conversation import (
    start_registration, handle_registration_step, get_or_detect_registration_step
)
from twilio.request_validator import RequestValidator
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/webhooks", tags=["webhooks"])


def verify_twilio_request(request_url: str, request_params: dict, signature: str) -> bool:
    """
    Verify that the request came from Twilio.

    Args:
        request_url: The full URL of the webhook
        request_params: The POST parameters
        signature: The X-Twilio-Signature header value

    Returns:
        True if request is from Twilio, False otherwise
    """
    try:
        validator = RequestValidator(settings.twilio_auth_token)
        return validator.validate(request_url, request_params, signature)
    except Exception as e:
        logger.error(f"Error validating Twilio request: {str(e)}")
        return False


@router.post("/twilio/sms")
async def receive_sms_message(request: Request, db: Session = Depends(get_db)):
    """
    Receive SMS messages from Twilio.

    Supports:
    - Text messages
    """
    try:
        # Get form parameters
        form_data = await request.form()
        request_params = dict(form_data)

        # Get signature from header
        signature = request.headers.get("X-Twilio-Signature", "")
        request_url = str(request.url)

        # Verify request is from Twilio
        if not verify_twilio_request(request_url, request_params, signature):
            logger.warning("Invalid Twilio SMS request signature")
            return PlainTextResponse("Unauthorized", status_code=403)

        logger.info(f"Received Twilio SMS webhook: {request_params}")

        # Extract message information
        phone_number = request_params.get("From")
        message_text = request_params.get("Body", "")
        message_sid = request_params.get("MessageSid")

        await _process_sms_message(phone_number, message_text, message_sid, db)

        # Return empty response to Twilio
        return PlainTextResponse("", status_code=204)

    except Exception as e:
        logger.error(f"Error processing Twilio SMS webhook: {str(e)}")
        return PlainTextResponse("", status_code=204)


@router.post("/twilio/whatsapp")
async def receive_whatsapp_message(request: Request, db: Session = Depends(get_db)):
    """
    Receive WhatsApp messages from Twilio.

    Supports:
    - Text messages
    - Audio (voice notes)
    - Images (receipts)
    - Documents
    """
    try:
        # Get form parameters
        form_data = await request.form()
        request_params = dict(form_data)

        # Get signature from header
        signature = request.headers.get("X-Twilio-Signature", "")
        request_url = str(request.url)

        # Verify request is from Twilio
        if not verify_twilio_request(request_url, request_params, signature):
            logger.warning("Invalid Twilio WhatsApp request signature")
            return PlainTextResponse("Unauthorized", status_code=403)

        logger.info(f"Received Twilio WhatsApp webhook: {request_params}")

        # Extract message information
        phone_number = request_params.get("From")
        message_body = request_params.get("Body", "")
        message_sid = request_params.get("MessageSid")
        media_count = int(request_params.get("NumMedia", 0))

        await _process_whatsapp_message(phone_number, message_body, media_count, request_params, message_sid, db)

        # Return empty response to Twilio
        return PlainTextResponse("", status_code=204)

    except Exception as e:
        logger.error(f"Error processing Twilio WhatsApp webhook: {str(e)}")
        return PlainTextResponse("", status_code=204)


async def _process_sms_message(phone_number: str, message_text: str, message_sid: str, db: Session):
    """Process individual SMS message from Twilio."""
    try:
        # Normalize phone number (Twilio provides E.164 format)
        if not phone_number:
            logger.warning("No phone number in SMS message")
            return

        logger.info(f"SMS from {phone_number}: {message_text}")

        # Check if user exists or is in registration flow
        registration_state = await get_or_detect_registration_step(phone_number, db)

        # Handle registration flow
        if not registration_state["is_registered"] and not registration_state["in_registration"]:
            # New user - start registration
            logger.info(f"New user detected: {phone_number}")
            await start_registration(phone_number, db)
            return

        elif not registration_state["is_registered"] and registration_state["in_registration"]:
            # User in registration flow
            if message_text.strip():
                await handle_registration_step(phone_number, message_text, db)
            return

        # Registered user - proceed with normal operations
        user = get_user_by_phone(db, phone_number)
        if not user:
            logger.warning(f"User should exist but not found: {phone_number}")
            return

        user_id = str(user.id)
        logger.info(f"Text message from registered user {phone_number}: {message_text}")

        # TODO: Handle text message - could trigger transaction creation or commands

    except Exception as e:
        logger.error(f"Error processing SMS message: {str(e)}")


async def _process_whatsapp_message(
    phone_number: str,
    message_body: str,
    media_count: int,
    request_params: dict,
    message_sid: str,
    db: Session
):
    """Process individual WhatsApp message from Twilio."""
    try:
        # Normalize phone number
        if not phone_number:
            logger.warning("No phone number in WhatsApp message")
            return

        # Check if user exists or is in registration flow
        registration_state = await get_or_detect_registration_step(phone_number, db)

        # Handle registration flow
        if not registration_state["is_registered"] and not registration_state["in_registration"]:
            # New user - start registration
            logger.info(f"New user detected: {phone_number}")
            if message_body.strip() or media_count > 0:
                await start_registration(phone_number, db)
            return

        elif not registration_state["is_registered"] and registration_state["in_registration"]:
            # User in registration flow
            if message_body.strip():
                await handle_registration_step(phone_number, message_body, db)
            return

        # Registered user - proceed with normal operations
        user = get_user_by_phone(db, phone_number)
        if not user:
            logger.warning(f"User should exist but not found: {phone_number}")
            return

        user_id = str(user.id)

        # Process text message
        if message_body.strip():
            logger.info(f"WhatsApp text from {phone_number}: {message_body}")
            # TODO: Handle text message

        # Process media files
        if media_count > 0:
            await _process_whatsapp_media(request_params, user_id, message_sid, db)

    except Exception as e:
        logger.error(f"Error processing WhatsApp message: {str(e)}")


async def _process_whatsapp_media(request_params: dict, user_id: str, message_sid: str, db: Session):
    """Process media files from WhatsApp message."""
    try:
        media_count = int(request_params.get("NumMedia", 0))

        for i in range(media_count):
            media_url = request_params.get(f"MediaUrl{i}")
            media_type = request_params.get(f"MediaContentType{i}", "")

            if not media_url:
                continue

            logger.info(f"Processing {media_type} media from WhatsApp message")

            # Download media from Twilio
            import requests
            try:
                response = requests.get(media_url)
                response.raise_for_status()
                media_bytes = response.content
            except Exception as e:
                logger.error(f"Error downloading media from Twilio: {str(e)}")
                continue

            # Save to S3 and process based on type
            from service.cloudinary_service import upload_file

            if media_type.startswith("audio/"):
                logger.info(f"Audio message from user {user_id}")
                s3_key = await upload_file(
                    media_bytes,
                    f"audio_{message_sid}.ogg",
                    f"messages/{user_id}/audio"
                )
                # Queue async task for transcription
                from model.database import User
                user = db.query(User).filter(User.id == user_id).first()
                if user:
                    process_voice_message_task.delay(user_id, s3_key, user.preferred_dialect)

            elif media_type.startswith("image/"):
                logger.info(f"Image message from user {user_id}")
                s3_key = await upload_file(
                    media_bytes,
                    f"receipt_{message_sid}.jpg",
                    f"messages/{user_id}/receipts"
                )
                # Queue async task for OCR
                process_receipt_image_task.delay(user_id, s3_key)

            elif media_type.startswith("application/"):
                logger.info(f"Document message from user {user_id}")
                s3_key = await upload_file(
                    media_bytes,
                    f"document_{message_sid}",
                    f"messages/{user_id}/documents"
                )
                # TODO: Handle document if needed

    except Exception as e:
        logger.error(f"Error processing WhatsApp media: {str(e)}")


# Backward compatibility: Keep old WhatsApp webhook endpoint but redirect to new one
@router.get("/whatsapp")
async def legacy_verify_whatsapp_webhook(
    hub_mode: str = None,
    hub_challenge: str = None,
    hub_verify_token: str = None
) -> PlainTextResponse:
    """
    Legacy WhatsApp webhook verification endpoint.
    Deprecated - use /twilio/whatsapp instead.
    """
    logger.warning("Legacy WhatsApp webhook endpoint called - please update to use Twilio")
    return PlainTextResponse("Please update to Twilio integration", status_code=301)


@router.post("/whatsapp")
async def legacy_receive_whatsapp_message(request: Request, db: Session = Depends(get_db)):
    """
    Legacy WhatsApp webhook endpoint.
    Deprecated - use /twilio/whatsapp instead.
    """
    logger.warning("Legacy WhatsApp webhook endpoint called - please update to use Twilio")
    return JSONResponse({"status": "deprecated"}, status_code=301)
