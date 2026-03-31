import datetime

from sqlalchemy.orm import Session

from app.crud.schedule import generate_slots, get_effective_schedule
from app.exceptions import BusinessError, NotFoundError
from app.models.appointment import Appointment
from app.schemas.appointment import AppointmentCreate


def get_available_slots(db: Session, date: datetime.date) -> list[dict]:
    sched = get_effective_schedule(db, date)
    all_slots = generate_slots(sched)
    if not all_slots:
        return []

    booked = {
        a.time_slot
        for a in db.query(Appointment).filter(
            Appointment.appointment_date == date,
            Appointment.status == "待就诊",
        )
    }

    cutoff: str | None = None
    if date == datetime.date.today():
        t = datetime.datetime.now() + datetime.timedelta(hours=1)
        cutoff = f"{t.hour:02d}:{t.minute:02d}"

    return [
        {
            "time_slot": slot,
            "available": slot not in booked and (cutoff is None or slot > cutoff),
        }
        for slot in all_slots
    ]


def create_appointment(db: Session, schema: AppointmentCreate) -> Appointment:
    # 同一患者同一天只能有一个待就诊预约
    existing = db.query(Appointment).filter(
        Appointment.patient_id == schema.patient_id,
        Appointment.appointment_date == schema.appointment_date,
        Appointment.status == "待就诊",
    ).first()
    if existing:
        raise BusinessError(f"您已预约当日 {existing.time_slot} 时段，请勿重复预约")

    slots = get_available_slots(db, schema.appointment_date)
    info = next((s for s in slots if s["time_slot"] == schema.time_slot), None)
    if not info or not info["available"]:
        raise BusinessError("该时段已约满或不可预约")
    apt = Appointment(
        patient_id=schema.patient_id,
        appointment_date=schema.appointment_date,
        time_slot=schema.time_slot,
    )
    db.add(apt)
    db.commit()
    db.refresh(apt)
    return apt


def get_appointments(
    db: Session,
    skip: int = 0,
    limit: int = 50,
    date: datetime.date | None = None,
    status: str | None = None,
    patient_id: int | None = None,
) -> list[Appointment]:
    q = db.query(Appointment)
    if date:
        q = q.filter(Appointment.appointment_date == date)
    if status:
        q = q.filter(Appointment.status == status)
    if patient_id:
        q = q.filter(Appointment.patient_id == patient_id)
    return q.order_by(Appointment.appointment_date, Appointment.time_slot).offset(skip).limit(limit).all()


def cancel_by_patient(db: Session, apt_id: int, reason: str | None = None) -> Appointment:
    apt = db.get(Appointment, apt_id)
    if not apt:
        raise NotFoundError("预约记录不存在")
    if apt.status != "待就诊":
        raise BusinessError(f"当前状态「{apt.status}」，无法取消")
    # 预约时间前2小时内不可取消
    apt_dt = datetime.datetime.combine(apt.appointment_date, datetime.time(*map(int, apt.time_slot.split(":"))))
    if datetime.datetime.now() >= apt_dt - datetime.timedelta(hours=2):
        raise BusinessError("距就诊时间不足2小时，无法取消")
    apt.status = "已取消"
    apt.cancel_reason = reason
    db.commit()
    db.refresh(apt)
    return apt


def cancel_by_doctor(db: Session, apt_id: int, reason: str | None = None) -> Appointment:
    apt = db.get(Appointment, apt_id)
    if not apt:
        raise NotFoundError("预约记录不存在")
    if apt.status != "待就诊":
        raise BusinessError(f"当前状态「{apt.status}」，无法取消")
    apt.status = "已取消"
    apt.cancel_reason = reason
    db.commit()
    db.refresh(apt)
    return apt


def mark_no_show(db: Session, apt_id: int) -> Appointment:
    apt = db.get(Appointment, apt_id)
    if not apt:
        raise NotFoundError("预约记录不存在")
    if apt.status != "待就诊":
        raise BusinessError(f"当前状态「{apt.status}」，无法标记爽约")
    apt.status = "爽约"
    db.commit()
    db.refresh(apt)
    return apt