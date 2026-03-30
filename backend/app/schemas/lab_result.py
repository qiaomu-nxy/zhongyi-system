import datetime
from pydantic import BaseModel, ConfigDict, Field


class LabResultCreate(BaseModel):
    indicator_name: str = Field(min_length=1, max_length=100)
    value: str = Field(min_length=1, max_length=50)
    unit: str | None = Field(None, max_length=50)
    reference_range: str | None = Field(None, max_length=100)
    is_abnormal: bool = False


class LabResultUpdate(BaseModel):
    indicator_name: str | None = Field(None, max_length=100)
    value: str | None = Field(None, max_length=50)
    unit: str | None = Field(None, max_length=50)
    reference_range: str | None = Field(None, max_length=100)
    is_abnormal: bool | None = None


class LabResultResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    visit_id: int
    patient_id: int
    indicator_name: str
    value: str
    unit: str | None
    reference_range: str | None
    is_abnormal: bool
    created_at: datetime.datetime