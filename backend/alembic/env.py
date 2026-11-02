from logging.config import fileConfig
import os
from pathlib import Path

from alembic import context
from dotenv import load_dotenv
from sqlalchemy import create_engine, pool

from database import Base
from models.admin import Admin  # noqa: F401
from models.event import Event  # noqa: F401
from models.news import News  # noqa: F401
from models.executive_session import ExecutiveSession  # noqa: F401
from models.executive import Executive  # noqa: F401
from models.gallery import Gallery  # noqa: F401
from models.resource import Resource  # noqa: F401
from models.site_content import SiteContent  # noqa: F401


BASE_DIR = Path(__file__).resolve().parents[1]
load_dotenv(BASE_DIR / ".env")

config = context.config

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    raise RuntimeError("DATABASE_URL is not set in the .env file")

target_metadata = Base.metadata


def run_migrations_offline() -> None:
    """Run migrations without creating a database connection."""
    context.configure(
        url=DATABASE_URL,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        compare_type=True,
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Run migrations using a live database connection."""
    engine = create_engine(
        DATABASE_URL,
        poolclass=pool.NullPool,
    )

    try:
        with engine.connect() as connection:
            context.configure(
                connection=connection,
                target_metadata=target_metadata,
                compare_type=True,
            )

            with context.begin_transaction():
                context.run_migrations()
    finally:
        engine.dispose()

if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
