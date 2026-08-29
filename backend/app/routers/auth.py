"""Auth endpoints: register, login, refresh, logout, and profile."""

from fastapi import APIRouter, Depends, Request, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.dependencies import get_current_user, get_db
from app.models import User
from app.rate_limit import limiter
from app.schemas.auth import (
    RefreshRequest,
    RegisterRequest,
    Token,
    UserResponse,
    UserUpdateRequest,
)
from app.services import auth_service

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
@limiter.limit("5/minute")
async def register(
    request: Request,
    payload: RegisterRequest,
    db: Session = Depends(get_db),
) -> User:
    """Create a new user account."""
    return auth_service.register_user(db, payload.email, payload.password, payload.full_name)


@router.post("/login", response_model=Token)
@limiter.limit("5/minute")
async def login(
    request: Request,
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db),
) -> Token:
    """Authenticate with email (as `username`) + password, returning a token pair.

    NOTE: `authenticate_user` raises `UnauthorizedError`, which the app-wide
    `AppException` handler already turns into a 401 JSON response, so no
    extra try/except is needed here.
    """
    user = auth_service.authenticate_user(db, form_data.username, form_data.password)
    return auth_service.issue_tokens(db, user)


@router.post("/refresh", response_model=Token)
async def refresh(payload: RefreshRequest, db: Session = Depends(get_db)) -> Token:
    """Exchange a valid refresh token for a new access + refresh token pair."""
    return auth_service.refresh_access_token(db, payload.refresh_token)


@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
async def logout(payload: RefreshRequest, db: Session = Depends(get_db)) -> None:
    """Revoke a refresh token."""
    auth_service.revoke_refresh_token(db, payload.refresh_token)


@router.get("/me", response_model=UserResponse)
async def get_me(current_user: User = Depends(get_current_user)) -> User:
    """Return the currently authenticated user's profile."""
    return current_user


@router.put("/me", response_model=UserResponse)
async def update_me(
    payload: UserUpdateRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> User:
    """Update the currently authenticated user's profile."""
    if payload.full_name is not None:
        current_user.full_name = payload.full_name
        db.add(current_user)
        db.commit()
        db.refresh(current_user)
    return current_user
