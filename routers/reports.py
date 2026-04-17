"""Report endpoints."""
from fastapi import APIRouter, Depends, status, Query
from sqlalchemy.orm import Session
from uuid import UUID
import uuid
import secrets
from datetime import datetime, timedelta

from model.database import get_db
from db.crud import (
    create_report, get_report, get_user_reports,
    create_report_share, get_report_share_by_token, mark_share_accessed
)
from schema.schema import (
    ReportGenerateRequest, ReportResponse, ReportShareRequest, ReportShareResponse
)
from dependencies import get_current_user
from exceptions import ResourceNotFoundError, ValidationError
from celery_app import generate_financial_report_task
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/reports", tags=["reports"])


@router.post(
    "/generate",
    response_model=dict,
    status_code=status.HTTP_202_ACCEPTED,
    summary="Generate financial report"
)
async def generate_report(
    report_request: ReportGenerateRequest,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """
    Generate a financial report (async operation).

    Returns a job_id for tracking progress.
    """
    try:
        # Create report record in database
        report = create_report(db, current_user.id, report_request)

        # Queue async task
        task = generate_financial_report_task.delay(
            str(current_user.id),
            report_request.report_type,
            report_request.start_date.isoformat(),
            report_request.end_date.isoformat()
        )

        logger.info(f"Report generation started: {report.id}, task: {task.id}")

        return {
            "job_id": str(task.id),
            "report_id": str(report.id),
            "status": "processing",
            "estimated_completion": (datetime.utcnow() + timedelta(minutes=5)).isoformat()
        }

    except Exception as e:
        logger.error(f"Error generating report: {str(e)}")
        raise ValidationError(f"Failed to generate report: {str(e)}")


@router.get(
    "/{report_id}",
    response_model=ReportResponse,
    summary="Get report details"
)
async def get_report_endpoint(
    report_id: UUID,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Get report by ID."""
    report = get_report(db, report_id, current_user.id)
    if not report:
        raise ResourceNotFoundError("Report not found")
    return report


@router.get(
    "",
    response_model=dict,
    summary="List user reports"
)
async def list_reports(
    limit: int = Query(50, le=100),
    offset: int = Query(0),
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """List all reports for the user."""
    try:
        reports, total = get_user_reports(db, current_user.id, limit=limit, offset=offset)

        return {
            "total": total,
            "limit": limit,
            "offset": offset,
            "reports": reports
        }
    except Exception as e:
        logger.error(f"Error listing reports: {str(e)}")
        raise ValidationError(f"Failed to list reports: {str(e)}")


@router.post(
    "/{report_id}/share",
    response_model=ReportShareResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Share report with bank"
)
async def share_report(
    report_id: UUID,
    share_request: ReportShareRequest,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """
    Create a share link for a report.

    Banks can access the report using the share_token.
    """
    try:
        # Verify report exists
        report = get_report(db, report_id, current_user.id)
        if not report:
            raise ResourceNotFoundError("Report not found")

        # Generate secure share token
        share_token = secrets.token_urlsafe(32)
        expires_at = datetime.utcnow() + timedelta(days=share_request.expiration_days)

        # Create share record
        share = create_report_share(
            db,
            report_id,
            share_request.bank_code,
            share_token,
            expires_at
        )

        # Get bank name from code (simplified - in production use a lookup)
        bank_names = {
            "058": "Guaranty Trust Bank",
            "007": "Zenith Bank",
            "003": "First Bank",
            "011": "First City Monument Bank"
        }
        bank_name = bank_names.get(share_request.bank_code, "Bank")

        logger.info(f"Report shared with bank: {report_id}, share: {share.id}")

        return ReportShareResponse(
            share_id=share.id,
            share_token=share_token,
            bank=bank_name,
            share_link=f"https://akowe.ai/reports/share/{share_token}",
            expires_at=expires_at
        )

    except ResourceNotFoundError:
        raise
    except Exception as e:
        logger.error(f"Error sharing report: {str(e)}")
        raise ValidationError(f"Failed to share report: {str(e)}")


@router.get(
    "/share/{share_token}",
    response_model=ReportResponse,
    summary="Access shared report"
)
async def get_shared_report(
    share_token: str,
    db: Session = Depends(get_db)
):
    """
    Get a shared report using the share token.

    No authentication required - token acts as access control.
    """
    try:
        # Get share record
        share = get_report_share_by_token(db, share_token)
        if not share:
            raise ResourceNotFoundError("Invalid or expired share token")

        # Check expiration
        if share.expires_at < datetime.utcnow():
            raise ValidationError("Share token has expired")

        # Mark as accessed
        mark_share_accessed(db, share.id)

        logger.info(f"Shared report accessed: {share.report_id}")

        return share.report

    except (ResourceNotFoundError, ValidationError):
        raise
    except Exception as e:
        logger.error(f"Error accessing shared report: {str(e)}")
        raise ValidationError(f"Failed to access report: {str(e)}")
