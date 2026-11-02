
from datetime import datetime

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    model_validator,
)


class ExecutiveCreate(BaseModel):
    session_id: int = Field(gt=0)
    name: str = Field(min_length=1, max_length=150)
    title: str = Field(min_length=1, max_length=100)
    department: str | None = Field(default=None, max_length=150)
    level: str | None = Field(default=None, max_length=20)
    bio: str | None = None
    photo_url: str | None = Field(default=None, max_length=500)
    display_order: int = Field(default=0, ge=0)
    is_active: bool = True


class ExecutiveUpdate(BaseModel):
    session_id: int | None = Field(default=None, gt=0)
    name: str | None = Field(default=None, min_length=1, max_length=150)
    title: str | None = Field(default=None, min_length=1, max_length=100)
    department: str | None = Field(default=None, max_length=150)
    level: str | None = Field(default=None, max_length=20)
    bio: str | None = None
    photo_url: str | None = Field(default=None, max_length=500)
    display_order: int | None = Field(default=None, ge=0)
    is_active: bool | None = None

    @model_validator(mode="after")
    def reject_null_required_fields(self):
        required_fields = (
            "session_id",
            "name",
            "title",
            "display_order",
            "is_active",
        )

        for field in required_fields:
            if (
                field in self.model_fields_set
                and getattr(self, field) is None
            ):
                raise ValueError(f"{field} cannot be null")

        return self


class ExecutiveResponse(BaseModel):
    id: int
    session_id: int
    name: str
    title: str
    department: str | None
    level: str | None
    bio: str | None
    photo_url: str | None
    display_order: int
    is_active: bool
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
