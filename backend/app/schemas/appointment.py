import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator

AppointmentStatus = Literal["待就诊", "已完成", "已取消", "爽约"]


class AppointmentCreate(BaseModel):
    patient_id: int
    appointment_date: datetime.date
    time_slot: str = Field(pattern=r"^\d{2}:\d{2}$")

    @field_validator("appointment_date")
    @classmethod
    def validate_date(cls, v: datetime.date) -> datetime.date:
        today = datetime.date.today()
        if v < today:
            raise ValueError("预约日期不能是过去的日期")
        if v > today + datetime.timedelta(days=7):
            raise ValueError("预约日期不能超过今天起7天")
        return v


class AppointmentCancelRequest(BaseModel):
    cancel_reason: str | None = Field(None, max_length=200)


class PatientBriefInApt(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    phone: str
    gender: str | None


class AppointmentResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    patient_id: int
    doctor_id: int | None
    appointment_date: datetime.date
    time_slot: str
    status: str
    cancel_reason: str | None
    created_at: datetime.datetime
    patient: PatientBriefInApt | None = None