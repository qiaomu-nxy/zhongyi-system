import datetime
from pydantic import BaseModel, ConfigDict, Field


class DoctorCreate(BaseModel):
    username: str = Field(min_length=2, max_length=50)
    password: str = Field(min_length=6)
    name: str = Field(min_length=1, max_length=50)
    role: str = "doctor"


class DoctorUpdate(BaseModel):
    name: str | None = Field(None, max_length=50)
    is_active: bool | None = None


class DoctorPasswordReset(BaseModel):
    new_password: str = Field(min_length=6)


class DoctorResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    username: str
    name: str
    role: str
    is_active: bool
    created_at: datetime.datetime