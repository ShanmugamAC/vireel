"""Shared FastAPI dependencies used across routers.

`get_db` is re-exported from `app.database` (owned by the database module)
so routers only ever need to import from this one place.
"""

from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from app.auth.jwt import decode_access_token
from app.database import get_db
from app.exceptions import UnauthorizedError
from app.models import User

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")


async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db),
) -> User:
    """Resolve the current authenticated user from a JWT bearer token."""
    payload = decode_access_token(token)
    if payload is None or payload.get("sub") is None:
        raise UnauthorizedError("Invalid or expired token")

    try:
        user_id = int(payload["sub"])
    except (TypeError, ValueError) as exc:
        raise UnauthorizedError("Invalid or expired token") from exc

    user = db.query(User).filter(User.id == user_id).first()
    if user is None or not user.is_active:
        raise UnauthorizedError("User not found")
    return user
