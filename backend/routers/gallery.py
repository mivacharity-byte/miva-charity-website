
from fastapi import APIRouter, Depends, HTTPException, Query, Response, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from database import get_db
from models.gallery import Gallery
from schemas.gallery import (
    GalleryCreate,
    GalleryUpdate,
    GalleryResponse,
)
from security import require_admin


router = APIRouter(
    prefix="/api/gallery",
    tags=["Gallery"],
)


# PUBLIC: List gallery entries.
@router.get("/", response_model=list[GalleryResponse])
def list_gallery(
    album: str | None = None,
    featured: bool | None = None,
    db: Session = Depends(get_db),
):
    statement = select(Gallery)

    if album is not None:
        statement = statement.where(Gallery.album == album)

    if featured is not None:
        statement = statement.where(Gallery.is_featured == featured)

    statement = statement.order_by(
        Gallery.display_order.asc(),
        Gallery.created_at.desc(),
    )

    return db.scalars(statement).all()


# PUBLIC: Get one gallery entry.
@router.get("/{gallery_id}", response_model=GalleryResponse)
def get_gallery_item(
    gallery_id: int,
    db: Session = Depends(get_db),
):
    gallery_item = db.get(Gallery, gallery_id)

    if gallery_item is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Gallery item not found",
        )

    return gallery_item


# ADMIN: Create a gallery entry.
@router.post(
    "/",
    response_model=GalleryResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_gallery_item(
    payload: GalleryCreate,
    db: Session = Depends(get_db),
    current_admin=Depends(require_admin),
):
    gallery_item = Gallery(**payload.model_dump())

    db.add(gallery_item)
    db.commit()
    db.refresh(gallery_item)

    return gallery_item


# ADMIN: Update a gallery entry.
@router.patch(
    "/{gallery_id}",
    response_model=GalleryResponse,
)
def update_gallery_item(
    gallery_id: int,
    payload: GalleryUpdate,
    db: Session = Depends(get_db),
    current_admin=Depends(require_admin),
):
    gallery_item = db.get(Gallery, gallery_id)

    if gallery_item is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Gallery item not found",
        )

    update_data = payload.model_dump(exclude_unset=True)

    for field, value in update_data.items():
        setattr(gallery_item, field, value)

    db.commit()
    db.refresh(gallery_item)

    return gallery_item


# ADMIN: Delete a gallery entry.
@router.delete(
    "/{gallery_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_gallery_item(
    gallery_id: int,
    db: Session = Depends(get_db),
    current_admin=Depends(require_admin),
):
    gallery_item = db.get(Gallery, gallery_id)

    if gallery_item is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Gallery item not found",
        )

    db.delete(gallery_item)
    db.commit()

    return Response(status_code=status.HTTP_204_NO_CONTENT)
