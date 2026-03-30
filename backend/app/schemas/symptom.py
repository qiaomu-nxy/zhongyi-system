import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

BodyPart = Literal[
    "头部", "面部", "颈部", "肩部", "胸部", "腹部",
    "腰部", "背部", "上肢", "下肢", "足部", "全身",
]


class SymptomRecordCreate(BaseModel):
    body_part: BodyPart
    symptom_name: str = Field(min_length=1, max_length=100)
    severity: int = Field(ge=1, le=10)
    duration: str | None = Field(None, max_length=50)
    location_detail: str | None = Field(None, max_length=50)
    description: str | None = None


class SymptomRecordResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    visit_id: int
    body_part: str
    symptom_name: str
    severity: int
    duration: str | None
    location_detail: str | None
    description: str | None
    created_at: datetime.datetime