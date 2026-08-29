"""Business logic for registration, login, and token lifecycle management."""

from datetime import UTC, datetime, timedelta

from sqlalchemy.orm import Session

from app.auth.jwt import (
    create_access_token,
    create_refresh_token_value,
    hash_password,
    verify_password,
)
from app.config import settings
from app.exceptions import ConflictError, UnauthorizedError
from app.models import RefreshToken, User
from app.schemas.auth import Token


def register_user(db: Session, email: str, password: str, full_name: str | None) -> User:
    """Create a new user account, rejecting duplicate emails."""
    existing = db.query(User).filter(User.email == email).first()
    if existing is not None:
        raise ConflictError("A user with this email already exists")

    user = User(email=email, hashed_password=hash_password(password), full_name=full_name)
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def authenticate_user(db: Session, email: str, password: str) -> User:
    """Verify credentials and return the matching user, or raise UnauthorizedError."""
    user = db.query(User).filter(User.email == email).first()
    if user is None or not verify_password(password, user.hashed_password):
        raise UnauthorizedError("Incorrect email or password")
    if not user.is_active:
        raise UnauthorizedError("Account is inactive")
    return user


def _as_aware_utc(value: datetime) -> datetime:
    """Treat a naive datetime as UTC.

    SQLite (used in tests / local dev) doesn't actually persist tzinfo on a
    `DateTime(timezone=True)` column — it silently drops it, so values read
    back can come out naive even though we always write UTC-aware ones.
    Postgres (production) preserves tzinfo correctly, so this is a no-op there.
    """
    return value if value.tzinfo is not None else value.replace(tzinfo=UTC)


def _store_refresh_token(db: Session, user: User) -> RefreshToken:
    """Create and persist a new RefreshToken row for the given user."""
    expires_at = datetime.now(UTC) + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
    refresh_token = RefreshToken(
        user_id=user.id,
        token=create_refresh_token_value(),
        expires_at=expires_at,
        revoked=False,
    )
    db.add(refresh_token)
    db.commit()
    db.refresh(refresh_token)
    return refresh_token


def issue_tokens(db: Session, user: User) -> Token:
    """Issue a fresh access + refresh token pair for a user."""
    access_token = create_access_token({"sub": str(user.id)})
    refresh_token = _store_refresh_token(db, user)
    return Token(access_token=access_token, refresh_token=refresh_token.token)


def refresh_access_token(db: Session, refresh_token_value: str) -> Token:
    """Validate a refresh token, rotate it, and issue a new access token."""
    stored = db.query(RefreshToken).filter(RefreshToken.token == refresh_token_value).first()
    now = datetime.now(UTC)
    if stored is None or stored.revoked or _as_aware_utc(stored.expires_at) < now:
        raise UnauthorizedError("Invalid or expired refresh token")

    user = db.query(User).filter(User.id == stored.user_id).first()
    if user is None or not user.is_active:
        raise UnauthorizedError("User not found")

    # Rotate: revoke the old refresh token and mint a new one.
    stored.revoked = True
    db.add(stored)
    db.commit()

    access_token = create_access_token({"sub": str(user.id)})
    new_refresh_token = _store_refresh_token(db, user)
    return Token(access_token=access_token, refresh_token=new_refresh_token.token)


def revoke_refresh_token(db: Session, refresh_token_value: str) -> None:
    """Mark a refresh token revoked. Idempotent/no-op if it doesn't exist."""
    stored = db.query(RefreshToken).filter(RefreshToken.token == refresh_token_value).first()
    if stored is None:
        return
    stored.revoked = True
    db.add(stored)
    db.commit()
