"""Shared pytest fixtures for the Vireel backend test suite.

Environment variables MUST be set before any `app.*` import happens, since
`app.config.Settings()` (module-level `settings = Settings()`) and
`app.database`'s module-level SQLAlchemy engine are both constructed at
import time from the environment.
"""

import os
import tempfile
from pathlib import Path

_TMP_DIR = Path(tempfile.mkdtemp(prefix="vireel-test-"))
_DB_PATH = (_TMP_DIR / "test.db").as_posix()

os.environ.setdefault("DATABASE_URL", f"sqlite:///{_DB_PATH}")
os.environ.setdefault("SECRET_KEY", "test-secret-key-not-for-production")
os.environ.setdefault("OPENAI_API_KEY", "test-openai-key")
os.environ.setdefault("MEDIA_ROOT", str(_TMP_DIR / "media"))

import pytest  # noqa: E402
from fastapi.testclient import TestClient  # noqa: E402

from app.database import SessionLocal, engine, get_db  # noqa: E402
from app.main import app  # noqa: E402
from app.models import Base  # noqa: E402
from app.rate_limit import limiter  # noqa: E402
from app.services import auth_service  # noqa: E402

# Rate limiting is a production concern; disable it for the whole test
# session so unrelated tests hammering /auth/register or /auth/login don't
# trip each other's 5/minute (etc) limits via slowapi's shared in-memory store.
limiter.enabled = False


@pytest.fixture()
def db_session():
    """Fresh SQLite schema per test, yielding a working SQLAlchemy session."""
    Base.metadata.create_all(bind=engine)
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(bind=engine)


@pytest.fixture()
def client(db_session):
    """A TestClient whose `get_db` dependency is pinned to `db_session`."""

    def _override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = _override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


@pytest.fixture()
def test_user(db_session):
    """Register a user via the service layer and issue a token pair for it."""
    user = auth_service.register_user(db_session, "user@example.com", "password123", "Test User")
    tokens = auth_service.issue_tokens(db_session, user)
    return user, tokens.access_token, tokens.refresh_token


def auth_headers(access_token: str) -> dict[str, str]:
    """Build an Authorization header dict for a given access token."""
    return {"Authorization": f"Bearer {access_token}"}
