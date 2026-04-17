# Cloudinary Integration - Quick Reference

## Environment Variables Setup

Copy to your `.env` file:

```env
# Get these from https://cloudinary.com/console
CLOUDINARY_CLOUD_NAME=your_cloud_name_here
CLOUDINARY_API_KEY=your_api_key_here
CLOUDINARY_API_SECRET=your_api_secret_here_keep_secure
```

## Core API Functions

### Upload File

```python
from service.cloudinary_service import upload_file

public_id = await upload_file(
    file_bytes=file_content,
    filename="receipt.jpg",
    folder="messages/receipts"
)
# Returns: "messages/receipts/receipt"
```

### Download File

```python
from service.cloudinary_service import download_file

file_bytes = await download_file(public_id="messages/receipts/receipt")
```

### Get Public URL

```python
from service.cloudinary_service import get_public_url

url = await get_public_url("messages/receipts/receipt")
# Returns: https://res.cloudinary.com/[cloud-name]/image/upload/.../receipt
```

### Get Secure/Signed URL

```python
from service.cloudinary_service import get_secure_url

url = await get_secure_url(
    public_id="messages/receipts/receipt",
    expiration=3600  # expires in 1 hour
)
```

### Delete File

```python
from service.cloudinary_service import delete_file

success = await delete_file("messages/receipts/receipt")
```

### Delete Folder

```python
from service.cloudinary_service import delete_folder

success = await delete_folder("messages/receipts")
```

### Get File Info

```python
from service.cloudinary_service import get_file_info

info = await get_file_info("messages/receipts/receipt")
# Returns: {"size": 102400, "format": "jpg", "url": "...", "created_at": "..."}
```

## File Organization

Cloudinary uses path-like `public_id` for organization:

```
messages/
  audio/{user_id}/audio_message.ogg
  receipts/{user_id}/receipt_image.jpg
  documents/{user_id}/doc.pdf

reports/
  {user_id}/monthly_report_{date}.pdf

profiles/
  {user_id}/avatar.jpg
```

## Supported File Types

### Images

-   `.jpg`, `.jpeg` - JPEG images
-   `.png` - PNG images
-   `.gif` - Animated GIFs
-   `.webp` - WebP format
-   `.bmp`, `.svg`, `.ico`

### Audio

-   `.mp3` - MPEG audio
-   `.wav` - WAV audio
-   `.ogg` - Ogg Vorbis
-   `.m4a`, `.aac`, `.flac`

### Documents

-   `.pdf` - PDF files
-   `.doc`, `.docx` - Word documents
-   `.txt` - Text files
-   Any other file type

## Common Patterns

### Audio Upload from WhatsApp

```python
from service.cloudinary_service import upload_file

audio_id = await upload_file(
    file_bytes=audio_bytes,
    filename="voice_message.ogg",
    folder=f"messages/{user_id}/audio"
)
# Returns: "messages/{user_id}/audio/voice_message"
```

### Receipt Image Upload

```python
receipt_id = await upload_file(
    file_bytes=image_bytes,
    filename="receipt.jpg",
    folder=f"messages/{user_id}/receipts"
)
# Returns: "messages/{user_id}/receipts/receipt"
```

### Report PDF Upload

```python
report_id = await upload_file(
    file_bytes=pdf_bytes,
    filename=f"monthly_{date}.pdf",
    folder=f"reports/{user_id}"
)
# Returns: "reports/{user_id}/monthly_{date}"
```

## URL Building

Cloudinary uses URL transformations. Build URLs for different purposes:

### Default (Secure HTTPS)

```
https://res.cloudinary.com/[cloud-name]/image/upload/v1/messages/receipts/receipt
```

### Resize Image

```
https://res.cloudinary.com/[cloud-name]/image/upload/w_300,h_300,c_fill/v1/receipt.jpg
```

### Optimize for Web

```
https://res.cloudinary.com/[cloud-name]/image/upload/f_auto,q_auto/v1/photo.jpg
```

### Auto-detect Format & Quality

```
https://res.cloudinary.com/[cloud-name]/image/upload/q_auto,f_auto/v1/image.jpg
```

## Error Handling

```python
from service.cloudinary_service import upload_file

try:
    public_id = await upload_file(
        file_bytes=file_content,
        filename="document.pdf",
        folder="documents"
    )
    print(f"Uploaded: {public_id}")
except Exception as e:
    print(f"Upload failed: {str(e)}")
```

## Cloudinary Dashboard Features

1. **Media Library**: Browse all uploaded files
2. **Folder Organization**: Create and manage folders
3. **Search**: Find files by public_id or tag
4. **Analytics**: View bandwidth and storage usage
5. **Settings**: Configure delivery URLs, authentication, etc.

Access at: https://console.cloudinary.com/console/c-[your-cloud-name]

## Comparison: S3 vs Cloudinary

| Feature             | AWS S3         | Cloudinary          |
| ------------------- | -------------- | ------------------- |
| Setup Complexity    | High           | Low                 |
| Free Tier           | Minimal        | Generous (25GB)     |
| Image Optimization  | Manual         | Automatic           |
| URL Transformations | Not native     | Built-in            |
| API Simplicity      | Complex        | Simple              |
| CDN                 | Via CloudFront | Built-in Global CDN |
| Learning Curve      | Steep          | Gentle              |

## File Naming Best Practices

### DO:

-   Use descriptive filenames: `receipt_20240117.jpg`
-   Use folders for organization: `messages/{user_id}/receipts`
-   Use lowercase with underscores: `voice_message.ogg`

### DON'T:

-   Use special characters in filenames
-   Use spaces in filenames
-   Use very long filenames (max 200 chars)
-   Skip folder organization: just `file.jpg`

## Performance Tips

1. **Use HTTPS**: All URLs are secure by default
2. **Enable Caching**: Use Secure URLs with expiration for private content
3. **Optimize Images**: Cloudinary does this automatically
4. **Use CDN**: Cloudinary's CDN is global and fast
5. **Check Usage**: Monitor dashboard for limits

## Free Tier Limits

-   **Storage**: 25 GB
-   **Bandwidth**: 25 GB/month
-   **File Size**: 100 MB per file
-   **API Calls**: Unlimited
-   **Transformations**: Unlimited

## Testing Checklist

-   [ ] Create Cloudinary account
-   [ ] Copy credentials to `.env` file
-   [ ] Run `pip install -r requirements.txt`
-   [ ] Test file upload
-   [ ] Test file download
-   [ ] Generate and test URLs
-   [ ] Check Cloudinary dashboard for uploaded files
-   [ ] Test file deletion
-   [ ] Monitor free tier usage

## Getting Help

1. **Documentation**: https://cloudinary.com/documentation
2. **Dashboard**: https://console.cloudinary.com
3. **Support**: https://support.cloudinary.com
4. **Status**: https://status.cloudinary.com
5. **Community**: https://community.cloudinary.com

## Key Files

-   **Service**: `service/cloudinary_service.py` - Main Cloudinary functions
-   **Config**: `config.py` - Cloudinary credentials
-   **Tasks**: `tasks/*.py` - Uses cloudinary_service
-   **Webhooks**: `routers/webhooks.py` - File uploads
