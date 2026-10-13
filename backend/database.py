
import os
from pathlib import Path

from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker


# Load environment variables from the backend folder
BASE_DIR = Path(__file__).resolve().parent
load_dotenv(BASE_DIR / ".env")


# Get the database connection URL
DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    raise RuntimeError("DATABASE_URL is not set in the .env file")


# Base class for SQLAlchemy models
class Base(DeclarativeBase):
    pass


# Create the database engine
engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,
)


# Create the database session factory
SessionLocal = sessionmaker(
    bind=engine,
    autoflush=False,
    autocommit=False,
)


# Provide a database session to each request
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
