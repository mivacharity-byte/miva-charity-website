
from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from database import get_db
from models import Event
from schemas.event import EventCreate, EventResponse, EventUpdate
from security import require_admin


router = APIRouter(
    prefix="/api/events",
    tags=["Events"],
)


# PUBLIC: List all events
@router.get("/", response_model=list[EventResponse])
def list_events(
    db: Session = Depends(get_db),
):
    statement = select(Event).order_by(Event.date.asc(), Event.id.asc())
    return db.scalars(statement).all()


# PUBLIC: Get one event
@router.get("/{event_id}", response_model=EventResponse)
def get_event(
    event_id: int,
    db: Session = Depends(get_db),
):
    event = db.get(Event, event_id)

    if event is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Event not found",
        )

    return event


# ADMIN: Create an event
@router.post(
    "/",
    response_model=EventResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_event(
    event_data: EventCreate,
    db: Session = Depends(get_db),
    current_admin=Depends(require_admin),
):
    event = Event(**event_data.model_dump())

    db.add(event)

    try:
        db.commit()
        db.refresh(event)
    except IntegrityError as exc:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Event conflicts with existing data or violates database constraints",
        ) from exc

    return event


# ADMIN: Update an event
@router.patch("/{event_id}", response_model=EventResponse)
def update_event(
    event_id: int,
    event_data: EventUpdate,
    db: Session = Depends(get_db),
    current_admin=Depends(require_admin),
):
    event = db.get(Event, event_id)

    if event is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Event not found",
        )

    updates = event_data.model_dump(exclude_unset=True)

    for field, value in updates.items():
        setattr(event, field, value)

    try:
        db.commit()
        db.refresh(event)
    except IntegrityError as exc:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Event conflicts with existing data or violates database constraints",
        ) from exc

    return event


# ADMIN: Delete an event
@router.delete(
    "/{event_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_event(
    event_id: int,
    db: Session = Depends(get_db),
    current_admin=Depends(require_admin),
):
    event = db.get(Event, event_id)

    if event is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Event not found",
        )

    db.delete(event)

    try:
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Event cannot be deleted because it is referenced by other records",
        ) from exc

    return Response(status_code=status.HTTP_204_NO_CONTENT)
