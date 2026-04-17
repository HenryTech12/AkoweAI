"""Pydantic schemas for AkoweAI API."""
from pydantic import BaseModel, Field, validator
from datetime import datetime
from typing import Optional, List
from uuid import UUID


# User Schemas
class UserCreate(BaseModel):
    """Schema for user registration."""
    phone_number: str = Field(..., description="Phone number with country code")
    business_name: str
    preferred_dialect: str = Field("english", description="pidgin, yoruba, igbo, hausa, or english")
    business_type: str


class UserResponse(BaseModel):
    """Schema for user response."""
    id: UUID
    phone_number: str
    business_name: str
    preferred_dialect: str
    business_type: str
    is_active: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class UserProfile(BaseModel):
    """Extended user profile with statistics."""
    id: UUID
    phone_number: str
    business_name: str
    preferred_dialect: str
    business_type: str
    account_created: datetime
    statistics: dict = Field(default_factory=dict)

    class Config:
        from_attributes = True


# Transaction Schemas
class TransactionItemBase(BaseModel):
    """Base schema for transaction items."""
    name: str
    quantity: float
    unit_price: float


class TransactionCreate(BaseModel):
    """Schema for creating a transaction."""
    amount: float = Field(..., gt=0)
    currency: str = Field("NGN")
    category: str = Field(..., description="expense, income, or debt")
    description: str
    transaction_date: datetime
    counterparty: Optional[str] = None
    items: Optional[List[TransactionItemBase]] = None

    @validator("category")
    def validate_category(cls, v):
        if v not in ["income", "expense", "debt"]:
            raise ValueError("category must be income, expense, or debt")
        return v


class TransactionUpdate(BaseModel):
    """Schema for updating a transaction."""
    amount: Optional[float] = None
    category: Optional[str] = None
    description: Optional[str] = None
    transaction_date: Optional[datetime] = None
    counterparty: Optional[str] = None


class TransactionResponse(BaseModel):
    """Schema for transaction response."""
    id: UUID
    user_id: UUID
    amount: float
    currency: str
    category: str
    description: str
    transaction_date: datetime
    counterparty: Optional[str]
    source: str
    confidence: float
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class TransactionListResponse(BaseModel):
    """Schema for transaction list response."""
    total: int
    limit: int
    offset: int
    transactions: List[TransactionResponse]


# Receipt Image Schemas
class ReceiptImageCreate(BaseModel):
    """Schema for uploading a receipt image."""
    s3_key: str


class ReceiptImageResponse(BaseModel):
    """Schema for receipt image response."""
    id: UUID
    user_id: UUID
    s3_key: str
    extracted_data: Optional[dict]
    extraction_status: str
    created_at: datetime

    class Config:
        from_attributes = True


# Voice Message Schemas
class VoiceMessageCreate(BaseModel):
    """Schema for uploading a voice message."""
    s3_audio_key: str
    dialect: Optional[str] = "english"


class VoiceMessageResponse(BaseModel):
    """Schema for voice message response."""
    id: UUID
    user_id: UUID
    s3_audio_key: str
    transcription: Optional[str]
    dialect_detected: Optional[str]
    transcription_status: str
    created_at: datetime

    class Config:
        from_attributes = True


# Report Schemas
class ReportGenerateRequest(BaseModel):
    """Schema for generating a report."""
    report_type: str = Field(..., description="credit-ready, monthly, quarterly, or custom")
    start_date: datetime
    end_date: datetime
    include_sections: Optional[List[str]] = Field(
        default=["income", "expenses", "debts", "insights"]
    )


class ReportSummary(BaseModel):
    """Schema for report summary."""
    total_income: float
    total_expenses: float
    net_profit: float
    debts_owed: float
    credit_score: int


class ReportResponse(BaseModel):
    """Schema for report response."""
    id: UUID
    user_id: UUID
    report_type: str
    period_start: datetime
    period_end: datetime
    status: str
    pdf_s3_key: Optional[str]
    summary_data: Optional[ReportSummary]
    created_at: datetime

    class Config:
        from_attributes = True


class ReportShareRequest(BaseModel):
    """Schema for sharing a report with a bank."""
    bank_code: str
    expiration_days: int = 30


class ReportShareResponse(BaseModel):
    """Schema for report share response."""
    share_id: UUID
    share_token: str
    bank: str
    share_link: str
    expires_at: datetime

    class Config:
        from_attributes = True


# AI Job Schemas
class AIJobCreate(BaseModel):
    """Schema for creating an AI job."""
    job_type: str = Field(..., description="transcription, ocr, or analysis")
    input_data: dict


class AIJobResponse(BaseModel):
    """Schema for AI job response."""
    id: UUID
    user_id: UUID
    job_type: str
    status: str
    created_at: datetime
    completed_at: Optional[datetime]
    output_data: Optional[dict]
    error_message: Optional[str]

    class Config:
        from_attributes = True


# WhatsApp Schemas
class WhatsAppMessage(BaseModel):
    """Schema for WhatsApp message content."""
    body: Optional[str] = None


class WhatsAppAudio(BaseModel):
    """Schema for WhatsApp audio content."""
    id: str
    mime_type: str


class WhatsAppImage(BaseModel):
    """Schema for WhatsApp image content."""
    id: str
    mime_type: str


class WhatsAppDocument(BaseModel):
    """Schema for WhatsApp document content."""
    id: str
    mime_type: str


class WhatsAppMessageItem(BaseModel):
    """Schema for individual WhatsApp message."""
    id: str
    from_: str = Field(..., alias="from")
    timestamp: str
    type: str  # text, audio, image, document
    text: Optional[WhatsAppMessage] = None
    audio: Optional[WhatsAppAudio] = None
    image: Optional[WhatsAppImage] = None
    document: Optional[WhatsAppDocument] = None

    class Config:
        populate_by_name = True


class WhatsAppValue(BaseModel):
    """Schema for WhatsApp webhook value."""
    messaging_product: str
    messages: List[WhatsAppMessageItem]


class WhatsAppChange(BaseModel):
    """Schema for WhatsApp webhook change."""
    value: WhatsAppValue


class WhatsAppEntry(BaseModel):
    """Schema for WhatsApp webhook entry."""
    id: str
    changes: List[WhatsAppChange]


class WhatsAppWebhook(BaseModel):
    """Schema for WhatsApp webhook."""
    object: str
    entry: List[WhatsAppEntry]


# Authentication Schemas
class TokenResponse(BaseModel):
    """Schema for token response."""
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class TokenData(BaseModel):
    """Schema for token data."""
    user_id: Optional[UUID] = None
    phone_number: Optional[str] = None


# Error Schemas
class ErrorResponse(BaseModel):
    """Schema for error responses."""
    detail: str
    request_id: Optional[str] = None


class HealthResponse(BaseModel):
    """Schema for health check response."""
    status: str
    timestamp: datetime
    services: dict
