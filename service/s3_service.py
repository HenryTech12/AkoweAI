"""AWS S3 service for file storage."""
import boto3
from config import settings
import logging
from io import BytesIO
import os

logger = logging.getLogger(__name__)

# Create S3 client
s3_client = boto3.client(
    's3',
    aws_access_key_id=settings.aws_access_key_id,
    aws_secret_access_key=settings.aws_secret_access_key,
    region_name=settings.aws_region
)


async def upload_file(file_bytes: bytes, filename: str, folder: str = "") -> str:
    """
    Upload a file to S3.

    Args:
        file_bytes: File content as bytes
        filename: Filename to save as
        folder: Optional folder path

    Returns:
        S3 key path
    """
    try:
        # Create S3 key
        if folder:
            s3_key = f"{folder}/{filename}"
        else:
            s3_key = filename

        # Upload to S3
        s3_client.put_object(
            Bucket=settings.aws_s3_bucket,
            Key=s3_key,
            Body=file_bytes,
            ContentType=_get_content_type(filename)
        )

        logger.info(f"File uploaded to S3: {s3_key}")
        return s3_key

    except Exception as e:
        logger.error(f"Error uploading file to S3: {str(e)}")
        raise


async def download_file(s3_key: str) -> bytes:
    """
    Download a file from S3.

    Args:
        s3_key: S3 key path

    Returns:
        File content as bytes
    """
    try:
        response = s3_client.get_object(
            Bucket=settings.aws_s3_bucket,
            Key=s3_key
        )

        file_bytes = response['Body'].read()
        logger.info(f"File downloaded from S3: {s3_key}")
        return file_bytes

    except Exception as e:
        logger.error(f"Error downloading file from S3: {str(e)}")
        raise


async def get_signed_url(s3_key: str, expiration: int = 3600) -> str:
    """
    Generate a signed URL for a file in S3.

    Args:
        s3_key: S3 key path
        expiration: URL expiration time in seconds

    Returns:
        Signed URL
    """
    try:
        url = s3_client.generate_presigned_url(
            'get_object',
            Params={'Bucket': settings.aws_s3_bucket, 'Key': s3_key},
            ExpiresIn=expiration
        )

        logger.info(f"Signed URL generated for: {s3_key}")
        return url

    except Exception as e:
        logger.error(f"Error generating signed URL: {str(e)}")
        raise


async def delete_file(s3_key: str) -> bool:
    """
    Delete a file from S3.

    Args:
        s3_key: S3 key path

    Returns:
        True if deleted successfully
    """
    try:
        s3_client.delete_object(
            Bucket=settings.aws_s3_bucket,
            Key=s3_key
        )

        logger.info(f"File deleted from S3: {s3_key}")
        return True

    except Exception as e:
        logger.error(f"Error deleting file from S3: {str(e)}")
        return False


def _get_content_type(filename: str) -> str:
    """Determine content type from filename."""
    extension = os.path.splitext(filename)[1].lower()

    content_types = {
        '.pdf': 'application/pdf',
        '.jpg': 'image/jpeg',
        '.jpeg': 'image/jpeg',
        '.png': 'image/png',
        '.gif': 'image/gif',
        '.ogg': 'audio/ogg',
        '.wav': 'audio/wav',
        '.mp3': 'audio/mpeg',
        '.m4a': 'audio/mp4',
        '.txt': 'text/plain',
        '.json': 'application/json'
    }

    return content_types.get(extension, 'application/octet-stream')
