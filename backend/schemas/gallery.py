
from datetime import datetime

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    model_validator,
)


class GalleryCreate(BaseModel):
    title: str = Field(min_length=1, max_length=200)
    description: str | None = None
    image_url: str = Field(min_length=1, max_length=500)
    album: str | None = Field(default=None, max_length=100)
    display_order: int = Field(default=0, ge=0)
    is_featured: bool = False


class GalleryUpdate(BaseModel):
    title: str | None = Field(default=None, min_length=1, max_length=200)
    description: str | None = None
    image_url: str | None = Field(default=None, min_length=1, max_length=500)
    album: str | None = Field(default=None, max_length=100)
    display_order: int | None = Field(default=None, ge=0)
    is_featured: bool | None = None

    @model_validator(mode="after")
    def reject_null_required_fields(self):
        required_fields = ("title", "image_url", "display_order", "is_featured")

        for field in required_fields:
            if (
                field in self.model_fields_set
                and getattr(self, field) is None
            ):
                raise ValueError(f"{field} cannot be null")

        return self


class GalleryResponse(BaseModel):
    id: int
    title: str
    description: str | None
    image_url: str
    album: str | None
    display_order: int
    is_featured: bool
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
