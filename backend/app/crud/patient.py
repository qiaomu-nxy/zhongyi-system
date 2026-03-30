import json

from sqlalchemy.orm import Session

from app.exceptions import BusinessError, NotFoundError
from app.models.patient import Patient
from app.schemas.patient import PatientCreate, PatientUpdate


def _serialize(data: dict) -> dict:
    if "medical_history" in data and isinstance(data["medical_history"], list):
        data["medical_history"] = json.dumps(data["medical_history"], ensure_ascii=False)
    return data


def create_patient(db: Session, schema: PatientCreate) -> Patient:
    data = _serialize(schema.model_dump())
    patient = Patient(**data)
    db.add(patient)
    db.commit()
    db.refresh(patient)
    return patient


def get_patient(db: Session, patient_id: int) -> Patient | None:
    return db.get(Patient, patient_id)


def get_by_phone_and_name(db: Session, phone: str, name: str) -> Patient | None:
    return (
        db.query(Patient)
        .filter(Patient.phone == phone, Patient.name == name, Patient.is_active.is_(True))
        .first()
    )


def get_patients(
    db: Session, skip: int = 0, limit: int = 20, search: str | None = None
) -> list[Patient]:
    q = db.query(Patient).filter(Patient.is_active.is_(True))
    if search:
        like = f"%{search}%"
        q = q.filter(Patient.name.like(like) | Patient.phone.like(like))
    return q.order_by(Patient.created_at.desc()).offset(skip).limit(limit).all()


def update_patient(db: Session, patient_id: int, schema: PatientUpdate) -> Patient | None:
    patient = db.get(Patient, patient_id)
    if not patient:
        return None
    data = _serialize(schema.model_dump(exclude_none=True))
    for k, v in data.items():
        setattr(patient, k, v)
    db.commit()
    db.refresh(patient)
    return patient


def merge_patients(db: Session, keep_id: int, remove_id: int) -> Patient:
    """合并重复患者档案（仅 admin 可用）。"""
    keep = db.get(Patient, keep_id)
    remove = db.get(Patient, remove_id)
    if not keep or not remove:
        raise NotFoundError("患者不存在")
    if keep_id == remove_id:
        raise BusinessError("不能合并相同患者")

    from app.models.visit import Visit
    from app.models.appointment import Appointment

    db.query(Visit).filter(Visit.patient_id == remove_id).update({"patient_id": keep_id})
    db.query(Appointment).filter(Appointment.patient_id == remove_id).update({"patient_id": keep_id})
    remove.is_active = False
    db.commit()
    db.refresh(keep)
    return keep