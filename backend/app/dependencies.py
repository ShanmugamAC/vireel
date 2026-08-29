"""Shared FastAPI dependencies used across routers.

`get_db` is re-exported from `app.database` (owned by the database module)
so routers only ever need to import from this one place.

`get_current_user` is a placeholder until the auth module phase implements
real JWT validation. It exists now so routers can already declare the
dependency in their signatures without breaking once auth lands.
"""

from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from app.database import get_db

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")


async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db),
) -> None:
    """Resolve the current authenticated user from a JWT bearer token.

    STUB: real JWT decoding + user lookup lands in the auth-module phase.
    """
    raise NotImplementedError("get_current_user is not yet implemented (auth module phase)")
