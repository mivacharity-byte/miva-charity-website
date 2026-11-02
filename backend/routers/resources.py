
from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from database import get_db
from models.resource import Resource
from schemas.resource import (
    ResourceCreate,
    ResourceUpdate,
    ResourceResponse,
)
from security import require_admin


router = APIRouter(
    prefix="/api/resources",
    tags=["Resources"],
)


# PUBLIC: List resources.
@router.get("/", response_model=list[ResourceResponse])
def list_resources(
    category: str | None = None,
    db: Session = Depends(get_db),
):
    statement = select(Resource)

    if category is not None:
        statement = statement.where(Resource.category == category)

    statement = statement.order_by(Resource.created_at.desc())

    return db.scalars(statement).all()


# PUBLIC: Get one resource.
@router.get("/{resource_id}", response_model=ResourceResponse)
def get_resource(
    resource_id: int,
    db: Session = Depends(get_db),
):
    resource = db.get(Resource, resource_id)

    if resource is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Resource not found",
        )

    return resource


# ADMIN: Create a resource.
@router.post(
    "/",
    response_model=ResourceResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_resource(
    payload: ResourceCreate,
    db: Session = Depends(get_db),
    current_admin=Depends(require_admin),
):
    resource = Resource(**payload.model_dump())

    db.add(resource)
    db.commit()
    db.refresh(resource)

    return resource


# ADMIN: Update a resource.
@router.patch(
    "/{resource_id}",
    response_model=ResourceResponse,
)
def update_resource(
    resource_id: int,
    payload: ResourceUpdate,
    db: Session = Depends(get_db),
    current_admin=Depends(require_admin),
):
    resource = db.get(Resource, resource_id)

    if resource is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Resource not found",
        )

    update_data = payload.model_dump(exclude_unset=True)

    for field, value in update_data.items():
        setattr(resource, field, value)

    db.commit()
    db.refresh(resource)

    return resource


# ADMIN: Delete a resource.
@router.delete(
    "/{resource_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_resource(
    resource_id: int,
    db: Session = Depends(get_db),
    current_admin=Depends(require_admin),
):
    resource = db.get(Resource, resource_id)

    if resource is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Resource not found",
        )

    db.delete(resource)
    db.commit()

    return Response(status_code=status.HTTP_204_NO_CONTENT)
