
from datetime import datetime
from typing import Literal

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    model_validator,
)


NewsStatus = Literal["draft", "published"]


class NewsCreate(BaseModel):
    title: str = Field(min_length=1, max_length=200)
    content: str = Field(min_length=1)
    image_url: str | None = Field(default=None, max_length=500)
    status: NewsStatus = "draft"


class NewsUpdate(BaseModel):
    title: str | None = Field(default=None, min_length=1, max_length=200)
    content: str | None = Field(default=None, min_length=1)
    image_url: str | None = Field(default=None, max_length=500)
    status: NewsStatus | None = None

    @model_validator(mode="after")
    def validate_required_fields(self):
        for field in ("title", "content", "status"):
            if field in self.model_fields_set and getattr(self, field) is None:
                raise ValueError(f"{field} cannot be null")
        return self


class NewsResponse(BaseModel):
    id: int
    title: str
    content: str
    image_url: str | None
    author_id: int
    status: NewsStatus
    published_at: datetime | None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
