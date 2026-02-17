"""
Database engine and session factory.
Designed for SQLite in dev, PostgreSQL in production.
"""

import os
from sqlalchemy import create_engine
from sqlalchemy.engine.url import make_url
from sqlalchemy.orm import sessionmaker, declarative_base
from app.config import get_settings

settings = get_settings()

# Use DATABASE_URL from environment or config
DATABASE_URL = os.environ.get("DATABASE_URL") or settings.DATABASE_URL
url_obj = make_url(DATABASE_URL)

if url_obj.drivername.startswith("sqlite"):
    connect_args = {"check_same_thread": False}
else:
    connect_args = {}

engine = create_engine(
    DATABASE_URL,
    connect_args=connect_args,
    echo=False,
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


def get_db():
    """Dependency that yields a database session and closes it after use."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
