"""SQLAlchemy database models for AkoweAI."""
from sqlalchemy import (
    Column, String, Integer, Float, Boolean, DateTime, Text, DECIMAL, ForeignKey, Index, JSON
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid

Base = declarative_base()


class User(Base):
    """User model for business owners."""

    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    phone_number = Column(String(20), unique=True, nullable=False, index=True)
    business_name = Column(String(255))
    preferred_dialect = Column(String(50), default="english")  # pidgin, yoruba, igbo, hausa, english
    business_type = Column(String(100))
    password_hash = Column(String(255))
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    transactions = relationship("Transaction", back_populates="user", cascade="all, delete-orphan")
    receipt_images = relationship("ReceiptImage", back_populates="user", cascade="all, delete-orphan")
    voice_messages = relationship("VoiceMessage", back_populates="user", cascade="all, delete-orphan")
    reports = relationship("Report", back_populates="user", cascade="all, delete-orphan")
    ai_jobs = relationship("AIJob", back_populates="user", cascade="all, delete-orphan")

    __table_args__ = (
        Index("idx_users_created", "created_at"),
    )


class Transaction(Base):
    """Transaction model for tracking income, expenses, and debts."""

    __tablename__ = "transactions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    amount = Column(DECIMAL(15, 2), nullable=False)
    currency = Column(String(3), default="NGN")
    category = Column(String(50), nullable=False)  # income, expense, debt
    description = Column(Text)
    transaction_date = Column(DateTime, nullable=False)
    counterparty = Column(String(255))
    source = Column(String(50), default="manual")  # voice, image, text, manual
    confidence = Column(Float, default=1.0)
    meta = Column(JSON)
    is_deleted = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    user = relationship("User", back_populates="transactions")

    __table_args__ = (
        Index("idx_transactions_user_created", "user_id", "created_at"),
        Index("idx_transactions_category", "category"),
    )


class ReceiptImage(Base):
    """Receipt image model for OCR processing."""

    __tablename__ = "receipt_images"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    transaction_id = Column(UUID(as_uuid=True), ForeignKey("transactions.id", ondelete="SET NULL"))
    s3_key = Column(String(500), nullable=False)
    extracted_data = Column(JSON)
    extraction_status = Column(String(50), default="pending")  # pending, completed, failed
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    user = relationship("User", back_populates="receipt_images")
    transaction = relationship("Transaction", foreign_keys=[transaction_id])


class VoiceMessage(Base):
    """Voice message model for audio transcription."""

    __tablename__ = "voice_messages"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    transaction_id = Column(UUID(as_uuid=True), ForeignKey("transactions.id", ondelete="SET NULL"))
    s3_audio_key = Column(String(500), nullable=False)
    transcription = Column(Text)
    dialect_detected = Column(String(50))
    transcription_status = Column(String(50), default="pending")  # pending, completed, failed
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    user = relationship("User", back_populates="voice_messages")
    transaction = relationship("Transaction", foreign_keys=[transaction_id])


class Report(Base):
    """Financial report model."""

    __tablename__ = "reports"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    report_type = Column(String(50), nullable=False)  # credit-ready, monthly, quarterly, custom
    period_start = Column(DateTime, nullable=False)
    period_end = Column(DateTime, nullable=False)
    pdf_s3_key = Column(String(500))
    summary_data = Column(JSON)
    status = Column(String(50), default="pending")  # pending, completed, failed
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    user = relationship("User", back_populates="reports")
    shares = relationship("ReportShare", back_populates="report", cascade="all, delete-orphan")

    __table_args__ = (
        Index("idx_reports_user", "user_id", "created_at"),
    )


class ReportShare(Base):
    """Shared report tracking for banks."""

    __tablename__ = "report_shares"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    report_id = Column(UUID(as_uuid=True), ForeignKey("reports.id", ondelete="CASCADE"), nullable=False)
    bank_code = Column(String(10))
    share_token = Column(String(255), unique=True, nullable=False)
    accessed_by_bank = Column(Boolean, default=False)
    accessed_at = Column(DateTime)
    expires_at = Column(DateTime, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    report = relationship("Report", back_populates="shares")

    __table_args__ = (
        Index("idx_report_shares_token", "share_token"),
    )


class AIJob(Base):
    """AI processing jobs for async tasks."""

    __tablename__ = "ai_jobs"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    job_type = Column(String(50), nullable=False)  # transcription, ocr, analysis
    input_data = Column(JSON)
    output_data = Column(JSON)
    status = Column(String(50), default="pending")  # pending, processing, completed, failed
    error_message = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    completed_at = Column(DateTime)

    # Relationships
    user = relationship("User", back_populates="ai_jobs")

    __table_args__ = (
        Index("idx_ai_jobs_status", "status", "created_at"),
    )


class RegistrationSession(Base):
    """Track multi-step WhatsApp registration conversations."""

    __tablename__ = "registration_sessions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    phone_number = Column(String(20), unique=True, nullable=False, index=True)
    
    # Registration progress
    step = Column(String(50), default="awaiting_business_name")  # awaiting_business_name, awaiting_dialect, awaiting_business_type, completed
    
    # Collected data
    business_name = Column(String(255))
    preferred_dialect = Column(String(50))
    business_type = Column(String(100))
    
    # Session tracking
    conversation_state = Column(JSON)  # Store full context
    started_at = Column(DateTime, default=datetime.utcnow)
    expires_at = Column(DateTime)  # Session expires after 24 hours
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    __table_args__ = (
        Index("idx_registration_sessions_phone", "phone_number"),
        Index("idx_registration_sessions_step", "step", "updated_at"),
    )
