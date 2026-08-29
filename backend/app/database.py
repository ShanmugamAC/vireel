"""Database engine, session factory, and FastAPI `get_db` dependency.

NOTE: reads DATABASE_URL directly from the environment rather than from
`app.config.settings`, since config.py is owned by another agent running in
parallel. Once config.py is confirmed stable, this can be switched to import
`settings.DATABASE_URL` instead.
"""

import os
from collections.abc import Generator

from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

DATABASE_URL = os.environ.get(
    "DATABASE_URL", "postgresql://user:pass@localhost:5432/vireel"
)

engine = create_engine(DATABASE_URL, pool_pre_ping=True)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db() -> Generator[Session, None, None]:
    """FastAPI dependency: yield a request-scoped DB session, always closing it."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
