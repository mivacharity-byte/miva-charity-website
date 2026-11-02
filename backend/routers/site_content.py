
from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from database import get_db
from models.site_content import SiteContent
from schemas.site_content import (
    SiteContentCreate,
    SiteContentUpdate,
    SiteContentResponse,
)
from security import require_admin


router = APIRouter(
    prefix="/api/site-content",
    tags=["Site Content"],
)


# PUBLIC: Retrieve all site content.
@router.get("/", response_model=list[SiteContentResponse])
def list_site_content(
    db: Session = Depends(get_db),
):
    statement = select(SiteContent).order_by(SiteContent.content_key.asc())

    return db.scalars(statement).all()


# PUBLIC: Retrieve content by key.
@router.get("/{content_key}", response_model=SiteContentResponse)
def get_site_content(
    content_key: str,
    db: Session = Depends(get_db),
):
    statement = select(SiteContent).where(
        SiteContent.content_key == content_key
    )

    content = db.scalar(statement)

    if content is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Site content not found",
        )

    return content


# ADMIN: Create site content.
@router.post(
    "/",
    response_model=SiteContentResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_site_content(
    payload: SiteContentCreate,
    db: Session = Depends(get_db),
    current_admin=Depends(require_admin),
):
    existing_content = db.scalar(
        select(SiteContent).where(
            SiteContent.content_key == payload.content_key
        )
    )

    if existing_content is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="A content item with this key already exists",
        )

    content = SiteContent(**payload.model_dump())

    db.add(content)

    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="A content item with this key already exists",
        )

    db.refresh(content)

    return content


# ADMIN: Update site content.
@router.patch(
    "/{content_id}",
    response_model=SiteContentResponse,
)
def update_site_content(
    content_id: int,
    payload: SiteContentUpdate,
    db: Session = Depends(get_db),
    current_admin=Depends(require_admin),
):
    content = db.get(SiteContent, content_id)

    if content is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Site content not found",
        )

    update_data = payload.model_dump(exclude_unset=True)

    new_key = update_data.get("content_key")

    if new_key is not None and new_key != content.content_key:
        existing_content = db.scalar(
            select(SiteContent).where(
                SiteContent.content_key == new_key,
                SiteContent.id != content_id,
            )
        )

        if existing_content is not None:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="A content item with this key already exists",
            )

    for field, value in update_data.items():
        setattr(content, field, value)

    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="A content item with this key already exists",
        )

    db.refresh(content)

    return content


# ADMIN: Delete site content.
@router.delete(
    "/{content_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_site_content(
    content_id: int,
    db: Session = Depends(get_db),
    current_admin=Depends(require_admin),
):
    content = db.get(SiteContent, content_id)

    if content is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Site content not found",
        )

    db.delete(content)
    db.commit()

    return Response(status_code=status.HTTP_204_NO_CONTENT)
