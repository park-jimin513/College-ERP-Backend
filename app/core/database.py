<<<<<<< HEAD
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from app.core.config import settings

# For SQLite, set check_same_thread=False
connect_args = {"check_same_thread": False} if settings.DATABASE_URL.startswith("sqlite") else {}

engine = create_engine(
    settings.DATABASE_URL,
    connect_args=connect_args,
    echo=False
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def get_db():
    """Dependency for obtaining database session per request."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
=======
from collections.abc import Iterator

from pymongo.database import Database

from app.core import mongo


def get_db() -> Iterator[Database]:
    database = mongo.mongo_db
    if database is None:
        raise RuntimeError("MongoDB is not configured.")
    yield database
>>>>>>> 78179b12b85b0a3294f129846aac5471930886b9
