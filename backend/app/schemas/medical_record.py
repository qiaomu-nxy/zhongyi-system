import datetime
import json
from typing import Literal

from pydantic import BaseModel, ConfigDict, field_validator

TreatmentType = Literal["中药", "针灸", "推拿", "艾灸", "其他"]


class MedicalRecordCreate(BaseModel):
    treatment_types: list[TreatmentType]
    tongue_diagnosis: str | None = None
    pulse_diagnosis: str | None = None
    physical_signs: str | None = None
    diagnosis: str | None = None
    syndrome_differentiation: str | None = None
    treatment_plan: str | None = None
    prescription: str | None = None
    acupuncture_points: list[str] | None = None
    notes: str | None = None


class MedicalRecordUpdate(BaseModel):
    treatment_types: list[TreatmentType] | None = None
    tongue_diagnosis: str | None = None
    pulse_diagnosis: str | None = None
    physical_signs: str | None = None
    diagnosis: str | None = None
    syndrome_differentiation: str | None = None
    treatment_plan: str | None = None
    prescription: str | None = None
    acupuncture_points: list[str] | None = None
    notes: str | None = None


class MedicalRecordResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    visit_id: int
    doctor_id: int | None
    treatment_types: list[str] = []
    tongue_diagnosis: str | None
    pulse_diagnosis: str | None
    physical_signs: str | None
    diagnosis: str | None
    syndrome_differentiation: str | None
    treatment_plan: str | None
    prescription: str | None
    acupuncture_points: list[str] | None = None
    notes: str | None
    created_at: datetime.datetime
    updated_at: datetime.datetime

    @field_validator("treatment_types", mode="before")
    @classmethod
    def parse_treatment_types(cls, v):
        if isinstance(v, str):
            try:
                return json.loads(v)
            except Exception:
                return []
        return v or []

    @field_validator("acupuncture_points", mode="before")
    @classmethod
    def parse_acupuncture_points(cls, v):
        if isinstance(v, str):
            try:
                return json.loads(v)
            except Exception:
                return []
        return v