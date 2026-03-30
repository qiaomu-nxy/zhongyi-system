import datetime
from dataclasses import dataclass

from sqlalchemy.orm import Session

from app.models.schedule import Schedule
from app.models.schedule_override import ScheduleOverride
from app.schemas.schedule import ScheduleOverrideCreate, ScheduleUpdate


@dataclass
class EffectiveSchedule:
    is_working: bool
    morning_start: str | None
    morning_end: str | None
    afternoon_start: str | None
    afternoon_end: str | None
    slot_duration: int = 30


def get_effective_schedule(db: Session, date: datetime.date) -> EffectiveSchedule | None:
    override = (
        db.query(ScheduleOverride)
        .filter(ScheduleOverride.override_date == date)
        .first()
    )
    if override is not None:
        if not override.is_working:
            return None
        return EffectiveSchedule(
            is_working=True,
            morning_start=override.morning_start,
            morning_end=override.morning_end,
            afternoon_start=override.afternoon_start,
            afternoon_end=override.afternoon_end,
        )

    sched = db.query(Schedule).filter(Schedule.weekday == date.weekday()).first()
    if not sched or not sched.is_working:
        return None
    return EffectiveSchedule(
        is_working=True,
        morning_start=sched.morning_start,
        morning_end=sched.morning_end,
        afternoon_start=sched.afternoon_start,
        afternoon_end=sched.afternoon_end,
        slot_duration=sched.slot_duration,
    )


def generate_slots(sched: EffectiveSchedule | None) -> list[str]:
    if not sched or not sched.is_working:
        return []
    slots: list[str] = []

    def _add(start: str | None, end: str | None) -> None:
        if not start or not end:
            return
        cur = sum(int(x) * m for x, m in zip(start.split(":"), [60, 1]))
        fin = sum(int(x) * m for x, m in zip(end.split(":"), [60, 1]))
        while cur < fin:
            h, m = divmod(cur, 60)
            slots.append(f"{h:02d}:{m:02d}")
            cur += sched.slot_duration

    _add(sched.morning_start, sched.morning_end)
    _add(sched.afternoon_start, sched.afternoon_end)
    return slots


def get_schedules(db: Session) -> list[Schedule]:
    return db.query(Schedule).order_by(Schedule.weekday).all()


def upsert_schedule(db: Session, schema: ScheduleUpdate) -> Schedule:
    sched = db.query(Schedule).filter(Schedule.weekday == schema.weekday).first()
    if sched:
        for k, v in schema.model_dump().items():
            setattr(sched, k, v)
    else:
        sched = Schedule(**schema.model_dump())
        db.add(sched)
    db.commit()
    db.refresh(sched)
    return sched


def get_overrides(db: Session) -> list[ScheduleOverride]:
    return (
        db.query(ScheduleOverride)
        .order_by(ScheduleOverride.override_date)
        .all()
    )


def create_override(db: Session, schema: ScheduleOverrideCreate) -> ScheduleOverride:
    existing = (
        db.query(ScheduleOverride)
        .filter(ScheduleOverride.override_date == schema.override_date)
        .first()
    )
    if existing:
        for k, v in schema.model_dump().items():
            setattr(existing, k, v)
        db.commit()
        db.refresh(existing)
        return existing
    o = ScheduleOverride(**schema.model_dump())
    db.add(o)
    db.commit()
    db.refresh(o)
    return o


def delete_override(db: Session, override_id: int) -> bool:
    o = db.get(ScheduleOverride, override_id)
    if not o:
        return False
    db.delete(o)
    db.commit()
    return True