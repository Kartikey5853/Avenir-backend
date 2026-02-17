"""
Authentication router – register, login, forgot password, reset password.
"""

import secrets
import logging
from datetime import datetime, timedelta, timezone

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.user import User
from app.schemas.auth import (
    RegisterRequest,
    LoginRequest,
    ForgotPasswordRequest,
    ResetPasswordRequest,
    TokenResponse,
    UserResponse,
    MessageResponse,
)
from app.utils.security import hash_password, verify_password, create_access_token

logger = logging.getLogger(__name__)
router = APIRouter(tags=["Authentication"])


@router.post("/register", response_model=TokenResponse, status_code=status.HTTP_201_CREATED)
def register(req: RegisterRequest, db: Session = Depends(get_db)):
    """
    Register a new user.
    - Validates email uniqueness
    - Hashes password with bcrypt
    - Returns JWT token immediately (auto-login after registration)
    """
    # Check if email already exists
    existing = db.query(User).filter(User.email == req.email).first()
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")

    # Create user with hashed password
    user = User(
        name=req.name,
        email=req.email,
        password_hash=hash_password(req.password),
        is_profile_completed=False,
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    # Generate JWT
    token = create_access_token(data={"sub": str(user.id)})
    logger.info(f"User registered: {user.email}")

    return TokenResponse(
        access_token=token,
        user=UserResponse.model_validate(user),
    )


@router.post("/login", response_model=TokenResponse)
def login(req: LoginRequest, db: Session = Depends(get_db)):
    """
    Authenticate user and return JWT.
    Response includes is_profile_completed so frontend can prompt profile setup.
    """
    user = db.query(User).filter(User.email == req.email).first()
    if not user or not verify_password(req.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Invalid email or password")

    token = create_access_token(data={"sub": str(user.id)})
    logger.info(f"User logged in: {user.email}")

    return TokenResponse(
        access_token=token,
        user=UserResponse.model_validate(user),
    )


@router.post("/forgot-password", response_model=MessageResponse)
def forgot_password(req: ForgotPasswordRequest, db: Session = Depends(get_db)):
    """
    Generate a password reset token.
    In production, this would send an email. For now, the token is stored
    and returned in the response (stubbed email).
    """
    user = db.query(User).filter(User.email == req.email).first()
    if not user:
        # Don't reveal whether user exists
        return MessageResponse(message="If an account with that email exists, a reset link has been sent.")

    # Generate reset token
    reset_token = secrets.token_urlsafe(32)
    user.reset_token = reset_token
    user.reset_token_expires = datetime.now(timezone.utc) + timedelta(hours=1)
    db.commit()

    # STUB: In production, send email with reset link
    logger.info(f"Password reset token generated for {user.email}: {reset_token}")

    return MessageResponse(message="If an account with that email exists, a reset link has been sent.")


@router.post("/reset-password", response_model=MessageResponse)
def reset_password(req: ResetPasswordRequest, db: Session = Depends(get_db)):
    """
    Reset password using a valid reset token.
    """
    user = db.query(User).filter(User.reset_token == req.token).first()
    if not user:
        raise HTTPException(status_code=400, detail="Invalid or expired reset token")

    # Check expiration
    if user.reset_token_expires and user.reset_token_expires.replace(tzinfo=timezone.utc) < datetime.now(timezone.utc):
        raise HTTPException(status_code=400, detail="Reset token has expired")

    # Update password
    user.password_hash = hash_password(req.new_password)
    user.reset_token = None
    user.reset_token_expires = None
    db.commit()

    logger.info(f"Password reset successful for {user.email}")
    return MessageResponse(message="Password reset successful. You can now login.")
