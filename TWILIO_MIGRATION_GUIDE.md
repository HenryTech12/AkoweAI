# Twilio Integration Migration Guide

## Overview

This guide explains how to migrate from WhatsApp Business API to Twilio for messaging. Twilio provides a unified platform for SMS and WhatsApp messaging with better reliability and simpler integration.

## Why Twilio?

-   **Reliability**: Better uptime and message delivery guarantees
-   **Unified Platform**: Single API for SMS and WhatsApp
-   **Easier Setup**: No complex Facebook app configuration
-   **Better Support**: Excellent documentation and support
-   **Scalability**: Handles high message volumes easily

## Setup Instructions

### 1. Create a Twilio Account

1. Go to [https://www.twilio.com](https://www.twilio.com)
2. Click "Sign up" and create a new account
3. Verify your email and phone number
4. Complete the account setup

### 2. Get Your Credentials

1. Go to **Console** (top left)
2. You'll see your credentials:

    - **Account SID**: Your main account identifier
    - **Auth Token**: Your authentication token
    - Keep these secure!

3. Get a Twilio Phone Number:
    - Go to **Phone Numbers** → **Buy a Number**
    - Select country and area code
    - Complete purchase

### 3. Enable WhatsApp on Twilio (Optional)

If you want to use WhatsApp instead of just SMS:

1. Go to **Messaging** → **Channels**
2. Click **WhatsApp**
3. Connect your business WhatsApp account or use Twilio's sandbox for testing
4. Note your WhatsApp phone number

### 4. Configure Environment Variables

Create or update your `.env` file:

```env
# Twilio Configuration
TWILIO_ACCOUNT_SID=your_account_sid_here
TWILIO_AUTH_TOKEN=your_auth_token_here
TWILIO_PHONE_NUMBER=+1234567890  # Your Twilio phone number (SMS)
TWILIO_WHATSAPP_NUMBER=+1234567890  # Your Twilio WhatsApp number (optional)
```

### 5. Set Webhook URL in Twilio

1. Go to **Messaging** → **Settings**
2. Under **Webhook URL**, set:

    - For SMS: `https://yourdomain.com/api/v1/webhooks/twilio/sms`
    - For WhatsApp: `https://yourdomain.com/api/v1/webhooks/twilio/whatsapp`

3. Make sure your webhooks are accessible from the internet (not localhost)

### 6. Install Dependencies

```bash
pip install -r requirements.txt
```

This will install:

-   `twilio==8.10.0` - Twilio Python SDK
-   All other existing dependencies

### 7. Update Your Application

The following files have been updated:

#### New Files Created:

-   **`service/twilio_service.py`** - Twilio messaging functions
-   **`tasks/twilio_sender.py`** - Twilio message sending tasks

#### Modified Files:

-   **`config.py`** - Replaced WhatsApp settings with Twilio credentials
-   **`requirements.txt`** - Added `twilio==8.10.0`
-   **`routers/webhooks.py`** - Updated to handle Twilio webhooks
-   **`service/whatsapp_conversation.py`** - Updated to use Twilio service

## Usage

### Sending Text Messages (SMS)

```python
from service.twilio_service import send_text_message

# Send SMS
response = await send_text_message(
    phone_number="+2341234567890",
    message_text="Hello from AkoweAI!"
)
```

### Sending WhatsApp Messages

```python
from service.twilio_service import send_whatsapp_message

# Send WhatsApp message
response = await send_whatsapp_message(
    phone_number="+2341234567890",
    message_text="Hello from AkoweAI via WhatsApp!"
)
```

### Sending Media

```python
from service.twilio_service import send_media_message

# Send image via WhatsApp
response = await send_media_message(
    phone_number="+2341234567890",
    media_url="https://example.com/image.jpg",
    message_text="Here's your receipt",
    use_whatsapp=True
)
```

### Using Celery Tasks

```python
from tasks.twilio_sender import send_message

# Send via Celery queue
send_message.delay(
    phone_number="+2341234567890",
    message_text="Async message",
    use_whatsapp=True
)
```

## Webhook Endpoints

Your application now exposes two webhook endpoints:

### SMS Webhook

-   **Endpoint**: `POST /api/v1/webhooks/twilio/sms`
-   **ConfigureThis in Twilio Console** under Messaging → Settings

### WhatsApp Webhook

-   **Endpoint**: `POST /api/v1/webhooks/twilio/whatsapp`
-   **Configure this in Twilio Console** under Messaging → WhatsApp Settings

Both endpoints are secured with Twilio's request signature validation.

## Testing

### Using Twilio's Sandbox

Twilio provides a WhatsApp sandbox for testing without production setup:

1. Go to **Messaging** → **Try Twilio WhatsApp**
2. Follow the instructions to connect to the sandbox
3. Send test messages using the provided number

### Local Testing

To test locally with ngrok:

```bash
# Install ngrok if you haven't
npm install -g ngrok

# Or using brew on macOS
brew install ngrok

# Start ngrok tunnel
ngrok http 8000

# Update webhook URL in Twilio with your ngrok URL
# e.g., https://xxxxxx.ngrok.io/api/v1/webhooks/twilio/whatsapp
```

## Troubleshooting

### Invalid Signature Error

-   Ensure your `TWILIO_AUTH_TOKEN` is correct
-   Webhook URL must exactly match what's configured in Twilio
-   Must include the full path: `/api/v1/webhooks/twilio/sms`

### Phone Number Formatting

-   Twilio expects E.164 format: `+[country code][number]`
-   Examples: `+2341234567890`, `+1234567890`, `+447911123456`
-   The system automatically formats Nigerian numbers:
    -   `0901234567` → `+2340901234567`
    -   `08123456789` → `+2348123456789`

### Message Not Sending

1. Check your account has available SMS/WhatsApp credits
2. Verify the phone number is in E.164 format
3. Check logs for error messages
4. Ensure webhook URL is properly configured

### Webhook Not Triggering

1. Verify webhook URL is accessible from the internet
2. Check ngrok is running (for local testing)
3. Verify URL matches exactly in Twilio Console
4. Check application logs for errors

## Migration from WhatsApp Business API

### Old Code (WhatsApp Business API)

```python
from service.whatsapp_service import send_text_message
await send_text_message(phone_number, "Message")
```

### New Code (Twilio)

```python
from service.twilio_service import send_whatsapp_message
await send_whatsapp_message(phone_number, "Message")
```

### Key Differences

| Feature        | WhatsApp API          | Twilio                  |
| -------------- | --------------------- | ----------------------- |
| Phone Format   | `234123456789`        | `+2341234567890`        |
| Webhook Format | JSON nested structure | Form data (URL encoded) |
| Media Download | WhatsApp API          | Direct URL access       |
| Verification   | Hub Token             | Request Signature       |

## Support & Documentation

-   **Twilio Docs**: https://www.twilio.com/docs/messaging
-   **WhatsApp on Twilio**: https://www.twilio.com/docs/whatsapp
-   **Python SDK**: https://www.twilio.com/docs/python/install
-   **Webhook Security**: https://www.twilio.com/docs/usage/webhooks/webhooks-security

## Next Steps

1. ✅ Create Twilio account and get credentials
2. ✅ Update `.env` file with your credentials
3. ✅ Test with SMS first (simpler setup)
4. ✅ Enable WhatsApp (optional, more complex)
5. ✅ Run tests to verify integration
6. ✅ Deploy to production

## Rollback (If Needed)

If you need to revert to WhatsApp Business API:

1. Keep the old `whatsapp_service.py` backup
2. Revert webhook changes to use WhatsApp format
3. Update `config.py` to use old WhatsApp settings
4. The old `whatsapp_sender.py` is still compatible

The new implementation has backward-compatible legacy endpoints at `/webhooks/whatsapp` for a smooth transition period.
