"""WhatsApp conversation manager for registration flow (using Twilio)."""
import logging
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from model.database import RegistrationSession, User
from db.crud import create_user
from schema.schema import UserCreate
from service.twilio_service import send_whatsapp_message
from config import settings

logger = logging.getLogger(__name__)

# Registration conversation states
STATES = {
    "awaiting_business_name": 0,
    "awaiting_dialect": 1,
    "awaiting_business_type": 2,
    "completed": 3
}

# Conversation prompts in different dialects
PROMPTS = {
    "business_name": {
        "english": "Welcome to AkoweAI! 👋 Let's set up your account. What's the name of your business?",
        "pidgin": "Welcome to AkoweAI! 👋 Make we set up your account. Wetin be your business name?",
        "yoruba": "Kaabo si AkoweAI! 👋 Jẹ ki a ṣeto akọọnt rẹ. Kini oruko ile-iṣẹ rẹ?",
        "igbo": "Welcome to AkoweAI! 👋 Ka anyị guzobe akaụntụ gị. Kedu aha ụlọ ọrụ gị?",
        "hausa": "Welcome to AkoweAI! 👋 Jiya mu setto akauni ka. Menene sunan kasuwanki?"
    },
    "dialect": {
        "english": "Great! Which language do you prefer? Reply with a number:\n1️⃣ English\n2️⃣ Pidgin\n3️⃣ Yoruba\n4️⃣ Igbo\n5️⃣ Hausa",
        "pidgin": "Nice! Wetin language you prefer? Reply amidst number:\n1️⃣ English\n2️⃣ Pidgin\n3️⃣ Yoruba\n4️⃣ Igbo\n5️⃣ Hausa",
        "yoruba": "O dáa! Ẹ̀kó wo ẹ̀ jọ̀ fúnra mi? Dáhùn pẹ̀lú àpẹ̀rẹ̀:\n1️⃣ English\n2️⃣ Pidgin\n3️⃣ Yoruba\n4️⃣ Igbo\n5️⃣ Hausa",
        "igbo": "Mmā! Kedu asụsụ ị chọrọ? Zaa site na nọmba:\n1️⃣ English\n2️⃣ Pidgin\n3️⃣ Yoruba\n4️⃣ Igbo\n5️⃣ Hausa",
        "hausa": "Al'amari! Wane harshe kake so? Amsa da lambar:\n1️⃣ English\n2️⃣ Pidgin\n3️⃣ Yoruba\n4️⃣ Igbo\n5️⃣ Hausa"
    },
    "business_type": {
        "english": "What type of business do you run? Reply with a number:\n1️⃣ Retail\n2️⃣ Food\n3️⃣ Transport\n4️⃣ Electronics\n5️⃣ Other",
        "pidgin": "Wetin kinda business you dey manage? Reply amidst number:\n1️⃣ Retail\n2️⃣ Food\n3️⃣ Transport\n4️⃣ Electronics\n5️⃣ Other",
        "yoruba": "Irinṣẹ̀ wo ni o ń ṣe? Dáhùn pẹ̀lú àpẹ̀rẹ̀:\n1️⃣ Retail\n2️⃣ Food\n3️⃣ Transport\n4️⃣ Electronics\n5️⃣ Other",
        "igbo": "Elu oru ole ka i na-arụ? Zaa site na nọmba:\n1️⃣ Retail\n2️⃣ Food\n3️⃣ Transport\n4️⃣ Electronics\n5️⃣ Other",
        "hausa": "Wane irin kasua ka ka ke aiki? Amsa da lambar:\n1️⃣ Retail\n2️⃣ Food\n3️⃣ Transport\n4️⃣ Electronics\n5️⃣ Other"
    },
    "confirmation": {
        "english": "✅ Account created successfully!\n📊 Business: {business_name}\n🗣️ Language: {dialect}\n💼 Type: {business_type}\n\nYou can now track your transactions! Send receipts, record expenses, or upload voice notes.",
        "pidgin": "✅ Account don create sharp sharp!\n📊 Business: {business_name}\n🗣️ Language: {dialect}\n💼 Type: {business_type}\n\nYou ready track your money now! Send receipt, record expense, or talk your transactions.",
        "yoruba": "✅ Akọọnt rẹ ti ṣẹ dá!\n📊 Ile-iṣẹ: {business_name}\n🗣️ Ede: {dialect}\n💼 Irú: {business_type}\n\nO le bẹ̀rẹ̀ ṣisọ àwọn onigbajumo. Ranṣẹ awọn ifawolesẹ, ṣe àkopa tabi kọ ọwọ.",
        "igbo": "✅ Akaụntụ gị na-akpụkpụ nwere nke ọma!\n📊 Ụlọ ọrụ: {business_name}\n🗣️ Asụsụ: {dialect}\n💼 Ụdị: {business_type}\n\nI nwere ike irụ ózụ ugbu a! Ziga ndenewu, gbalịa mkpesa, ma ọ bụ magbasa aka.",
        "hausa": "✅ Akauni ya yi aiki sosai!\n📊 Kasua: {business_name}\n🗣️ Harshe: {dialect}\n💼 Nau'i: {business_type}\n\nZa ka iya tukiya harkokin sida. Aika fakiti, rikoodi jaji, ko rubutu muryar."
    }
}

# Mapping for dialect numbers
DIALECT_MAP = {
    "1": "english",
    "2": "pidgin",
    "3": "yoruba",
    "4": "igbo",
    "5": "hausa"
}

# Mapping for business type numbers
BUSINESS_TYPE_MAP = {
    "1": "retail",
    "2": "food",
    "3": "transport",
    "4": "electronics",
    "5": "other"
}


async def start_registration(phone_number: str, db: Session):
    """Start WhatsApp registration flow for new user."""
    try:
        # Check if phone already has active session
        existing_session = db.query(RegistrationSession).filter(
            RegistrationSession.phone_number == phone_number,
            RegistrationSession.step != "completed"
        ).first()

        if existing_session:
            # Resume existing session
            return await handle_registration_step(phone_number, "", db)

        # Create new registration session
        session = RegistrationSession(
            phone_number=phone_number,
            step="awaiting_business_name",
            expires_at=datetime.utcnow() + timedelta(hours=24),
            conversation_state={"started": True}
        )
        db.add(session)
        db.commit()
        db.refresh(session)

        logger.info(f"Started registration for {phone_number}")

        # Send welcome message
        prompt = PROMPTS["business_name"]["english"]
        await send_whatsapp_message(phone_number, prompt)

        return {"status": "registration_started", "step": "awaiting_business_name"}

    except Exception as e:
        logger.error(f"Error starting registration: {str(e)}")
        raise


async def handle_registration_step(phone_number: str, user_response: str, db: Session):
    """Handle user response in registration flow."""
    try:
        # Get active session
        session = db.query(RegistrationSession).filter(
            RegistrationSession.phone_number == phone_number,
            RegistrationSession.step != "completed"
        ).first()

        if not session:
            # No active session, start new one
            return await start_registration(phone_number, db)

        current_step = session.step

        # Process response based on current step
        if current_step == "awaiting_business_name":
            # Validate business name
            if not user_response or len(user_response.strip()) < 2:
                prompt = PROMPTS["business_name"]["english"]
                await send_whatsapp_message(phone_number, "Please enter a valid business name")
                await send_whatsapp_message(phone_number, prompt)
                return {"status": "awaiting_input", "step": current_step}

            session.business_name = user_response.strip()
            session.step = "awaiting_dialect"
            db.commit()

            # Ask for dialect preference
            prompt = PROMPTS["dialect"]["english"]
            await send_whatsapp_message(phone_number, prompt)

            return {"status": "awaiting_input", "step": "awaiting_dialect"}

        elif current_step == "awaiting_dialect":
            # Map number to dialect
            dialect = DIALECT_MAP.get(user_response.strip(), None)
            if not dialect:
                prompt = PROMPTS["dialect"]["english"]
                await send_whatsapp_message(phone_number, "Invalid choice. Please reply with 1-5")
                await send_whatsapp_message(phone_number, prompt)
                return {"status": "awaiting_input", "step": current_step}

            session.preferred_dialect = dialect
            session.step = "awaiting_business_type"
            db.commit()

            # Ask for business type
            prompt = PROMPTS["business_type"][dialect]
            await send_whatsapp_message(phone_number, prompt)

            return {"status": "awaiting_input", "step": "awaiting_business_type"}

        elif current_step == "awaiting_business_type":
            # Map number to business type
            business_type = BUSINESS_TYPE_MAP.get(user_response.strip(), None)
            if not business_type:
                dialect_prompt = session.preferred_dialect or "english"
                prompt = PROMPTS["business_type"][dialect_prompt]
                await send_whatsapp_message(phone_number, "Invalid choice. Please reply with 1-5")
                await send_whatsapp_message(phone_number, prompt)
                return {"status": "awaiting_input", "step": current_step}

            session.business_type = business_type
            session.step = "completed"
            db.commit()

            # Create user account
            user_create = UserCreate(
                phone_number=phone_number,
                business_name=session.business_name,
                preferred_dialect=session.preferred_dialect,
                business_type=session.business_type
            )

            user = create_user(db, user_create)
            logger.info(f"User account created: {user.id}")

            # Send confirmation with tokens
            from dependencies import create_access_token, create_refresh_token
            
            confirmation_prompt = PROMPTS["confirmation"][session.preferred_dialect]
            confirmation = confirmation_prompt.format(
                business_name=session.business_name,
                dialect=session.preferred_dialect,
                business_type=session.business_type
            )

            access_token = create_access_token(str(user.id))
            refresh_token = create_refresh_token(str(user.id))

            # Send confirmation message
            await send_whatsapp_message(phone_number, confirmation)

            # Send tokens in separate message
            token_message = f"""
🔐 Your account is ready! Here are your tokens:

Access Token:
{access_token}

Refresh Token:
{refresh_token}

Keep these safe! Use the access token for API requests.
"""
            await send_whatsapp_message(phone_number, token_message)

            return {
                "status": "registration_complete",
                "user_id": str(user.id),
                "access_token": access_token,
                "refresh_token": refresh_token
            }

    except Exception as e:
        logger.error(f"Error handling registration step: {str(e)}")
        raise


async def get_or_detect_registration_step(phone_number: str, db: Session):
    """Check if phone has active registration or get user."""
    try:
        # Check for active registration session
        session = db.query(RegistrationSession).filter(
            RegistrationSession.phone_number == phone_number,
            RegistrationSession.step != "completed"
        ).first()

        if session:
            return {
                "is_registered": False,
                "in_registration": True,
                "step": session.step
            }

        # Check if user exists
        user = db.query(User).filter(User.phone_number == phone_number).first()

        if user:
            return {
                "is_registered": True,
                "in_registration": False,
                "user_id": str(user.id)
            }

        # New user, no session
        return {
            "is_registered": False,
            "in_registration": False
        }

    except Exception as e:
        logger.error(f"Error detecting registration state: {str(e)}")
        raise


async def cancel_registration(phone_number: str, db: Session):
    """Cancel active registration session."""
    try:
        session = db.query(RegistrationSession).filter(
            RegistrationSession.phone_number == phone_number,
            RegistrationSession.step != "completed"
        ).first()

        if session:
            db.delete(session)
            db.commit()
            logger.info(f"Cancelled registration for {phone_number}")
            await send_whatsapp_message(phone_number, "Registration cancelled. Send any message to start again.")

    except Exception as e:
        logger.error(f"Error cancelling registration: {str(e)}")
        raise
