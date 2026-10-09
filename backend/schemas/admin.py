from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr


class AdminBase(BaseModel):
    name: str
    email: EmailStr
    role: str = "admin"


class AdminCreate(AdminBase):
    password: str


class AdminResponse(AdminBase):
    id: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)