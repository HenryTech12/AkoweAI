"""CRUD operations for database models."""
from sqlalchemy.orm import Session
from sqlalchemy import and_
from model.database import User, Transaction, Report, ReportShare, ReceiptImage, VoiceMessage, AIJob, RegistrationSession
from schema.schema import (
    UserCreate, TransactionCreate, TransactionUpdate, ReportGenerateRequest
)
from datetime import datetime, timedelta
from uuid import UUID
import logging

logger = logging.getLogger(__name__)


# User CRUD
def create_user(db: Session, user_data: UserCreate) -> User:
    """Create a new user."""
    user = User(**user_data.model_dump())
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def get_user(db: Session, user_id: UUID) -> User:
    """Get user by ID."""
    return db.query(User).filter(User.id == user_id).first()


def get_user_by_phone(db: Session, phone_number: str) -> User:
    """Get user by phone number."""
    return db.query(User).filter(User.phone_number == phone_number).first()


def update_user(db: Session, user_id: UUID, user_data: dict) -> User:
    """Update user information."""
    user = db.query(User).filter(User.id == user_id).first()
    if user:
        for key, value in user_data.items():
            setattr(user, key, value)
        user.updated_at = datetime.utcnow()
        db.commit()
        db.refresh(user)
    return user


# Transaction CRUD
def create_transaction(db: Session, user_id: UUID, transaction_data: TransactionCreate) -> Transaction:
    """Create a new transaction."""
    transaction = Transaction(
        user_id=user_id,
        **transaction_data.model_dump(exclude={"items"})
    )
    db.add(transaction)
    db.commit()
    db.refresh(transaction)
    return transaction


def get_transaction(db: Session, transaction_id: UUID, user_id: UUID) -> Transaction:
    """Get transaction by ID."""
    return db.query(Transaction).filter(
        and_(
            Transaction.id == transaction_id,
            Transaction.user_id == user_id,
            Transaction.is_deleted == False
        )
    ).first()


def get_user_transactions(
    db: Session,
    user_id: UUID,
    start_date: datetime = None,
    end_date: datetime = None,
    category: str = None,
    limit: int = 50,
    offset: int = 0
) -> tuple:
    """Get user transactions with filtering."""
    query = db.query(Transaction).filter(
        Transaction.user_id == user_id,
        Transaction.is_deleted == False
    )

    if start_date:
        query = query.filter(Transaction.transaction_date >= start_date)

    if end_date:
        query = query.filter(Transaction.transaction_date <= end_date)

    if category:
        query = query.filter(Transaction.category == category)

    total = query.count()
    transactions = query.order_by(Transaction.created_at.desc()).offset(offset).limit(limit).all()

    return transactions, total


def update_transaction(
    db: Session,
    transaction_id: UUID,
    user_id: UUID,
    transaction_data: TransactionUpdate
) -> Transaction:
    """Update a transaction."""
    transaction = db.query(Transaction).filter(
        and_(
            Transaction.id == transaction_id,
            Transaction.user_id == user_id
        )
    ).first()

    if transaction:
        update_data = transaction_data.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(transaction, key, value)
        transaction.updated_at = datetime.utcnow()
        db.commit()
        db.refresh(transaction)

    return transaction


def delete_transaction(db: Session, transaction_id: UUID, user_id: UUID) -> bool:
    """Soft delete a transaction."""
    transaction = db.query(Transaction).filter(
        and_(
            Transaction.id == transaction_id,
            Transaction.user_id == user_id
        )
    ).first()

    if transaction:
        transaction.is_deleted = True
        db.commit()
        return True
    return False


def get_transaction_statistics(db: Session, user_id: UUID, period_days: int = 30):
    """Get transaction statistics for a user."""
    cutoff_date = datetime.utcnow() - timedelta(days=period_days)

    transactions = db.query(Transaction).filter(
        and_(
            Transaction.user_id == user_id,
            Transaction.created_at >= cutoff_date,
            Transaction.is_deleted == False
        )
    ).all()

    stats = {
        "total_transactions": len(transactions),
        "total_income": 0,
        "total_expenses": 0,
        "total_debts": 0,
    }

    for trans in transactions:
        if trans.category == "income":
            stats["total_income"] += float(trans.amount)
        elif trans.category == "expense":
            stats["total_expenses"] += float(trans.amount)
        elif trans.category == "debt":
            stats["total_debts"] += float(trans.amount)

    stats["net_profit"] = stats["total_income"] - stats["total_expenses"]

    return stats


# Report CRUD
def create_report(db: Session, user_id: UUID, report_data: ReportGenerateRequest) -> Report:
    """Create a new report."""
    report = Report(
        user_id=user_id,
        report_type=report_data.report_type,
        period_start=report_data.start_date,
        period_end=report_data.end_date,
        status="pending"
    )
    db.add(report)
    db.commit()
    db.refresh(report)
    return report


def get_report(db: Session, report_id: UUID, user_id: UUID) -> Report:
    """Get report by ID."""
    return db.query(Report).filter(
        and_(
            Report.id == report_id,
            Report.user_id == user_id
        )
    ).first()


def get_user_reports(db: Session, user_id: UUID, limit: int = 50, offset: int = 0) -> tuple:
    """Get user reports."""
    query = db.query(Report).filter(Report.user_id == user_id)
    total = query.count()
    reports = query.order_by(Report.created_at.desc()).offset(offset).limit(limit).all()
    return reports, total


def update_report(db: Session, report_id: UUID, report_data: dict) -> Report:
    """Update a report."""
    report = db.query(Report).filter(Report.id == report_id).first()
    if report:
        for key, value in report_data.items():
            setattr(report, key, value)
        report.updated_at = datetime.utcnow()
        db.commit()
        db.refresh(report)
    return report


# Report Share CRUD
def create_report_share(db: Session, report_id: UUID, bank_code: str, share_token: str, expires_at: datetime) -> ReportShare:
    """Create a report share."""
    share = ReportShare(
        report_id=report_id,
        bank_code=bank_code,
        share_token=share_token,
        expires_at=expires_at
    )
    db.add(share)
    db.commit()
    db.refresh(share)
    return share


def get_report_share_by_token(db: Session, share_token: str) -> ReportShare:
    """Get report share by token."""
    return db.query(ReportShare).filter(ReportShare.share_token == share_token).first()


def mark_share_accessed(db: Session, share_id: UUID) -> ReportShare:
    """Mark a share as accessed by bank."""
    share = db.query(ReportShare).filter(ReportShare.id == share_id).first()
    if share:
        share.accessed_by_bank = True
        share.accessed_at = datetime.utcnow()
        db.commit()
        db.refresh(share)
    return share


# Receipt Image CRUD
def create_receipt_image(db: Session, user_id: UUID, s3_key: str) -> ReceiptImage:
    """Create receipt image record."""
    receipt = ReceiptImage(
        user_id=user_id,
        s3_key=s3_key,
        extraction_status="pending"
    )
    db.add(receipt)
    db.commit()
    db.refresh(receipt)
    return receipt


def get_receipt_image(db: Session, receipt_id: UUID, user_id: UUID) -> ReceiptImage:
    """Get receipt image by ID."""
    return db.query(ReceiptImage).filter(
        and_(
            ReceiptImage.id == receipt_id,
            ReceiptImage.user_id == user_id
        )
    ).first()


def update_receipt_extraction(db: Session, receipt_id: UUID, extracted_data: dict, status: str) -> ReceiptImage:
    """Update receipt extraction status."""
    receipt = db.query(ReceiptImage).filter(ReceiptImage.id == receipt_id).first()
    if receipt:
        receipt.extracted_data = extracted_data
        receipt.extraction_status = status
        db.commit()
        db.refresh(receipt)
    return receipt


# Voice Message CRUD
def create_voice_message(db: Session, user_id: UUID, s3_audio_key: str, dialect: str) -> VoiceMessage:
    """Create voice message record."""
    voice = VoiceMessage(
        user_id=user_id,
        s3_audio_key=s3_audio_key,
        dialect_detected=dialect,
        transcription_status="pending"
    )
    db.add(voice)
    db.commit()
    db.refresh(voice)
    return voice


def get_voice_message(db: Session, voice_id: UUID, user_id: UUID) -> VoiceMessage:
    """Get voice message by ID."""
    return db.query(VoiceMessage).filter(
        and_(
            VoiceMessage.id == voice_id,
            VoiceMessage.user_id == user_id
        )
    ).first()


def update_voice_transcription(db: Session, voice_id: UUID, transcription: str, status: str) -> VoiceMessage:
    """Update voice transcription."""
    voice = db.query(VoiceMessage).filter(VoiceMessage.id == voice_id).first()
    if voice:
        voice.transcription = transcription
        voice.transcription_status = status
        db.commit()
        db.refresh(voice)
    return voice


# AI Job CRUD
def create_ai_job(db: Session, user_id: UUID, job_type: str, input_data: dict) -> AIJob:
    """Create AI job."""
    job = AIJob(
        user_id=user_id,
        job_type=job_type,
        input_data=input_data,
        status="pending"
    )
    db.add(job)
    db.commit()
    db.refresh(job)
    return job


def get_ai_job(db: Session, job_id: UUID) -> AIJob:
    """Get AI job by ID."""
    return db.query(AIJob).filter(AIJob.id == job_id).first()


def update_ai_job(db: Session, job_id: UUID, update_data: dict) -> AIJob:
    """Update AI job."""
    job = db.query(AIJob).filter(AIJob.id == job_id).first()
    if job:
        for key, value in update_data.items():
            setattr(job, key, value)
        if update_data.get("status") == "completed":
            job.completed_at = datetime.utcnow()
        db.commit()
        db.refresh(job)
    return job


# Registration Session CRUD
def get_registration_session(db: Session, phone_number: str) -> RegistrationSession:
    """Get active registration session for phone."""
    return db.query(RegistrationSession).filter(
        and_(
            RegistrationSession.phone_number == phone_number,
            RegistrationSession.step != "completed"
        )
    ).first()


def create_registration_session(db: Session, phone_number: str) -> RegistrationSession:
    """Create new registration session."""
    from datetime import timedelta
    
    session = RegistrationSession(
        phone_number=phone_number,
        step="awaiting_business_name",
        expires_at=datetime.utcnow() + timedelta(hours=24)
    )
    db.add(session)
    db.commit()
    db.refresh(session)
    return session


def update_registration_session(db: Session, phone_number: str, update_data: dict) -> RegistrationSession:
    """Update registration session."""
    session = db.query(RegistrationSession).filter(
        RegistrationSession.phone_number == phone_number
    ).first()
    
    if session:
        for key, value in update_data.items():
            setattr(session, key, value)
        session.updated_at = datetime.utcnow()
        db.commit()
        db.refresh(session)
    
    return session


def delete_registration_session(db: Session, phone_number: str) -> bool:
    """Delete registration session."""
    session = db.query(RegistrationSession).filter(
        RegistrationSession.phone_number == phone_number
    ).first()
    
    if session:
        db.delete(session)
        db.commit()
        return True
    return False
