
from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


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
