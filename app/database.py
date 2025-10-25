from __future__ import annotations

import os
from contextlib import contextmanager
from typing import Iterator

from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker, DeclarativeBase


class Base(DeclarativeBase):
    pass


def _create_engine():
    database_url = os.getenv("DATABASE_URL", "sqlite:///market_data.db")

    if database_url.startswith("sqlite"):
        return create_engine(
            database_url, connect_args={"check_same_thread": False}, future=True
        )
    return create_engine(database_url, future=True)


def init_db() -> None:
    from . import models  # noqa: F401  # ensure models are registered

    Base.metadata.create_all(bind=engine)


engine = _create_engine()
SessionLocal = scoped_session(sessionmaker(bind=engine, autoflush=False, autocommit=False))


@contextmanager
def session_scope() -> Iterator[scoped_session]:
    session = SessionLocal()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()
