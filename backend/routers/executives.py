
from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from database import get_db
from models import Executive, ExecutiveSession
from schemas.executive import (
    ExecutiveCreate,
    ExecutiveResponse,
    ExecutiveUpdate,
)
from security import require_admin


router = APIRouter(
    prefix="/api/executives",
    tags=["Executives"],
)


# PUBLIC: List active executives.
@router.get("/", response_model=list[ExecutiveResponse])
def list_executives(
    session_id: int | None = None,
    db: Session = Depends(get_db),
):
    statement = select(Executive).where(
        Executive.is_active.is_(True)
    )

    if session_id is not None:
        statement = statement.where(
            Executive.session_id == session_id
        )

    statement = statement.order_by(
        Executive.display_order.asc(),
        Executive.id.asc(),
    )

    return db.scalars(statement).all()


# PUBLIC: List executives belonging to the current session.
@router.get("/current", response_model=list[ExecutiveResponse])
def get_current_executives(
    db: Session = Depends(get_db),
):
    current_session = db.scalar(
        select(ExecutiveSession).where(
            ExecutiveSession.is_current.is_(True)
        )
    )

    if current_session is None:
        return []

    statement = (
        select(Executive)
        .where(
            Executive.session_id == current_session.id,
            Executive.is_active.is_(True),
        )
        .order_by(
            Executive.display_order.asc(),
            Executive.id.asc(),
        )
    )

    return db.scalars(statement).all()


# ADMIN: View all executives, including inactive and historical records.
@router.get(
    "/admin/all",
    response_model=list[ExecutiveResponse],
)
def list_all_executives(
    db: Session = Depends(get_db),
    current_admin=Depends(require_admin),
):
    statement = select(Executive).order_by(
        Executive.session_id.desc(),
        Executive.display_order.asc(),
        Executive.id.asc(),
    )

    return db.scalars(statement).all()


# PUBLIC: List active executives in a particular session.
@router.get(
    "/session/{session_id}",
    response_model=list[ExecutiveResponse],
)
def get_executives_by_session(
    session_id: int,
    db: Session = Depends(get_db),
):
    executive_session = db.get(ExecutiveSession, session_id)

    if executive_session is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Executive session not found",
        )

    statement = (
        select(Executive)
        .where(
            Executive.session_id == session_id,
            Executive.is_active.is_(True),
        )
        .order_by(
            Executive.display_order.asc(),
            Executive.id.asc(),
        )
    )

    return db.scalars(statement).all()


# PUBLIC: Retrieve an active executive by ID.
@router.get(
    "/{executive_id}",
    response_model=ExecutiveResponse,
)
def get_executive(
    executive_id: int,
    db: Session = Depends(get_db),
):
    executive = db.get(Executive, executive_id)

    if executive is None or not executive.is_active:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Executive not found",
        )

    return executive


# ADMIN: Create an executive.
@router.post(
    "/",
    response_model=ExecutiveResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_executive(
    executive_data: ExecutiveCreate,
    db: Session = Depends(get_db),
    current_admin=Depends(require_admin),
):
    executive_session = db.get(
        ExecutiveSession,
        executive_data.session_id,
    )

    if executive_session is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Executive session not found",
        )

    executive = Executive(**executive_data.model_dump())

    db.add(executive)
    db.commit()
    db.refresh(executive)

    return executive


# ADMIN: Update an executive.
@router.patch(
    "/{executive_id}",
    response_model=ExecutiveResponse,
)
def update_executive(
    executive_id: int,
    executive_data: ExecutiveUpdate,
    db: Session = Depends(get_db),
    current_admin=Depends(require_admin),
):
    executive = db.get(Executive, executive_id)

    if executive is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Executive not found",
        )

    updates = executive_data.model_dump(exclude_unset=True)

    if "session_id" in updates:
        if updates["session_id"] is None:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="session_id cannot be null",
            )

        executive_session = db.get(
            ExecutiveSession,
            updates["session_id"],
        )

        if executive_session is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Executive session not found",
            )

    for field, value in updates.items():
        setattr(executive, field, value)

    db.commit()
    db.refresh(executive)

    return executive


# ADMIN: Delete an executive.
@router.delete(
    "/{executive_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_executive(
    executive_id: int,
    db: Session = Depends(get_db),
    current_admin=Depends(require_admin),
):
    executive = db.get(Executive, executive_id)

    if executive is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Executive not found",
        )

    db.delete(executive)
    db.commit()

    return Response(status_code=status.HTTP_204_NO_CONTENT)
