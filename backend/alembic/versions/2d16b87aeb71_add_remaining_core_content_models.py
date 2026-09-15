"""Add remaining core content models

Revision ID: 2d16b87aeb71
Revises: c59ea7855730
Create Date: 2026-09-15 13:14:16.531139

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql


# revision identifiers, used by Alembic.
revision: str = "2d16b87aeb71"
down_revision: Union[str, Sequence[str], None] = "c59ea7855730"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""

    # Create executive sessions table
    op.create_table(
        "executive_sessions",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(length=150), nullable=False),
        sa.Column("academic_year", sa.String(length=20), nullable=False),
        sa.Column("is_current", sa.Boolean(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("academic_year"),
    )

    op.create_index(
        op.f("ix_executive_sessions_id"),
        "executive_sessions",
        ["id"],
        unique=False,
    )

    # Create gallery table
    op.create_table(
        "gallery",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("title", sa.String(length=200), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("image_url", sa.String(length=500), nullable=False),
        sa.Column("album", sa.String(length=100), nullable=True),
        sa.Column("display_order", sa.Integer(), nullable=False),
        sa.Column("is_featured", sa.Boolean(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_index(
        op.f("ix_gallery_album"),
        "gallery",
        ["album"],
        unique=False,
    )

    op.create_index(
        op.f("ix_gallery_id"),
        "gallery",
        ["id"],
        unique=False,
    )

    # Create resources table
    op.create_table(
        "resources",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("title", sa.String(length=200), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("category", sa.String(length=100), nullable=False),
        sa.Column("file_url", sa.String(length=500), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_index(
        op.f("ix_resources_category"),
        "resources",
        ["category"],
        unique=False,
    )

    op.create_index(
        op.f("ix_resources_id"),
        "resources",
        ["id"],
        unique=False,
    )

    # Create site content table
    op.create_table(
        "site_content",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("content_key", sa.String(length=100), nullable=False),
        sa.Column("content_value", sa.Text(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_index(
        op.f("ix_site_content_content_key"),
        "site_content",
        ["content_key"],
        unique=True,
    )

    op.create_index(
        op.f("ix_site_content_id"),
        "site_content",
        ["id"],
        unique=False,
    )

    # Update existing executives table
    op.add_column(
        "executives",
        sa.Column("session_id", sa.Integer(), nullable=False),
    )

    op.add_column(
        "executives",
        sa.Column("title", sa.String(length=100), nullable=False),
    )

    op.create_index(
        op.f("ix_executives_session_id"),
        "executives",
        ["session_id"],
        unique=False,
    )

    op.create_foreign_key(
        "fk_executives_session_id",
        "executives",
        "executive_sessions",
        ["session_id"],
        ["id"],
    )

    op.drop_column("executives", "position")


def downgrade() -> None:
    """Downgrade schema."""

    op.add_column(
        "executives",
        sa.Column(
            "position",
            mysql.VARCHAR(length=100),
            nullable=False,
        ),
    )

    op.drop_constraint(
        "fk_executives_session_id",
        "executives",
        type_="foreignkey",
    )

    op.drop_index(
        op.f("ix_executives_session_id"),
        table_name="executives",
    )

    op.drop_column("executives", "title")
    op.drop_column("executives", "session_id")

    op.drop_index(
        op.f("ix_site_content_id"),
        table_name="site_content",
    )

    op.drop_index(
        op.f("ix_site_content_content_key"),
        table_name="site_content",
    )

    op.drop_table("site_content")

    op.drop_index(
        op.f("ix_resources_id"),
        table_name="resources",
    )

    op.drop_index(
        op.f("ix_resources_category"),
        table_name="resources",
    )

    op.drop_table("resources")

    op.drop_index(
        op.f("ix_gallery_id"),
        table_name="gallery",
    )

    op.drop_index(
        op.f("ix_gallery_album"),
        table_name="gallery",
    )

    op.drop_table("gallery")

    op.drop_index(
        op.f("ix_executive_sessions_id"),
        table_name="executive_sessions",
    )

    op.drop_table("executive_sessions")