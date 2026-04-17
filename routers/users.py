"""User and authentication endpoints."""
from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from model.database import get_db
from db.crud import create_user, get_user, get_user_by_phone, get_transaction_statistics
from schema.schema import UserCreate, UserResponse, UserProfile, TokenResponse
from exceptions import ValidationError, AuthenticationError, ResourceNotFoundError
from dependencies import get_current_user, create_access_token, create_refresh_token
from config import settings
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post(
    "/register",
    response_model=TokenResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Register a new user"
)
async def register(
    user_data: UserCreate,
    db: Session = Depends(get_db)
):
    """
    Register a new user.

    Returns access and refresh tokens.
    """
    try:
        # Check if user already exists
        existing_user = get_user_by_phone(db, user_data.phone_number)
        if existing_user:
            raise ValidationError("Phone number already registered")

        # Create user
        user = create_user(db, user_data)

        # Generate tokens
        access_token = create_access_token(str(user.id))
        refresh_token = create_refresh_token(str(user.id))

        logger.info(f"User registered: {user.id}")

        return TokenResponse(
            access_token=access_token,
            refresh_token=refresh_token
        )

    except ValidationError:
        raise
    except Exception as e:
        logger.error(f"Error registering user: {str(e)}")
        raise ValidationError(f"Registration failed: {str(e)}")


@router.post(
    "/login",
    response_model=TokenResponse,
    summary="Login user"
)
async def login(
    phone_number: str,
    db: Session = Depends(get_db)
):
    """
    Simplified login - returns tokens for user.

    In production, add password authentication.
    """
    try:
        # Get user by phone
        user = get_user_by_phone(db, phone_number)
        if not user:
            raise AuthenticationError("User not found")

        # Generate tokens
        access_token = create_access_token(str(user.id))
        refresh_token = create_refresh_token(str(user.id))

        logger.info(f"User logged in: {user.id}")

        return TokenResponse(
            access_token=access_token,
            refresh_token=refresh_token
        )

    except AuthenticationError:
        raise
    except Exception as e:
        logger.error(f"Error during login: {str(e)}")
        raise AuthenticationError(f"Login failed: {str(e)}")


users_router = APIRouter(prefix="/users", tags=["users"])


@users_router.get(
    "/me",
    response_model=UserProfile,
    summary="Get current user profile"
)
async def get_current_user_profile(
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Get the current authenticated user's profile."""
    try:
        # Get fresh user data
        user = get_user(db, current_user.id)
        if not user:
            raise ResourceNotFoundError("User not found")

        # Get statistics
        stats = get_transaction_statistics(db, current_user.id)

        return UserProfile(
            id=user.id,
            phone_number=user.phone_number,
            business_name=user.business_name,
            preferred_dialect=user.preferred_dialect,
            business_type=user.business_type,
            account_created=user.created_at,
            statistics=stats
        )

    except ResourceNotFoundError:
        raise
    except Exception as e:
        logger.error(f"Error fetching user profile: {str(e)}")
        raise ValidationError(f"Failed to fetch profile: {str(e)}")


@users_router.get(
    "/{user_id}",
    response_model=UserResponse,
    summary="Get user information"
)
async def get_user_info(
    user_id: str,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """
    Get user information.

    Users can only access their own information.
    """
    from uuid import UUID

    # Convert to UUID
    try:
        target_user_id = UUID(user_id)
    except ValueError:
        raise ValidationError("Invalid user ID format")

    # Check authorization
    if target_user_id != current_user.id:
        from exceptions import AuthorizationError
        raise AuthorizationError("Cannot access other user's information")

    # Get user
    user = get_user(db, target_user_id)
    if not user:
        raise ResourceNotFoundError("User not found")

    return user


@users_router.put(
    "/me",
    response_model=UserResponse,
    summary="Update user profile"
)
async def update_user_profile(
    update_data: dict,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Update current user's profile."""
    try:
        from db.crud import update_user

        # Allowed fields to update
        allowed_fields = {"business_name", "preferred_dialect", "business_type"}
        update_dict = {k: v for k, v in update_data.items() if k in allowed_fields}

        user = update_user(db, current_user.id, update_dict)

        logger.info(f"User profile updated: {current_user.id}")

        return user

    except Exception as e:
        logger.error(f"Error updating user profile: {str(e)}")
        raise ValidationError(f"Failed to update profile: {str(e)}")
