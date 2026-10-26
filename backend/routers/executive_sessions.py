

from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from database import get_db
from models import ExecutiveSession
from schemas.executive_session import (
    ExecutiveSessionCreate,
    ExecutiveSessionResponse,
    ExecutiveSessionUpdate,
)
from security import require_admin


router = APIRouter(
    prefix="/api/executive-sessions",
    tags=["Executive Sessions"],
)


@router.get("/", response_model=list[ExecutiveSessionResponse])
def list_executive_sessions(
    db: Session = Depends(get_db),
):
    statement = select(ExecutiveSession).order_by(
        ExecutiveSession.academic_year.desc(),
        ExecutiveSession.id.desc(),
    )

    return db.scalars(statement).all()


@router.get(
    "/{session_id}",
    response_model=ExecutiveSessionResponse,
)
def get_executive_session(
    session_id: int,
    db: Session = Depends(get_db),
):
    session = db.get(ExecutiveSession, session_id)

    if session is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Executive session not found",
        )

    return session


@router.post(
    "/",
    response_model=ExecutiveSessionResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_executive_session(
    session_data: ExecutiveSessionCreate,
    db: Session = Depends(get_db),
    current_admin=Depends(require_admin),
):
    session_values = session_data.model_dump()
    is_current = session_values["is_current"]

    try:
        if is_current:
            current_sessions = db.scalars(
                select(ExecutiveSession).where(
                    ExecutiveSession.is_current.is_(True)
                )
            ).all()

            for existing_session in current_sessions:
                existing_session.is_current = False

            db.flush()

        executive_session = ExecutiveSession(**session_values)
        db.add(executive_session)
        db.commit()
        db.refresh(executive_session)

        return executive_session

    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="An executive session with this academic year already exists",
        )


@router.patch(
    "/{session_id}",
    response_model=ExecutiveSessionResponse,
)
def update_executive_session(
    session_id: int,
    session_data: ExecutiveSessionUpdate,
    db: Session = Depends(get_db),
    current_admin=Depends(require_admin),
):
    executive_session = db.get(ExecutiveSession, session_id)

    if executive_session is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Executive session not found",
        )

    updates = session_data.model_dump(exclude_unset=True)

    if (
        "academic_year" in updates
        and updates["academic_year"] is None
    ):
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="academic_year cannot be null",
        )

    if "name" in updates and updates["name"] is None:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="name cannot be null",
        )

    if updates.get("is_current") is True:
        other_current_sessions = db.scalars(
            select(ExecutiveSession).where(
                ExecutiveSession.is_current.is_(True),
                ExecutiveSession.id != session_id,
            )
        ).all()

        for other_session in other_current_sessions:
            other_session.is_current = False

        db.flush()

    for field, value in updates.items():
        setattr(executive_session, field, value)

    try:
        db.commit()
        db.refresh(executive_session)

        return executive_session

    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="An executive session with this academic year already exists",
        )


@router.delete(
    "/{session_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_executive_session(
    session_id: int,
    db: Session = Depends(get_db),
    current_admin=Depends(require_admin),
):
    executive_session = db.get(ExecutiveSession, session_id)

    if executive_session is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Executive session not found",
        )

    if executive_session.executives:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Cannot delete an executive session that still has executives",
        )

    db.delete(executive_session)
    db.commit()

    return Response(status_code=status.HTTP_204_NO_CONTENT)
