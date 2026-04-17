"""OpenAI Whisper service for audio transcription."""
import openai
from config import settings
import logging
import os

logger = logging.getLogger(__name__)

openai.api_key = settings.openai_api_key


async def transcribe_audio(audio_file_path: str, language: str = None) -> str:
    """
    Transcribe audio file using OpenAI Whisper.

    Args:
        audio_file_path: Path to audio file (local or S3)
        language: Language code (e.g., 'en', 'yo' for Yoruba)

    Returns:
        Transcribed text
    """
    try:
        with open(audio_file_path, "rb") as audio_file:
            transcript = openai.audio.transcriptions.create(
                model="whisper-1",
                file=audio_file,
                language=language if language else None,
                response_format="text"
            )

        logger.info(f"Audio transcribed successfully: {len(transcript)} characters")
        return transcript

    except Exception as e:
        logger.error(f"Error transcribing audio: {str(e)}")
        raise


async def transcribe_audio_from_bytes(audio_bytes: bytes, filename: str, language: str = None) -> str:
    """
    Transcribe audio from bytes using OpenAI Whisper.

    Args:
        audio_bytes: Audio file bytes
        filename: Name of the audio file
        language: Language code

    Returns:
        Transcribed text
    """
    try:
        from io import BytesIO

        audio_file = BytesIO(audio_bytes)
        audio_file.name = filename

        transcript = openai.audio.transcriptions.create(
            model="whisper-1",
            file=audio_file,
            language=language if language else None,
            response_format="text"
        )

        logger.info(f"Audio transcribed successfully from bytes: {len(transcript)} characters")
        return transcript

    except Exception as e:
        logger.error(f"Error transcribing audio from bytes: {str(e)}")
        raise
