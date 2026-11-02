
from datetime import datetime

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    model_validator,
)


class ResourceCreate(BaseModel):
    title: str = Field(min_length=1, max_length=200)
    description: str | None = None
    category: str = Field(min_length=1, max_length=100)
    file_url: str = Field(min_length=1, max_length=500)


class ResourceUpdate(BaseModel):
    title: str | None = Field(default=None, min_length=1, max_length=200)
    description: str | None = None
    category: str | None = Field(default=None, min_length=1, max_length=100)
    file_url: str | None = Field(default=None, min_length=1, max_length=500)

    @model_validator(mode="after")
    def reject_null_required_fields(self):
        required_fields = ("title", "category", "file_url")

        for field in required_fields:
            if (
                field in self.model_fields_set
                and getattr(self, field) is None
            ):
                raise ValueError(f"{field} cannot be null")

        return self


class ResourceResponse(BaseModel):
    id: int
    title: str
    description: str | None
    category: str
    file_url: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
