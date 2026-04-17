"""Cloudinary service for file storage."""
import cloudinary
import cloudinary.uploader
import cloudinary.api
from config import settings
import logging
from io import BytesIO
import os
from typing import Optional

logger = logging.getLogger(__name__)

# Configure Cloudinary
cloudinary.config(
    cloud_name=settings.cloudinary_cloud_name,
    api_key=settings.cloudinary_api_key,
    api_secret=settings.cloudinary_api_secret
)


async def upload_file(file_bytes: bytes, filename: str, folder: str = "") -> str:
    """
    Upload a file to Cloudinary.

    Args:
        file_bytes: File content as bytes
        filename: Filename to save as
        folder: Optional folder path (becomes the public_id prefix)

    Returns:
        Cloudinary public_id (full path)
    """
    try:
        # Create public_id with folder path
        if folder:
            public_id = f"{folder}/{os.path.splitext(filename)[0]}"
        else:
            public_id = os.path.splitext(filename)[0]

        # Determine resource type
        resource_type = _get_resource_type(filename)

        # Upload to Cloudinary
        result = cloudinary.uploader.upload(
            file_bytes,
            public_id=public_id,
            resource_type=resource_type,
            overwrite=True,
            invalidate=True
        )

        logger.info(f"File uploaded to Cloudinary: {result['public_id']}")
        return result['public_id']

    except Exception as e:
        logger.error(f"Error uploading file to Cloudinary: {str(e)}")
        raise


async def download_file(public_id: str) -> bytes:
    """
    Download a file from Cloudinary.

    Args:
        public_id: Cloudinary public_id (file path)

    Returns:
        File content as bytes
    """
    try:
        import requests

        # Get the secure URL for the file
        url = cloudinary.CloudinaryResource(public_id).build_url(secure=True)

        # Download the file
        response = requests.get(url)
        response.raise_for_status()

        file_bytes = response.content
        logger.info(f"File downloaded from Cloudinary: {public_id}")
        return file_bytes

    except Exception as e:
        logger.error(f"Error downloading file from Cloudinary: {str(e)}")
        raise


async def get_secure_url(public_id: str, expiration: int = 3600) -> str:
    """
    Generate a secure/signed URL for a file in Cloudinary.

    Args:
        public_id: Cloudinary public_id (file path)
        expiration: URL expiration time in seconds

    Returns:
        Secure URL
    """
    try:
        url = cloudinary.CloudinaryResource(public_id).build_url(
            secure=True,
            sign_url=True,
            expires_at=int(__import__('time').time()) + expiration
        )

        logger.info(f"Secure URL generated for: {public_id}")
        return url

    except Exception as e:
        logger.error(f"Error generating secure URL: {str(e)}")
        raise


async def get_public_url(public_id: str) -> str:
    """
    Generate a public URL for a file in Cloudinary.

    Args:
        public_id: Cloudinary public_id (file path)

    Returns:
        Public URL
    """
    try:
        url = cloudinary.CloudinaryResource(public_id).build_url(secure=True)
        logger.info(f"Public URL generated for: {public_id}")
        return url

    except Exception as e:
        logger.error(f"Error generating public URL: {str(e)}")
        raise


async def delete_file(public_id: str) -> bool:
    """
    Delete a file from Cloudinary.

    Args:
        public_id: Cloudinary public_id (file path)

    Returns:
        True if deleted successfully
    """
    try:
        resource_type = _get_resource_type_from_public_id(public_id)
        result = cloudinary.uploader.destroy(public_id, resource_type=resource_type)

        if result.get('result') == 'ok':
            logger.info(f"File deleted from Cloudinary: {public_id}")
            return True
        else:
            logger.warning(f"File deletion returned non-ok result: {result}")
            return False

    except Exception as e:
        logger.error(f"Error deleting file from Cloudinary: {str(e)}")
        return False


async def delete_folder(folder_path: str) -> bool:
    """
    Delete all files in a folder from Cloudinary.

    Args:
        folder_path: Folder path in Cloudinary

    Returns:
        True if deletion successful
    """
    try:
        result = cloudinary.api.delete_resources_by_prefix(folder_path)
        logger.info(f"Folder deleted from Cloudinary: {folder_path}")
        return True

    except Exception as e:
        logger.error(f"Error deleting folder from Cloudinary: {str(e)}")
        return False


async def get_file_info(public_id: str) -> dict:
    """
    Get metadata about a file in Cloudinary.

    Args:
        public_id: Cloudinary public_id (file path)

    Returns:
        File metadata dictionary
    """
    try:
        resource_type = _get_resource_type_from_public_id(public_id)
        result = cloudinary.api.resource(public_id, resource_type=resource_type)

        return {
            "public_id": result.get('public_id'),
            "format": result.get('format'),
            "size": result.get('bytes'),
            "url": result.get('secure_url'),
            "created_at": result.get('created_at'),
            "resource_type": result.get('resource_type'),
            "width": result.get('width'),
            "height": result.get('height'),
        }

    except Exception as e:
        logger.error(f"Error getting file info from Cloudinary: {str(e)}")
        raise


def _get_resource_type(filename: str) -> str:
    """
    Determine Cloudinary resource type from filename.
    Returns: 'image', 'video', 'raw', or 'auto'
    """
    extension = os.path.splitext(filename)[1].lower()

    image_extensions = {'.jpg', '.jpeg', '.png', '.gif', '.webp', '.bmp', '.svg', '.ico'}
    video_extensions = {'.mp4', '.webm', '.ogg', '.mov', '.avi', '.mkv'}
    audio_extensions = {'.mp3', '.wav', '.m4a', '.aac', '.flac', '.ogg', '.wma'}

    if extension in image_extensions:
        return 'image'
    elif extension in video_extensions:
        return 'video'
    elif extension in audio_extensions:
        return 'raw'  # Audio files as raw
    else:
        return 'raw'  # Everything else as raw


def _get_resource_type_from_public_id(public_id: str) -> str:
    """
    Infer resource type from public_id based on common patterns.
    """
    # Common folder patterns
    if '/audio/' in public_id:
        return 'raw'
    elif '/documents/' in public_id:
        return 'raw'
    elif '/receipts/' in public_id or '/images/' in public_id:
        return 'image'
    elif '/video/' in public_id:
        return 'video'
    elif '/reports/' in public_id:
        return 'raw'
    else:
        return 'raw'  # Default to raw


# Backward compatibility - alias for file downloads
async def download_media(public_id: str) -> bytes:
    """
    Download media from Cloudinary (alias for download_file).
    
    Args:
        public_id: Cloudinary public_id
        
    Returns:
        Media file bytes
    """
    return await download_file(public_id)


# Backward compatibility - alias for signed URLs
async def get_signed_url(public_id: str, expiration: int = 3600) -> str:
    """
    Generate a signed URL for a file (alias for get_secure_url).
    
    Args:
        public_id: Cloudinary public_id
        expiration: URL expiration in seconds
        
    Returns:
        Signed URL
    """
    return await get_secure_url(public_id, expiration)
