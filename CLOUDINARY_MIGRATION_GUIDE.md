# Cloudinary Integration Migration Guide

## Overview

This guide explains how to migrate from AWS S3 to Cloudinary for file storage. Cloudinary is a modern, developer-friendly cloud storage platform with built-in image optimization, transformations, and delivery.

## Why Cloudinary?

-   **Simpler Setup**: No complex IAM roles or bucket policies
-   **Built-in Optimization**: Automatic image compression and optimization
-   **Better Performance**: Global CDN with automatic optimization
-   **Generous Free Tier**: Up to 25 GB storage and 25 GB bandwidth free
-   **Developer-Friendly**: Simple SDK and API
-   **Easier Integration**: Less infrastructure management

## Setup Instructions

### 1. Create a Cloudinary Account

1. Go to [https://cloudinary.com](https://cloudinary.com)
2. Click "Sign up for free"
3. Complete the registration with your email
4. Verify your email
5. Complete account setup

### 2. Get Your Credentials

1. Go to your **Dashboard** (top right corner, account menu)
2. You'll see your credentials:
    - **Cloud Name**: Your unique identifier
    - **API Key**: Your API key
    - **API Secret**: Your secret key (keep this safe!)

Example dashboard URL: `https://console.cloudinary.com/console/c-[your-cloud-name]`

### 3. Configure Environment Variables

Create or update your `.env` file:

```env
# Cloudinary Configuration
CLOUDINARY_CLOUD_NAME=your_cloud_name_here
CLOUDINARY_API_KEY=your_api_key_here
CLOUDINARY_API_SECRET=your_api_secret_here
```

⚠️ **IMPORTANT**: Never commit `CLOUDINARY_API_SECRET` to version control!

### 4. Install Dependencies

```bash
pip install -r requirements.txt
```

This will install:

-   `cloudinary==1.35.0` - Cloudinary Python SDK
-   All other existing dependencies

### 5. Update Your Application

The following files have been updated:

**New Files Created:**

-   **`service/cloudinary_service.py`** - Cloudinary file operations

**Modified Files:**

-   **`config.py`** - Replaced AWS with Cloudinary credentials
-   **`requirements.txt`** - Added `cloudinary==1.35.0`, removed `boto3`
-   **`routers/webhooks.py`** - Uses cloudinary_service
-   **`tasks/voice_processor.py`** - Uses cloudinary_service
-   **`tasks/image_processor.py`** - Uses cloudinary_service
-   **`tasks/report_generator.py`** - Uses cloudinary_service

## Usage

### Uploading Files

```python
from service.cloudinary_service import upload_file

# Upload a file
public_id = await upload_file(
    file_bytes=file_content,
    filename="receipt.jpg",
    folder="messages/receipts"
)

# Returns: "messages/receipts/receipt"
```

### Downloading Files

```python
from service.cloudinary_service import download_file

# Download a file
file_bytes = await download_file(public_id="messages/receipts/receipt")
```

### Getting File URLs

```python
from service.cloudinary_service import get_public_url, get_secure_url

# Get public URL (no expiration)
public_url = await get_public_url("messages/receipts/receipt")
# Returns: https://res.cloudinary.com/[cloud-name]/image/upload/.../receipt

# Get secure/signed URL (with expiration)
secure_url = await get_secure_url(
    public_id="messages/receipts/receipt",
    expiration=3600  # 1 hour
)
```

### Deleting Files

```python
from service.cloudinary_service import delete_file, delete_folder

# Delete a single file
success = await delete_file("messages/receipts/receipt")

# Delete all files in a folder
success = await delete_folder("messages/receipts")
```

### Getting File Information

```python
from service.cloudinary_service import get_file_info

# Get metadata about a file
info = await get_file_info("messages/receipts/receipt")
# Returns size, format, URL, dimensions, etc.
```

## File Organization

Cloudinary doesn't have actual folders, but you can organize files using path-like public_ids:

```
messages/
  audio/audio_12345.ogg
  receipts/receipt_67890.jpg
  documents/doc_11111.pdf

reports/
  user_123/
    monthly_2024_01.pdf
    monthly_2024_02.pdf

profiles/
  user_456/
    avatar.jpg
```

## API Comparison: AWS S3 → Cloudinary

| Operation  | AWS S3                         | Cloudinary                                          |
| ---------- | ------------------------------ | --------------------------------------------------- |
| Upload     | `s3_client.put_object(...)`    | `cloudinary.uploader.upload(...)`                   |
| Download   | `s3_client.get_object(...)`    | `cloudinary.CloudinaryResource(...).build_url(...)` |
| Delete     | `s3_client.delete_object(...)` | `cloudinary.uploader.destroy(...)`                  |
| Signed URL | `generate_presigned_url(...)`  | `build_url(sign_url=True)`                          |
| Public URL | Construct manually             | `build_url()`                                       |

## Benefits of Cloudinary

### 1. Image Optimization

Automatically optimize images on upload:

```python
# Cloudinary automatically compresses/optimizes
await upload_file(file_bytes, "photo.jpg", "images")
```

### 2. URL-Based Transformations

Modify images on-the-fly via URL:

```
# Resize to 300x300 and crop
https://res.cloudinary.com/[cloud-name]/image/upload/c_fill,w_300,h_300/v1/photo.jpg

# Convert to WebP and compress
https://res.cloudinary.com/[cloud-name]/image/upload/f_auto,q_auto/v1/photo.jpg

# Blur for privacy
https://res.cloudinary.com/[cloud-name]/image/upload/e_blur:300/v1/photo.jpg
```

### 3. Built-in Media Management

-   View all uploaded files in dashboard
-   Easy file management console
-   Folder organization
-   Search and filter capabilities

### 4. Security

-   Fine-grained access control
-   Signed URLs with expiration
-   Restricted delivery domains
-   API tokens with restricted permissions

## Monitoring & Limits

### Free Tier Includes:

-   25 GB storage
-   25 GB bandwidth/month
-   Unlimited transformations
-   Unlimited API calls

### Check Usage:

1. Go to Cloudinary Dashboard
2. Click **Account Settings**
3. View **Media Statistics**
4. See storage used and bandwidth consumed

### Upgrade When Needed:

Plans start from $99/month for 100 GB storage and 100 GB bandwidth.

## Troubleshooting

### "AuthenticationError: Invalid credentials"

-   Verify `CLOUDINARY_CLOUD_NAME`, `CLOUDINARY_API_KEY`, `CLOUDINARY_API_SECRET`
-   Check you copied them correctly from dashboard
-   API Secret is case-sensitive

### "ResourceNotFound: Can't find resource"

-   Try with correct `public_id` (includes folder path)
-   Example: `messages/receipts/receipt` not just `receipt`
-   File must exist before downloading

### File Upload Fails

-   Check file is not too large (free tier supports up to 100MB per file)
-   Verify file format is supported
-   Check internet connection
-   Enable debug logging

### Slow Performance

-   Cloudinary should have near-instant performance
-   Check your network speed
-   Try from different region
-   Check Cloudinary status page

## Migration from AWS S3

### Old Code (AWS S3)

```python
from service.s3_service import upload_file, download_file, get_signed_url

# Upload
s3_key = await upload_file(file_bytes, "file.pdf", "reports")

# Download
file_bytes = await download_file(s3_key)

# Signed URL
url = await get_signed_url(s3_key, 3600)
```

### New Code (Cloudinary)

```python
from service.cloudinary_service import upload_file, download_file, get_secure_url

# Upload (same interface!)
public_id = await upload_file(file_bytes, "file.pdf", "reports")

# Download (same interface!)
file_bytes = await download_file(public_id)

# Secure URL (same interface!)
url = await get_secure_url(public_id, 3600)
```

✅ **Interface is almost identical!** Minimal code changes needed.

## Database Migrations

If you stored S3 keys in database, you need to update them. Since Cloudinary uses the same path format (including folder prefix), the migration is simpler:

**Before:** `reports/user_123/report_2024.pdf`
**After:** `reports/user_123/report_2024.pdf` (same!)

The `public_id` format is compatible with the folder structure used in S3 keys.

## Support & Documentation

-   **Cloudinary Console**: https://console.cloudinary.com
-   **API Documentation**: https://cloudinary.com/documentation
-   **Python SDK**: https://cloudinary.com/documentation/python_integration
-   **Video Tutorials**: https://cloudinary.com/documentation/how_to_integrate_cloudinary
-   **Support**: https://support.cloudinary.com

## Next Steps

1. ✅ Create Cloudinary account
2. ✅ Get credentials from dashboard
3. ✅ Update `.env` file
4. ✅ Install dependencies: `pip install -r requirements.txt`
5. ✅ Update any database records with old S3 paths (optional - paths are same)
6. ✅ Test file upload/download
7. ✅ Deploy to production

## Rollback Plan

If you need to revert to AWS S3:

1. Keep old `s3_service.py` backed up
2. Update imports from `cloudinary_service` back to `s3_service`
3. Restore AWS credentials to `config.py`
4. Reinstall `boto3` in requirements.txt

The function signatures are identical, so minimal code changes needed to rollback.
