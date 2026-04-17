# AkoweAI - Backend Engineer Implementation Guide

**Target Audience:** Backend Engineers  
**Date:** April 2026  
**Project:** AkoweAI - Multilingual AI Financial Bridge for Africa's Invisible MSMEs

---

## Table of Contents

1. [Quick Start](#quick-start)
2. [Architecture Overview](#architecture-overview)
3. [API Specification](#api-specification)
4. [Database Design](#database-design)
5. [Message Queue System](#message-queue-system)
6. [Error Handling & Monitoring](#error-handling--monitoring)
7. [Deployment](#deployment)

---

## Quick Start

### Prerequisites

-   Python 3.9+
-   PostgreSQL 13+
-   Redis 7+
-   Docker & Docker Compose

### Setup

```bash
# Clone and navigate
git clone https://github.com/yourorg/akowe-ai.git
cd akowe-ai/backend

# Create virtual environment
python -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Environment setup
cp .env.example .env
# Update with:
# - CLAUDE_API_KEY
# - OPENAI_API_KEY
# - WHATSAPP_ACCESS_TOKEN
# - DATABASE_URL
# - REDIS_URL

# Run migrations
alembic upgrade head

# Start development
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

---

## Architecture Overview

### System Components

```
WhatsApp Input → Webhook Handler → Message Router → Processing Queue
                                                          ↓
                                              Claude 3.5 + Whisper
                                                          ↓
                                              PostgreSQL Database
                                                          ↓
                                              Report Generator
                                                          ↓
                                              WhatsApp Output
```

### Tech Stack

| Layer              | Technology                        |
| ------------------ | --------------------------------- |
| **API Framework**  | FastAPI (async)                   |
| **Database**       | PostgreSQL + SQLAlchemy ORM       |
| **Cache**          | Redis                             |
| **Task Queue**     | Celery + RabbitMQ                 |
| **PDF Generation** | ReportLab + WeasyPrint            |
| **File Storage**   | AWS S3 / Firebase Storage         |
| **AI/ML APIs**     | Claude 3.5 Sonnet, OpenAI Whisper |

---

## API Specification

### 1. Webhook Endpoints

#### Verify WhatsApp Webhook

```
GET /api/v1/webhooks/whatsapp?hub.mode=subscribe&hub.challenge=XXX&hub.verify_token=XXX

Response: 200 OK
Body: hub.challenge value (for WhatsApp verification)
```

#### Receive WhatsApp Messages

```
POST /api/v1/webhooks/whatsapp

Headers:
- X-Hub-Signature: sha1=<signature>
- Content-Type: application/json

Request Body:
{
  "object": "whatsapp_business_account",
  "entry": [
    {
      "id": "123456",
      "changes": [
        {
          "value": {
            "messaging_product": "whatsapp",
            "messages": [
              {
                "from": "254XXXXXXXXX",
                "id": "wamid.XXX",
                "message_status": "delivered",
                "timestamp": "1234567890",
                "type": "text|audio|image|document",
                "text": { "body": "message content" },
                "audio": { "id": "audio_id", "mime_type": "audio/ogg" },
                "image": { "id": "image_id", "mime_type": "image/jpeg" },
                "document": { "id": "doc_id", "mime_type": "application/pdf" }
              }
            ]
          }
        }
      ]
    }
  ]
}

Response: 200 OK
{
  "status": "received",
  "job_id": "uuid"
}
```

### 2. Transaction Endpoints

#### Create Transaction

```
POST /api/v1/transactions

Headers:
- Authorization: Bearer <jwt_token>
- Content-Type: application/json

Request Body:
{
  "amount": 50000,
  "currency": "NGN",
  "category": "expense|income|debt",
  "description": "Fuel purchase",
  "transaction_date": "2026-04-15",
  "counterparty": "Shell Nigeria",
  "items": [
    {
      "name": "Diesel",
      "quantity": 10,
      "unit_price": 5000
    }
  ]
}

Response: 201 Created
{
  "id": "uuid",
  "user_id": "uuid",
  "status": "created",
  "created_at": "2026-04-15T10:00:00Z"
}
```

#### List Transactions

```
GET /api/v1/transactions?start_date=2026-03-15&end_date=2026-04-15&category=expense&limit=50&offset=0

Headers:
- Authorization: Bearer <jwt_token>

Response: 200 OK
{
  "total": 150,
  "limit": 50,
  "offset": 0,
  "transactions": [
    {
      "id": "uuid",
      "amount": 50000,
      "category": "expense",
      "description": "Fuel",
      "created_at": "2026-04-15T10:00:00Z",
      "source": "voice|image|text",
      "confidence": 0.95
    }
  ]
}
```

#### Update Transaction

```
PUT /api/v1/transactions/:transaction_id

Headers:
- Authorization: Bearer <jwt_token>
- Content-Type: application/json

Request Body:
{
  "amount": 55000,
  "category": "expense",
  "description": "Updated description"
}

Response: 200 OK
{
  "id": "uuid",
  "updated_at": "2026-04-15T11:00:00Z"
}
```

#### Delete Transaction

```
DELETE /api/v1/transactions/:transaction_id

Headers:
- Authorization: Bearer <jwt_token>

Response: 200 OK
{
  "status": "deleted",
  "deleted_at": "2026-04-15T11:00:00Z"
}
```

### 3. Report Endpoints

#### Generate Report

```
POST /api/v1/reports/generate

Headers:
- Authorization: Bearer <jwt_token>
- Content-Type: application/json

Request Body:
{
  "report_type": "credit-ready|monthly|quarterly|custom",
  "start_date": "2025-10-15",
  "end_date": "2026-04-15",
  "include_sections": ["income", "expenses", "debts", "insights"]
}

Response: 202 Accepted (Async)
{
  "job_id": "uuid",
  "status": "processing",
  "estimated_completion": "2026-04-15T12:00:00Z"
}
```

#### Get Report

```
GET /api/v1/reports/:report_id

Headers:
- Authorization: Bearer <jwt_token>

Response: 200 OK
{
  "id": "uuid",
  "status": "completed|processing|failed",
  "pdf_url": "https://s3.amazonaws.com/akowe-reports/...",
  "summary": {
    "total_income": 500000,
    "total_expenses": 200000,
    "net_profit": 300000,
    "debts_owed": 50000,
    "credit_score": 72
  },
  "generated_at": "2026-04-15T12:00:00Z"
}
```

#### Share Report with Bank

```
POST /api/v1/reports/:report_id/share

Headers:
- Authorization: Bearer <jwt_token>
- Content-Type: application/json

Request Body:
{
  "bank_code": "058",  // GTB
  "expiration_days": 30
}

Response: 201 Created
{
  "share_id": "uuid",
  "share_token": "secure_token",
  "bank": "Guaranty Trust Bank",
  "share_link": "https://akowe.ai/reports/share/secure_token",
  "expires_at": "2026-05-15T12:00:00Z"
}
```

### 4. User Endpoints

#### Register User

```
POST /api/v1/auth/register

Headers:
- Content-Type: application/json

Request Body:
{
  "phone_number": "+234XXXXXXXXXX",
  "business_name": "John's Trading",
  "preferred_dialect": "pidgin|yoruba|igbo|hausa|english",
  "business_type": "retail|food|transport|electronics"
}

Response: 201 Created
{
  "user_id": "uuid",
  "phone_number": "+234XXXXXXXXXX",
  "access_token": "jwt_token",
  "refresh_token": "refresh_token"
}
```

#### Get User Profile

```
GET /api/v1/users/me

Headers:
- Authorization: Bearer <jwt_token>

Response: 200 OK
{
  "id": "uuid",
  "phone_number": "+234XXXXXXXXXX",
  "business_name": "John's Trading",
  "preferred_dialect": "pidgin",
  "business_type": "retail",
  "account_created": "2026-04-01T10:00:00Z",
  "statistics": {
    "total_transactions": 145,
    "total_reported_income": 1500000,
    "credit_score": 72
  }
}
```

---

## Database Design

### PostgreSQL Schema

```sql
-- Users
CREATE TABLE users (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  phone_number VARCHAR(20) UNIQUE NOT NULL,
  business_name VARCHAR(255),
  preferred_dialect VARCHAR(50),
  business_type VARCHAR(100),
  password_hash VARCHAR(255),
  is_active BOOLEAN DEFAULT TRUE,
  created_at TIMESTAMP DEFAULT NOW(),
  updated_at TIMESTAMP DEFAULT NOW()
);

-- Transactions
CREATE TABLE transactions (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  amount DECIMAL(15, 2) NOT NULL,
  currency VARCHAR(3) DEFAULT 'NGN',
  category VARCHAR(50) NOT NULL, -- 'income', 'expense', 'debt'
  description TEXT,
  transaction_date DATE NOT NULL,
  counterparty VARCHAR(255),
  source VARCHAR(50), -- 'voice', 'image', 'text', 'manual'
  confidence FLOAT DEFAULT 1.0,
  metadata JSONB,
  is_deleted BOOLEAN DEFAULT FALSE,
  created_at TIMESTAMP DEFAULT NOW(),
  updated_at TIMESTAMP DEFAULT NOW(),
  CONSTRAINT amount_positive CHECK (amount > 0)
);

-- Receipt Images
CREATE TABLE receipt_images (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  transaction_id UUID REFERENCES transactions(id) ON DELETE SET NULL,
  s3_key VARCHAR(500) NOT NULL,
  extracted_data JSONB,
  extraction_status VARCHAR(50), -- 'pending', 'completed', 'failed'
  created_at TIMESTAMP DEFAULT NOW(),
  updated_at TIMESTAMP DEFAULT NOW()
);

-- Voice Messages
CREATE TABLE voice_messages (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  transaction_id UUID REFERENCES transactions(id) ON DELETE SET NULL,
  s3_audio_key VARCHAR(500) NOT NULL,
  transcription TEXT,
  dialect_detected VARCHAR(50),
  transcription_status VARCHAR(50), -- 'pending', 'completed', 'failed'
  created_at TIMESTAMP DEFAULT NOW()
);

-- Reports
CREATE TABLE reports (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  report_type VARCHAR(50), -- 'credit-ready', 'monthly', 'quarterly'
  period_start DATE NOT NULL,
  period_end DATE NOT NULL,
  pdf_s3_key VARCHAR(500),
  summary_data JSONB,
  status VARCHAR(50), -- 'pending', 'completed', 'failed'
  created_at TIMESTAMP DEFAULT NOW()
);

-- Report Shares
CREATE TABLE report_shares (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  report_id UUID NOT NULL REFERENCES reports(id) ON DELETE CASCADE,
  bank_code VARCHAR(10),
  share_token VARCHAR(255) UNIQUE NOT NULL,
  accessed_by_bank BOOLEAN DEFAULT FALSE,
  accessed_at TIMESTAMP,
  expires_at TIMESTAMP,
  created_at TIMESTAMP DEFAULT NOW()
);

-- AI Processing Jobs
CREATE TABLE ai_jobs (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID NOT NULL REFERENCES users(id),
  job_type VARCHAR(50), -- 'transcription', 'ocr', 'analysis'
  input_data JSONB,
  output_data JSONB,
  status VARCHAR(50) DEFAULT 'pending', -- 'pending', 'processing', 'completed', 'failed'
  error_message TEXT,
  created_at TIMESTAMP DEFAULT NOW(),
  completed_at TIMESTAMP
);

-- Indexes for performance
CREATE INDEX idx_transactions_user_created ON transactions(user_id, created_at DESC);
CREATE INDEX idx_transactions_category ON transactions(category);
CREATE INDEX idx_reports_user ON reports(user_id, created_at DESC);
CREATE INDEX idx_report_shares_token ON report_shares(share_token);
CREATE INDEX idx_ai_jobs_status ON ai_jobs(status, created_at);
```

---

## Message Queue System

### Celery Configuration

```python
# celery_app.py
from celery import Celery
import os

celery_app = Celery(
    'akowe',
    broker=os.getenv('CELERY_BROKER_URL', 'redis://localhost:6379/0'),
    backend=os.getenv('CELERY_RESULT_BACKEND', 'redis://localhost:6379/1')
)

celery_app.conf.update(
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    timezone='Africa/Lagos',
    enable_utc=True,
    task_track_started=True,
    task_time_limit=30 * 60,  # 30 minute hard limit
    task_soft_time_limit=25 * 60,  # 25 minute soft limit
)

@celery_app.task(bind=True, max_retries=3)
def process_voice_message(self, user_id, audio_s3_key, dialect):
    """Process voice message with retries"""
    try:
        from tasks.voice_processor import process_voice
        return process_voice(user_id, audio_s3_key, dialect)
    except Exception as exc:
        # Retry with exponential backoff
        raise self.retry(exc=exc, countdown=60 * (2 ** self.request.retries))

@celery_app.task(bind=True, max_retries=3)
def process_receipt_image(self, user_id, image_s3_key):
    """Process receipt image with retries"""
    try:
        from tasks.image_processor import process_image
        return process_image(user_id, image_s3_key)
    except Exception as exc:
        raise self.retry(exc=exc, countdown=60 * (2 ** self.request.retries))

@celery_app.task()
def generate_financial_report(user_id, report_type, start_date, end_date):
    """Generate financial report"""
    from tasks.report_generator import generate_report
    return generate_report(user_id, report_type, start_date, end_date)

@celery_app.task()
def send_whatsapp_message(phone_number, message_text):
    """Send WhatsApp message"""
    from integrations.whatsapp import send_message
    return send_message(phone_number, message_text)
```

### Task Handlers

```python
# tasks/voice_processor.py
from services.openai_service import transcribe_audio
from services.claude_service import extract_transaction_from_text

async def process_voice(user_id: str, audio_s3_key: str, dialect: str):
    """
    1. Download audio from S3
    2. Transcribe with Whisper
    3. Extract transaction with Claude
    4. Store in database
    """
    # Download audio
    audio_data = download_from_s3(audio_s3_key)

    # Transcribe
    transcription = transcribe_audio(audio_data, language=dialect)

    # Extract transaction
    transaction_data = extract_transaction_from_text(
        transcription,
        dialect=dialect,
        user_id=user_id
    )

    # Store in database
    db.create_transaction(user_id, transaction_data)

    # Notify user
    send_whatsapp_message(
        phone_number,
        f"✓ Transaction recorded: {transaction_data['amount']} {transaction_data['description']}"
    )
```

---

## Error Handling & Monitoring

### Global Exception Handler

```python
# exceptions.py
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
import logging

logger = logging.getLogger(__name__)

class AkoweException(Exception):
    def __init__(self, status_code: int, detail: str):
        self.status_code = status_code
        self.detail = detail

class TransactionProcessingError(AkoweException):
    pass

class WhatsAppIntegrationError(AkoweException):
    pass

class DatabaseError(AkoweException):
    pass

def setup_exception_handlers(app: FastAPI):
    @app.exception_handler(AkoweException)
    async def akowe_exception_handler(request: Request, exc: AkoweException):
        logger.error(f"AkoweException: {exc.detail}", extra={
            "path": str(request.url),
            "status_code": exc.status_code
        })
        return JSONResponse(
            status_code=exc.status_code,
            content={"detail": exc.detail, "request_id": request.headers.get("X-Request-ID")}
        )

    @app.exception_handler(Exception)
    async def general_exception_handler(request: Request, exc: Exception):
        logger.exception(f"Unhandled exception: {str(exc)}", extra={
            "path": str(request.url)
        })
        return JSONResponse(
            status_code=500,
            content={"detail": "Internal server error", "request_id": request.headers.get("X-Request-ID")}
        )
```

### Logging & Monitoring

```python
# monitoring.py
from prometheus_client import Counter, Histogram, Gauge
import time

# Metrics
api_requests = Counter(
    'api_requests_total',
    'Total API requests',
    ['method', 'endpoint', 'status']
)

request_duration = Histogram(
    'api_request_duration_seconds',
    'API request duration',
    ['method', 'endpoint']
)

transactions_processed = Counter(
    'transactions_processed_total',
    'Total transactions processed',
    ['source', 'status']  # source: voice, image, text
)

claude_api_calls = Counter(
    'claude_api_calls_total',
    'Total Claude API calls',
    ['operation']
)

active_users_gauge = Gauge(
    'active_users_count',
    'Number of active users'
)

# Middleware
from fastapi import Request

async def monitoring_middleware(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    duration = time.time() - start_time

    api_requests.labels(
        method=request.method,
        endpoint=request.url.path,
        status=response.status_code
    ).inc()

    request_duration.labels(
        method=request.method,
        endpoint=request.url.path
    ).observe(duration)

    return response
```

---

## Deployment

### Docker Setup

```dockerfile
# Dockerfile
FROM python:3.9-slim

WORKDIR /app

# System dependencies
RUN apt-get update && apt-get install -y \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Application code
COPY . .

# Create non-root user
RUN useradd -m appuser && chown -R appuser:appuser /app
USER appuser

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD python -c "import requests; requests.get('http://localhost:8000/health')"

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### Environment Variables

```bash
# .env.example
# Database
DATABASE_URL=postgresql://user:password@localhost:5432/akowe
SQLALCHEMY_ECHO=False

# Redis/Cache
REDIS_URL=redis://localhost:6379/0

# Celery
CELERY_BROKER_URL=redis://localhost:6379/1
CELERY_RESULT_BACKEND=redis://localhost:6379/1

# APIs
CLAUDE_API_KEY=sk-xxx
OPENAI_API_KEY=sk-xxx
WHATSAPP_ACCESS_TOKEN=xxx
WHATSAPP_PHONE_ID=xxx
WHATSAPP_BUSINESS_ACCOUNT_ID=xxx

# AWS/Storage
AWS_ACCESS_KEY_ID=xxx
AWS_SECRET_ACCESS_KEY=xxx
AWS_S3_BUCKET=akowe-production

# Security
JWT_SECRET=your-secret-key
JWT_ALGORITHM=HS256
JWT_EXPIRATION_HOURS=24

# App
DEBUG=False
ENVIRONMENT=production
LOG_LEVEL=INFO
```

### Health Check Endpoint

```python
# health.py
from fastapi import APIRouter
from sqlalchemy import text
from redis import Redis

router = APIRouter()

@router.get("/health")
async def health_check(db: Session = Depends(get_db)):
    """Check application health"""
    try:
        # Database
        db.execute(text("SELECT 1"))

        # Redis
        redis = Redis.from_url(os.getenv("REDIS_URL"))
        redis.ping()

        return {
            "status": "healthy",
            "timestamp": datetime.now(),
            "services": {
                "database": "ok",
                "cache": "ok"
            }
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "error": str(e)
        }, 503
```

---

## Development Best Practices

### 1. Code Structure

```
backend/
├── app/
│   ├── __init__.py
│   ├── main.py              # FastAPI app initialization
│   ├── config.py            # Configuration
│   ├── dependencies.py      # Dependency injection
│   ├── api/
│   │   ├── v1/
│   │   │   ├── endpoints/
│   │   │   │   ├── transactions.py
│   │   │   │   ├── reports.py
│   │   │   │   ├── users.py
│   │   │   │   └── webhooks.py
│   │   │   └── router.py
│   ├── services/
│   │   ├── claude_service.py
│   │   ├── whatsapp_service.py
│   │   ├── report_service.py
│   │   └── transaction_service.py
│   ├── models/
│   │   ├── database.py      # SQLAlchemy models
│   │   └── schemas.py       # Pydantic schemas
│   ├── db/
│   │   ├── database.py      # Database connection
│   │   └── crud.py          # Database operations
│   └── tasks/
│       ├── voice_processor.py
│       ├── image_processor.py
│       └── report_generator.py
├── tests/
│   ├── test_api.py
│   ├── test_services.py
│   └── conftest.py
├── migrations/              # Alembic migrations
├── requirements.txt
├── .env.example
└── docker-compose.yml
```

### 2. Testing

```python
# tests/conftest.py
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.models.database import Base

@pytest.fixture(scope="session")
def db_engine():
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    yield engine
    Base.metadata.drop_all(engine)

@pytest.fixture
def db_session(db_engine):
    TestingSessionLocal = sessionmaker(bind=db_engine)
    session = TestingSessionLocal()
    yield session
    session.close()

@pytest.fixture
def client(db_session):
    def override_get_db():
        yield db_session

    from fastapi.testclient import TestClient
    from app.main import app

    app.dependency_overrides[get_db] = override_get_db
    return TestClient(app)
```

---

## Troubleshooting

| Issue                           | Solution                                                |
| ------------------------------- | ------------------------------------------------------- |
| Messages not processing         | Check Redis connection, verify Celery worker running    |
| Claude API errors               | Verify API key, check rate limits, review prompt format |
| WhatsApp webhook not triggering | Verify webhook URL, check Access Token, review logs     |
| Database migrations failing     | Check migrations folder, ensure database is running     |
| Memory leaks in production      | Review Celery task cleanup, check S3 file handles       |

This guide should provide backend engineers everything needed to develop, deploy, and maintain the AkoweAI backend infrastructure.
