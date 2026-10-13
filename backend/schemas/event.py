from datetime import date as date_type
from datetime import datetime as datetime_type
from datetime import time as time_type

from pydantic import BaseModel, ConfigDict, Field



class EventCreate(BaseModel):
    title: str = Field(min_length=1, max_length=200)
    description: str = Field(min_length=1)
    date: date_type
    time: time_type | None = None
    location: str | None = Field(default=None, max_length=255)
    image_url: str | None = Field(default=None, max_length=500)
    registration_url: str | None = Field(default=None, max_length=500)
    status: str = Field(default="upcoming", max_length=20)
    is_featured: bool = False


class EventUpdate(BaseModel):
    title: str | None = Field(default=None, min_length=1, max_length=200)
    description: str | None = Field(default=None, min_length=1)
    date: date_type | None = None
    time: time_type | None = None
    location: str | None = Field(default=None, max_length=255)
    image_url: str | None = Field(default=None, max_length=500)
    registration_url: str | None = Field(default=None, max_length=500)
    status: str | None = Field(default=None, max_length=20)
    is_featured: bool | None = None


class EventResponse(BaseModel):
    id: int
    title: str
    description: str
    date: date_type
    time: time_type | None
    location: str | None
    image_url: str | None
    registration_url: str | None
    status: str
    is_featured: bool
    created_at: datetime_type

    model_config = ConfigDict(from_attributes=True)
