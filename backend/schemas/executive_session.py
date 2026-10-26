
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class ExecutiveSessionCreate(BaseModel):
    name: str = Field(min_length=1, max_length=150)
    academic_year: str = Field(min_length=1, max_length=20)
    is_current: bool = False


class ExecutiveSessionUpdate(BaseModel):
    name: str | None = Field(
        default=None,
        min_length=1,
        max_length=150,
    )
    academic_year: str | None = Field(
        default=None,
        min_length=1,
        max_length=20,
    )
    is_current: bool | None = None


class ExecutiveSessionResponse(BaseModel):
    id: int
    name: str
    academic_year: str
    is_current: bool
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
