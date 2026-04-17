# AkoweAI Backend - Complete Setup Guide

## 📋 Overview

This is the FastAPI backend for AkoweAI, a multilingual AI financial bridge for Africa's invisible MSMEs. The backend handles:

-   WhatsApp message processing and webhooks
-   Audio transcription using OpenAI Whisper
-   Receipt OCR processing using Claude Vision
-   Financial transaction management
-   Report generation
-   User authentication and profiles
-   Async task processing with Celery

## 🛠️ Technology Stack

-   **Framework**: FastAPI
-   **Database**: PostgreSQL
-   **Cache/Broker**: Redis
-   **Task Queue**: Celery
-   **AI APIs**: Claude 3.5 Sonnet, OpenAI Whisper
-   **File Storage**: AWS S3

## 📦 Prerequisites

-   Python 3.9+
-   PostgreSQL 13+
-   Redis 7+
-   Docker & Docker Compose (optional)
-   API Keys:
    -   Claude API Key
    -   OpenAI API Key (for Whisper)
    -   WhatsApp Access Token
    -   AWS Credentials (optional, for file storage)

## 🚀 Quick Start

### Option 1: Using Docker Compose (Recommended)

```bash
# Clone the repository
git clone https://github.com/yourorg/akowe-ai.git
cd akowe-ai/backend

# Copy environment file
cp .env.example .env

# Update .env with your API keys
# CLAUDE_API_KEY, OPENAI_API_KEY, WHATSAPP_ACCESS_TOKEN, etc.

# Start all services
docker-compose up -d

# Check logs
docker-compose logs -f backend

# Access the application
# API: http://localhost:8000
# Docs: http://localhost:8000/docs
# Flower (Celery UI): http://localhost:5555
```

### Option 2: Manual Setup

#### 1. Create Virtual Environment

```bash
python -m venv venv

# On Windows
venv\Scripts\activate

# On macOS/Linux
source venv/bin/activate
```

#### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

#### 3. Setup Environment Variables

```bash
cp .env.example .env

# Edit .env with your configuration
# Required:
# - DATABASE_URL: PostgreSQL connection string
# - REDIS_URL: Redis connection string
# - CLAUDE_API_KEY: Your Claude API key
# - OPENAI_API_KEY: Your OpenAI API key
# - WHATSAPP_ACCESS_TOKEN: Your WhatsApp token
# - JWT_SECRET: A strong secret key for JWT
```

#### 4. Setup Database

```bash
# Make sure PostgreSQL is running
# Create database
createdb akowe_db

# The tables will be created automatically when the app starts
```

#### 5. Run Redis

```bash
# Start Redis server (make sure it's running on port 6379)
redis-server
```

#### 6. Start the Backend

```bash
# In one terminal, start the FastAPI server
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

#### 7. Start Celery Worker (in another terminal)

```bash
celery -A celery_app worker --loglevel=info
```

#### 8. Start Celery Flower for Monitoring (optional)

```bash
celery -A celery_app flower --port=5555
```

## 📚 API Documentation

Once the server is running, access the interactive API documentation:

-   **Swagger UI**: http://localhost:8000/docs
-   **ReDoc**: http://localhost:8000/redoc

### Main Endpoints

#### Authentication

-   `POST /api/v1/auth/register` - Register new user
-   `POST /api/v1/auth/login` - Login user

#### Transactions

-   `POST /api/v1/transactions` - Create transaction
-   `GET /api/v1/transactions` - List transactions
-   `GET /api/v1/transactions/{id}` - Get transaction
-   `PUT /api/v1/transactions/{id}` - Update transaction
-   `DELETE /api/v1/transactions/{id}` - Delete transaction

#### Reports

-   `POST /api/v1/reports/generate` - Generate financial report
-   `GET /api/v1/reports/{id}` - Get report
-   `GET /api/v1/reports` - List reports
-   `POST /api/v1/reports/{id}/share` - Share report with bank

#### User

-   `GET /api/v1/users/me` - Get current user profile
-   `PUT /api/v1/users/me` - Update user profile

#### Health

-   `GET /api/v1/health` - Health check
-   `GET /api/v1/ready` - Readiness check
-   `GET /api/v1/live` - Liveness check

#### Webhooks

-   `GET /webhooks/whatsapp` - WhatsApp webhook verification
-   `POST /webhooks/whatsapp` - WhatsApp message webhook

## 🔧 Configuration

### Environment Variables

See `.env.example` for all available options:

```env
# Database
DATABASE_URL=postgresql://user:password@localhost:5432/akowe_db

# Redis
REDIS_URL=redis://localhost:6379/0

# Celery
CELERY_BROKER_URL=redis://localhost:6379/1
CELERY_RESULT_BACKEND=redis://localhost:6379/1

# APIs
CLAUDE_API_KEY=sk-ant-...
OPENAI_API_KEY=sk-...
WHATSAPP_ACCESS_TOKEN=...

# JWT
JWT_SECRET=your-super-secret-key
JWT_EXPIRATION_HOURS=24

# App
DEBUG=False
ENVIRONMENT=production
```

## 🏗️ Project Structure

```
akowe-ai/
├── main.py                 # FastAPI application
├── config.py              # Configuration settings
├── dependencies.py        # Authentication & dependency injection
├── exceptions.py          # Exception handlers
├── celery_app.py          # Celery configuration
├── db/
│   ├── database.py        # Database connection
│   └── crud.py            # Database operations
├── model/
│   └── database.py        # SQLAlchemy models
├── schema/
│   └── schema.py          # Pydantic schemas
├── service/
│   ├── claude_service.py  # Claude AI integration
│   ├── openai_service.py  # OpenAI Whisper
│   ├── whatsapp_service.py# WhatsApp integration
│   └── s3_service.py      # AWS S3 storage
├── routers/
│   ├── webhooks.py        # WhatsApp webhook
│   ├── transactions.py    # Transaction endpoints
│   ├── reports.py         # Report endpoints
│   ├── users.py           # User endpoints
│   └── health.py          # Health check
├── tasks/
│   ├── voice_processor.py # Audio transcription
│   ├── image_processor.py # Receipt OCR
│   ├── report_generator.py# Report generation
│   └── whatsapp_sender.py # Message sending
├── requirements.txt       # Python dependencies
├── Dockerfile            # Docker image
└── docker-compose.yml    # Docker Compose
```

## 📱 WhatsApp Integration

### Setup WhatsApp Webhook

1. Get your WhatsApp Business Account credentials
2. In Facebook Developer Console:

    - Create an app and add WhatsApp product
    - Get Access Token, Phone ID, and Business Account ID
    - Add webhook URL: `https://your-domain/webhooks/whatsapp`
    - Set Verify Token (same as `WHATSAPP_VERIFY_TOKEN` in .env)

3. Configure in `.env`:

```env
WHATSAPP_ACCESS_TOKEN=your_token
WHATSAPP_PHONE_ID=your_phone_id
WHATSAPP_BUSINESS_ACCOUNT_ID=your_account_id
WHATSAPP_VERIFY_TOKEN=your_verify_token
```

## 🔐 Authentication

The API uses JWT (JSON Web Tokens) for authentication:

1. **Register**: `POST /api/v1/auth/register`

    - Returns `access_token` and `refresh_token`

2. **Use Token**: Add to request headers:
    ```
    Authorization: Bearer <access_token>
    ```

## 📊 Database Schema

Key tables:

-   `users` - User accounts
-   `transactions` - Financial transactions
-   `receipt_images` - Receipt images for OCR
-   `voice_messages` - Voice message transcriptions
-   `reports` - Generated financial reports
-   `report_shares` - Report sharing with banks
-   `ai_jobs` - Async AI processing jobs

## 🚨 Error Handling

All errors return JSON with:

```json
{
    "detail": "Error message",
    "request_id": "unique-request-id",
    "timestamp": "2026-04-15T10:00:00Z"
}
```

## 📝 Logging

Logs are printed to console and can be configured via `LOG_LEVEL`:

-   `DEBUG` - Verbose logging
-   `INFO` - General information (default)
-   `WARNING` - Warnings only
-   `ERROR` - Errors only

## 🧪 Testing

```bash
# Run tests
pytest

# With coverage
pytest --cov

# Specific test file
pytest tests/test_api.py
```

## 🐛 Troubleshooting

### Database Connection Error

```
Check DATABASE_URL format
Ensure PostgreSQL is running
Check database credentials
```

### Redis Connection Error

```
Ensure Redis is running on port 6379
Check REDIS_URL configuration
```

### Celery Not Working

```
Restart Celery worker
Check broker/backend URLs
Review Celery logs
```

### WhatsApp Messages Not Processing

```
Check webhook URL is accessible
Verify webhook signature validation
Review X-Hub-Signature header
Check log files for errors
```

## 🔒 Security Considerations

1. **JWT Secret**: Change `JWT_SECRET` in production
2. **Database**: Use strong passwords for PostgreSQL
3. **API Keys**: Never commit `.env` files
4. **CORS**: Configure allowed origins in production
5. **HTTPS**: Always use HTTPS in production
6. **Rate Limiting**: Consider adding rate limiting middleware
7. **Input Validation**: All inputs validated with Pydantic

## 📈 Monitoring

### Health Endpoints

-   `GET /api/v1/health` - Full health check
-   `GET /api/v1/ready` - Readiness probe
-   `GET /api/v1/live` - Liveness probe

### Celery Monitoring

-   Flower UI: http://localhost:5555
-   Real-time task monitoring and statistics

### Metrics

-   Prometheus metrics available at `/metrics` (if enabled)

## 🚀 Deployment

### Using Docker

```bash
# Build image
docker build -t akowe-backend:latest .

# Run container
docker run -p 8000:8000 \
  -e DATABASE_URL=postgresql://... \
  -e REDIS_URL=redis://... \
  akowe-backend:latest
```

### Using Kubernetes

See `k8s/` directory for Kubernetes manifests (if available)

## 📖 Additional Resources

-   [FastAPI Documentation](https://fastapi.tiangolo.com/)
-   [SQLAlchemy Documentation](https://docs.sqlalchemy.org/)
-   [Celery Documentation](https://docs.celeryproject.org/)
-   [Claude API Documentation](https://docs.anthropic.com/)
-   [OpenAI Whisper API](https://platform.openai.com/docs/guides/speech-to-text)
-   [WhatsApp Graph API](https://developers.facebook.com/docs/whatsapp)

## 📞 Support

For issues or questions:

1. Check the troubleshooting section
2. Review log files for error messages
3. Check API documentation at `/docs`
4. Review the GitHub issues section

## 📄 License

This project is licensed under the MIT License - see LICENSE file for details.

## 🤝 Contributing

Contributions are welcome! Please follow the contribution guidelines in CONTRIBUTING.md
