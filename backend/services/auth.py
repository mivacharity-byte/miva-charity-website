from sqlalchemy import select
from sqlalchemy.orm import Session

from models.admin import Admin
from security import verify_password


def authenticate_admin(
    db: Session,
    email: str,
    password: str,
) -> Admin | None:
    """Find an admin by email and verify the password."""

    statement = select(Admin).where(Admin.email == email)

    admin = db.scalar(statement)

    if admin is None:
        return None

    if not verify_password(password, admin.password_hash):
        return None

    return admin