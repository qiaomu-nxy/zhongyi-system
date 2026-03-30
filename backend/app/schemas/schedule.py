import datetime
from pydantic import BaseModel, ConfigDict, Field


class ScheduleUpdate(BaseModel):
    """按 weekday 批量更新排班，不支持单独 Create（初始化时全量写入）"""
    weekday: int = Field(ge=0, le=6)
    is_working: bool
    morning_start: str | None = None
    morning_end: str | None = None
    afternoon_start: str | None = None
    afternoon_end: str | None = None
    slot_duration: int = Field(default=30, ge=15, le=120)


class ScheduleResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    doctor_id: int | None
    weekday: int
    is_working: bool
    morning_start: str | None
    morning_end: str | None
    afternoon_start: str | None
    afternoon_end: str | None
    slot_duration: int
    created_at: datetime.datetime


class ScheduleOverrideCreate(BaseModel):
    override_date: datetime.date
    is_working: bool
    morning_start: str | None = None
    morning_end: str | None = None
    afternoon_start: str | None = None
    afternoon_end: str | None = None
    reason: str | None = Field(None, max_length=200)


class ScheduleOverrideResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    doctor_id: int | None
    override_date: datetime.date
    is_working: bool
    morning_start: str | None
    morning_end: str | None
    afternoon_start: str | None
    afternoon_end: str | None
    reason: str | None
    created_at: datetime.datetime