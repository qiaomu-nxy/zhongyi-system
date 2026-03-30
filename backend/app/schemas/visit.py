import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


VisitStatus = Literal["待签到", "待接诊", "已完成", "已作废"]


class PatientBrief(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    phone: str
    gender: str | None
    birth_date: datetime.date | None


class VisitCreate(BaseModel):
    patient_id: int
    visit_date: datetime.date = Field(default_factory=datetime.date.today)
    chief_complaint: str | None = None


class VisitUpdate(BaseModel):
    status: VisitStatus | None = None
    chief_complaint: str | None = None


class VisitResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    patient_id: int
    doctor_id: int | None
    visit_date: datetime.date
    visit_number: int
    status: str
    chief_complaint: str | None
    symptom_submitted_at: datetime.datetime | None
    created_at: datetime.datetime
    patient: PatientBrief | None = None