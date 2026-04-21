"""Receipt image processing task."""
import logging
import asyncio
from sqlalchemy.orm import Session
from model.database import SessionLocal
from db.crud import create_receipt_image, update_receipt_extraction, create_transaction
from service.claude_service import extract_transaction_from_text
from service.cloudinary_service import download_file
from schema.schema import TransactionCreate
from datetime import datetime
from uuid import UUID

logger = logging.getLogger(__name__)


def _extract_text_from_image(image_bytes: bytes, image_s3_key: str) -> dict:
    """
    Extract text from image using Claude Vision.
    
    Returns: Dictionary with extracted text and metadata
    """
    # This would call Claude Vision API
    # For now, returning a placeholder
    return {
        "text": "",
        "metadata": {
            "filename": image_s3_key,
            "size": len(image_bytes)
        }
    }


def process_image(user_id: str, image_s3_key: str):
    """
    Process receipt image:
    1. Download image from Cloudinary
    2. Extract text with OCR (Claude Vision)
    3. Extract transaction data
    4. Store in database
    """
    db: Session = SessionLocal()

    try:
        # Convert user_id to UUID if string
        if isinstance(user_id, str):
            user_id = UUID(user_id)

        # Create receipt image record
        receipt = create_receipt_image(db, user_id, image_s3_key)
        logger.info(f"Created receipt image record: {receipt.id}")

        # Download image from Cloudinary (run in event loop)
        image_bytes = asyncio.run(download_file(image_s3_key))
        logger.info(f"Downloaded image from Cloudinary: {image_s3_key}")

        # Extract text from image using Claude Vision
        extracted_data = _extract_text_from_image(image_bytes, image_s3_key)
        logger.info(f"Extracted text from image: {extracted_data}")

        # Extract transaction from extracted text
        transaction_text = extracted_data.get("text", "")
        transaction_data_raw = asyncio.run(extract_transaction_from_text(
            transaction_text,
            user_id=str(user_id)
        ))

        # Update receipt record with extraction
        update_receipt_extraction(db, receipt.id, extracted_data, "completed")

        # Create transaction
        transaction_create = TransactionCreate(
            amount=transaction_data_raw.get("amount"),
            currency=transaction_data_raw.get("currency", "NGN"),
            category=transaction_data_raw.get("category"),
            description=transaction_data_raw.get("description"),
            transaction_date=datetime.fromisoformat(
                transaction_data_raw.get("transaction_date", datetime.utcnow().isoformat())
            ),
            counterparty=transaction_data_raw.get("counterparty"),
            source="image"
        )

        transaction = create_transaction(db, user_id, transaction_create)
        logger.info(f"Created transaction from image: {transaction.id}")

        # Update receipt with transaction link
        receipt.transaction_id = transaction.id
        db.commit()

        return {
            "status": "success",
            "receipt_id": str(receipt.id),
            "transaction_id": str(transaction.id),
            "extracted_data": extracted_data
        }

    except Exception as e:
        logger.error(f"Error processing receipt image: {str(e)}")
        # Update receipt record with error
        try:
            update_receipt_extraction(db, receipt.id, {"error": str(e)}, "failed")
        except:
            pass
        raise
    """
    Process receipt image:
    1. Download image from S3
    2. Extract text with OCR (Claude Vision)
    3. Extract transaction data
    4. Store in database
    """
    db: Session = SessionLocal()

    try:
        # Create receipt image record
        receipt = create_receipt_image(db, user_id, image_s3_key)
        logger.info(f"Created receipt image record: {receipt.id}")

        # Download image from S3
        image_bytes = await download_file(image_s3_key)
        logger.info(f"Downloaded image from S3: {image_s3_key}")

        # Extract text from image using Claude Vision
        extracted_data = _extract_text_from_image(image_bytes, image_s3_key)
        logger.info(f"Extracted text from image: {extracted_data}")

        # Extract transaction from extracted text
        transaction_text = extracted_data.get("text", "")
        transaction_data_raw = await extract_transaction_from_text(
            transaction_text,
            user_id=user_id
        )

        # Update receipt record with extraction
        update_receipt_extraction(db, receipt.id, extracted_data, "completed")

        # Create transaction
        transaction_create = TransactionCreate(
            amount=transaction_data_raw.get("amount"),
            currency=transaction_data_raw.get("currency", "NGN"),
            category=transaction_data_raw.get("category"),
            description=transaction_data_raw.get("description"),
            transaction_date=datetime.fromisoformat(
                transaction_data_raw.get("transaction_date", datetime.utcnow().isoformat())
            ),
            counterparty=transaction_data_raw.get("counterparty"),
            source="image"
        )

        transaction = create_transaction(db, user_id, transaction_create)
        logger.info(f"Created transaction from image: {transaction.id}")

        # Update receipt with transaction link
        receipt.transaction_id = transaction.id
        db.commit()

        return {
            "status": "success",
            "receipt_id": str(receipt.id),
            "transaction_id": str(transaction.id),
            "extracted_data": extracted_data
        }

    except Exception as e:
        logger.error(f"Error processing receipt image: {str(e)}")
        # Update receipt record with error
        update_receipt_extraction(db, receipt.id, {"error": str(e)}, "failed")
        raise

    finally:
        db.close()


def _extract_text_from_image(image_bytes: bytes, filename: str) -> dict:
    """
    Extract text from image using Claude Vision.

    Args:
        image_bytes: Image file bytes
        filename: Image filename

    Returns:
        Dictionary with extracted data
    """
    try:
        from anthropic import Anthropic
        import base64

        client = Anthropic()

        # Encode image to base64
        encoded_image = base64.standard_b64encode(image_bytes).decode("utf-8")

        # Determine image type from filename
        extension = filename.split('.')[-1].lower()
        media_type_map = {
            'jpg': 'image/jpeg',
            'jpeg': 'image/jpeg',
            'png': 'image/png',
            'gif': 'image/gif',
            'webp': 'image/webp'
        }
        media_type = media_type_map.get(extension, 'image/jpeg')

        # Use Claude Vision to extract text
        message = client.messages.create(
            model="claude-3-5-sonnet-20241022",
            max_tokens=1024,
            messages=[
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "image",
                            "source": {
                                "type": "base64",
                                "media_type": media_type,
                                "data": encoded_image,
                            },
                        },
                        {
                            "type": "text",
                            "text": "Extract all text and financial information from this receipt. Return as structured JSON with fields: store_name, items, total_amount, currency, date, payment_method, and raw_text."
                        }
                    ],
                }
            ],
        )

        import json
        response_text = message.content[0].text
        extracted_data = json.loads(response_text)

        return extracted_data

    except Exception as e:
        logger.error(f"Error extracting text from image: {str(e)}")
        raise
