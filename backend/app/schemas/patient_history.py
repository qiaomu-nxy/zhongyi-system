import datetime
from pydantic import BaseModel, ConfigDict, Field


class PatientHistoryCreate(BaseModel):
    patient_id: int
    condition_name: str = Field(min_length=1, max_length=100)
    treatment_institution: str | None = Field(None, max_length=200)
    treatment_method: str | None = Field(None, max_length=200)
    treatment_duration: str | None = Field(None, max_length=100)
    treatment_effect: str | None = None


class PatientHistoryUpdate(BaseModel):
    condition_name: str | None = Field(None, max_length=100)
    treatment_institution: str | None = Field(None, max_length=200)
    treatment_method: str | None = Field(None, max_length=200)
    treatment_duration: str | None = Field(None, max_length=100)
    treatment_effect: str | None = None


class PatientHistoryResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    patient_id: int
    condition_name: str
    treatment_institution: str | None
    treatment_method: str | None
    treatment_duration: str | None
    treatment_effect: str | None
    created_at: datetime.datetime