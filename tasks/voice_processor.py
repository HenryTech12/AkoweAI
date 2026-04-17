"""Voice message processing task."""
import logging
from sqlalchemy.orm import Session
from model.database import SessionLocal
from db.crud import create_voice_message, update_voice_transcription, create_transaction
from service.openai_service import transcribe_audio_from_bytes
from service.claude_service import extract_transaction_from_text, analyze_dialect
from service.cloudinary_service import download_file
from schema.schema import TransactionCreate
from datetime import datetime

logger = logging.getLogger(__name__)


async def process_voice(user_id: str, audio_s3_key: str, dialect: str):
    """
    Process voice message:
    1. Download audio from S3
    2. Transcribe with Whisper
    3. Extract transaction with Claude
    4. Store in database
    """
    db: Session = SessionLocal()

    try:
        # Create voice message record
        voice = create_voice_message(db, user_id, audio_s3_key, dialect)
        logger.info(f"Created voice message record: {voice.id}")

        # Download audio from S3
        audio_bytes = await download_file(audio_s3_key)
        logger.info(f"Downloaded audio from S3: {audio_s3_key}")

        # Transcribe audio
        transcription = await transcribe_audio_from_bytes(
            audio_bytes,
            audio_s3_key.split('/')[-1],
            language=_get_whisper_language_code(dialect)
        )
        logger.info(f"Transcribed audio: {transcription[:100]}...")

        # Detect dialect if not provided
        detected_dialect = await analyze_dialect(transcription) if dialect == "auto" else dialect

        # Update voice record with transcription
        update_voice_transcription(db, voice.id, transcription, "completed")

        # Extract transaction from transcription
        transaction_data_raw = await extract_transaction_from_text(
            transcription,
            dialect=detected_dialect,
            user_id=user_id
        )

        # Create transaction
        transaction_create = TransactionCreate(
            amount=transaction_data_raw.get("amount"),
            currency=transaction_data_raw.get("currency", "NGN"),
            category=transaction_data_raw.get("category"),
            description=transaction_data_raw.get("description"),
            transaction_date=datetime.fromisoformat(
                transaction_data_raw.get("transaction_date", datetime.utcnow().isoformat())
            ),
            counterparty=transaction_data_raw.get("counterparty")
        )

        transaction = create_transaction(db, user_id, transaction_create)
        logger.info(f"Created transaction: {transaction.id}")

        # Update voice message with transaction link
        voice.transaction_id = transaction.id
        db.commit()

        return {
            "status": "success",
            "voice_id": str(voice.id),
            "transaction_id": str(transaction.id),
            "transcription": transcription
        }

    except Exception as e:
        logger.error(f"Error processing voice message: {str(e)}")
        # Update voice record with error
        update_voice_transcription(db, voice.id, str(e), "failed")
        raise

    finally:
        db.close()


def _get_whisper_language_code(dialect: str) -> str:
    """Map dialect to Whisper language code."""
    dialect_map = {
        "english": "en",
        "pidgin": "en",  # Whisper English also handles Pidgin
        "yoruba": "yo",
        "igbo": "ig",
        "hausa": "ha",
    }
    return dialect_map.get(dialect, "en")
