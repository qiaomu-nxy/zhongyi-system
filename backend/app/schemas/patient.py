import datetime
import json

from pydantic import BaseModel, ConfigDict, Field, field_validator


class PatientCreate(BaseModel):
    name: str = Field(min_length=1, max_length=50)
    phone: str
    gender: str | None = None
    birth_date: datetime.date | None = None
    medical_history: list[str] | None = None
    allergy_history: str | None = Field(None, max_length=500)

    @field_validator("phone")
    @classmethod
    def phone_digits(cls, v: str) -> str:
        if not v.isdigit() or len(v) != 11:
            raise ValueError("手机号必须为11位数字")
        return v


class PatientUpdate(BaseModel):
    name: str | None = Field(None, min_length=1, max_length=50)
    gender: str | None = None
    birth_date: datetime.date | None = None
    medical_history: list[str] | None = None
    allergy_history: str | None = Field(None, max_length=500)


class PatientResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    phone: str
    gender: str | None
    birth_date: datetime.date | None
    medical_history: list[str] | None = None
    allergy_history: str | None
    is_active: bool
    created_at: datetime.datetime

    @field_validator("medical_history", mode="before")
    @classmethod
    def parse_medical_history(cls, v):
        if isinstance(v, str):
            try:
                return json.loads(v)
            except Exception:
                return []
        return v