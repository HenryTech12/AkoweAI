# Twilio Integration - Quick Reference

## Environment Variables Template

Copy this to your `.env` file and replace with your actual values:

```env
# ========== TWILIO CONFIGURATION ==========
# Get these from https://www.twilio.com/console

# Your Twilio Account SID (found at the top of your console)
TWILIO_ACCOUNT_SID=ACxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx

# Your Twilio Auth Token (keep this SECRET!)
TWILIO_AUTH_TOKEN=your_actual_auth_token_here

# Your Twilio SMS Phone Number (get from Phone Numbers section)
# Format: +1 area code and number, e.g., +15551234567
TWILIO_PHONE_NUMBER=+1555123456

# Your WhatsApp Phone Number (if using WhatsApp)
# Can be the same as TWILIO_PHONE_NUMBER if using sandbox
# Format: +1 area code and number
TWILIO_WHATSAPP_NUMBER=+1555123456
```

## API Comparison

### Sending Messages

#### SMS (Text Message)

```python
from service.twilio_service import send_text_message

await send_text_message(
    phone_number="+2341234567890",
    message_text="Your message here"
)
```

#### WhatsApp

```python
from service.twilio_service import send_whatsapp_message

await send_whatsapp_message(
    phone_number="+2341234567890",
    message_text="Your message here"
)
```

#### Media (Image, Document, etc.)

```python
from service.twilio_service import send_media_message

await send_media_message(
    phone_number="+2341234567890",
    media_url="https://example.com/file.jpg",
    message_text="Optional caption",
    use_whatsapp=True  # Set to False for SMS
)
```

### Using with Celery

```python
from tasks.twilio_sender import send_message

# Queue message for async sending
send_message.delay(
    phone_number="+2341234567890",
    message_text="Your message",
    use_whatsapp=True
)
```

## Webhook Endpoints

### Receive SMS

```
POST /api/v1/webhooks/twilio/sms
```

### Receive WhatsApp

```
POST /api/v1/webhooks/twilio/whatsapp
```

Both require Twilio webhook URL configured in console.

## Phone Number Formatting

### Automatic Formatting

Nigerian numbers are automatically converted to E.164:

-   Input: `0901234567` or `901234567`
-   Output: `+2340901234567`

### Manual Formatting

Always use E.164 format with country code:

-   Nigeria: `+234` followed by number without leading 0
-   Example: `+2341234567890`
-   United States: `+1` followed by number
-   Example: `+15551234567`

## Status Codes

All functions return status information:

```python
{
    "sid": "SMxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx",  # Twilio message ID
    "status": "queued",  # or "sent", "delivered", "failed"
    "phone_number": "+2341234567890"
}
```

## Error Handling

```python
from service.twilio_service import send_whatsapp_message

try:
    response = await send_whatsapp_message(
        phone_number="+2341234567890",
        message_text="Test message"
    )
    print(f"Message sent: {response['sid']}")
except Exception as e:
    print(f"Failed to send: {str(e)}")
```

## Testing Checklist

-   [ ] Create Twilio account
-   [ ] Get Account SID and Auth Token
-   [ ] Purchase or use sandbox phone number
-   [ ] Add credentials to `.env` file
-   [ ] Install dependencies: `pip install -r requirements.txt`
-   [ ] Test sending SMS via test script
-   [ ] Test sending WhatsApp (if enabled)
-   [ ] Configure webhook URL in Twilio console
-   [ ] Test receiving messages
-   [ ] Deploy to production

## Common Issues

### "Unauthorized - Invalid credentials"

-   Check `TWILIO_ACCOUNT_SID` and `TWILIO_AUTH_TOKEN`
-   Verify you copied them correctly from Twilio console
-   Auth tokens are sensitive - don't commit to Git

### "Cannot GET /webhooks/twilio/sms"

-   Ensure you're using `POST` method, not `GET`
-   Webhook URL should include full path
-   Verify URL matches in Twilio console

### "Invalid phone number format"

-   Use E.164 format: `+[country][number]`
-   For Nigeria, remove leading 0: `234...` not `0...`
-   Twilio validates all phone numbers

### "Webhook not being called"

-   Verify webhook URL is publicly accessible
-   Use ngrok for local testing: `ngrok http 8000`
-   Check logs for incoming requests
-   Verify URL matches exactly in console

## Getting Help

1. **Twilio Console**: Check message logs at https://www.twilio.com/console/sms/logs
2. **Python SDK Docs**: https://www.twilio.com/docs/python/
3. **WhatsApp on Twilio**: https://www.twilio.com/docs/whatsapp
4. **Webhook Debugging**: Use request logging middleware

## Key Files

-   **Service**: `service/twilio_service.py` - Main Twilio functions
-   **Tasks**: `tasks/twilio_sender.py` - Celery tasks
-   **Webhooks**: `routers/webhooks.py` - Incoming message handlers
-   **Config**: `config.py` - Twilio credentials
-   **Conversation**: `service/whatsapp_conversation.py` - Registration flow
