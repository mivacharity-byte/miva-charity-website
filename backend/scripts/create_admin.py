import getpass

from sqlalchemy import select

from database import SessionLocal
from models import Admin, News, Executive, ExecutiveSession
from security import hash_password


def main() -> None:
    name = input("Admin name: ").strip()
    email = input("Admin email: ").strip().lower()
    password = getpass.getpass("Admin password: ")

    if not name:
        raise ValueError("Admin name is required.")

    if not email:
        raise ValueError("Admin email is required.")

    if len(password) < 8:
        raise ValueError("Password must be at least 8 characters.")

    db = SessionLocal()

    try:
        existing_admin = db.scalar(
            select(Admin).where(Admin.email == email)
        )

        if existing_admin:
            raise ValueError("An admin with this email already exists.")

        admin = Admin(
            name=name,
            email=email,
            password_hash=hash_password(password),
            role="admin",
        )

        db.add(admin)
        db.commit()
        db.refresh(admin)

        print(f"Admin created successfully. ID: {admin.id}")

    except Exception:
        db.rollback()
        raise

    finally:
        db.close()


if __name__ == "__main__":
    main()