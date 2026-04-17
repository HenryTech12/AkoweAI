"""Transaction endpoints."""
from fastapi import APIRouter, Depends, status, Query
from sqlalchemy.orm import Session
from uuid import UUID
from model.database import get_db
from db.crud import (
    create_transaction, get_transaction, get_user_transactions,
    update_transaction, delete_transaction
)
from schema.schema import (
    TransactionCreate, TransactionUpdate, TransactionResponse, TransactionListResponse
)
from exceptions import ResourceNotFoundError, ValidationError
from dependencies import get_current_user
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/transactions", tags=["transactions"])


@router.post(
    "",
    response_model=TransactionResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new transaction"
)
async def create_transaction_endpoint(
    transaction: TransactionCreate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Create a new transaction."""
    try:
        db_transaction = create_transaction(db, current_user.id, transaction)
        logger.info(f"Transaction created: {db_transaction.id}")
        return db_transaction
    except Exception as e:
        logger.error(f"Error creating transaction: {str(e)}")
        raise ValidationError(f"Failed to create transaction: {str(e)}")


@router.get(
    "",
    response_model=TransactionListResponse,
    summary="List user transactions"
)
async def list_transactions(
    start_date: str = Query(None, description="ISO format date"),
    end_date: str = Query(None, description="ISO format date"),
    category: str = Query(None, description="Filter by category"),
    limit: int = Query(50, le=100),
    offset: int = Query(0),
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """List transactions with filtering."""
    try:
        from datetime import datetime

        start_dt = datetime.fromisoformat(start_date) if start_date else None
        end_dt = datetime.fromisoformat(end_date) if end_date else None

        transactions, total = get_user_transactions(
            db,
            current_user.id,
            start_date=start_dt,
            end_date=end_dt,
            category=category,
            limit=limit,
            offset=offset
        )

        return TransactionListResponse(
            total=total,
            limit=limit,
            offset=offset,
            transactions=transactions
        )
    except Exception as e:
        logger.error(f"Error listing transactions: {str(e)}")
        raise ValidationError(f"Failed to list transactions: {str(e)}")


@router.get(
    "/{transaction_id}",
    response_model=TransactionResponse,
    summary="Get transaction details"
)
async def get_transaction_endpoint(
    transaction_id: UUID,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Get transaction by ID."""
    transaction = get_transaction(db, transaction_id, current_user.id)
    if not transaction:
        raise ResourceNotFoundError("Transaction not found")
    return transaction


@router.put(
    "/{transaction_id}",
    response_model=TransactionResponse,
    summary="Update transaction"
)
async def update_transaction_endpoint(
    transaction_id: UUID,
    transaction_data: TransactionUpdate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Update a transaction."""
    try:
        # Verify transaction exists
        transaction = get_transaction(db, transaction_id, current_user.id)
        if not transaction:
            raise ResourceNotFoundError("Transaction not found")

        # Update transaction
        updated = update_transaction(db, transaction_id, current_user.id, transaction_data)
        logger.info(f"Transaction updated: {transaction_id}")
        return updated

    except Exception as e:
        logger.error(f"Error updating transaction: {str(e)}")
        raise ValidationError(f"Failed to update transaction: {str(e)}")


@router.delete(
    "/{transaction_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete transaction"
)
async def delete_transaction_endpoint(
    transaction_id: UUID,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Delete a transaction (soft delete)."""
    try:
        # Verify transaction exists
        transaction = get_transaction(db, transaction_id, current_user.id)
        if not transaction:
            raise ResourceNotFoundError("Transaction not found")

        # Delete transaction
        success = delete_transaction(db, transaction_id, current_user.id)
        if success:
            logger.info(f"Transaction deleted: {transaction_id}")
        else:
            raise ValidationError("Failed to delete transaction")

    except ResourceNotFoundError:
        raise
    except Exception as e:
        logger.error(f"Error deleting transaction: {str(e)}")
        raise ValidationError(f"Failed to delete transaction: {str(e)}")
