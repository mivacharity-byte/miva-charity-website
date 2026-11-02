
from datetime import datetime

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    model_validator,
)


class SiteContentCreate(BaseModel):
    content_key: str = Field(min_length=1, max_length=100)
    content_value: str = Field(min_length=1)


class SiteContentUpdate(BaseModel):
    content_key: str | None = Field(
        default=None,
        min_length=1,
        max_length=100,
    )
    content_value: str | None = Field(
        default=None,
        min_length=1,
    )

    @model_validator(mode="after")
    def reject_null_required_fields(self):
        required_fields = ("content_key", "content_value")

        for field in required_fields:
            if (
                field in self.model_fields_set
                and getattr(self, field) is None
            ):
                raise ValueError(f"{field} cannot be null")

        return self


class SiteContentResponse(BaseModel):
    id: int
    content_key: str
    content_value: str
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
