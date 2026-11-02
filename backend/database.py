
import os
from pathlib import Path

from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker

# Load local environment variables during development.
BASE_DIR = Path(__file__).resolve().parent
load_dotenv(BASE_DIR / ".env")

DATABASE_URL = os.getenv("DATABASE_URL")
DB_SSL_CA = os.getenv("DB_SSL_CA")

if not DATABASE_URL:
    raise RuntimeError("DATABASE_URL environment variable is not set.")

# Configure SSL when a CA certificate path is supplied.
connect_args = {}

if DB_SSL_CA:
    ca_path = Path(DB_SSL_CA)

    if not ca_path.is_file():
        raise RuntimeError(
            f"MySQL SSL certificate not found at: {DB_SSL_CA}"
        )

    connect_args["ssl"] = {"ca": str(ca_path)}

class Base(DeclarativeBase):
    pass


engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,
    connect_args=connect_args,
)

SessionLocal = sessionmaker(
    bind=engine,
    autoflush=False,
    autocommit=False,
)


def get_db():
    db = SessionLocal()

    try:
        yield db
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()
