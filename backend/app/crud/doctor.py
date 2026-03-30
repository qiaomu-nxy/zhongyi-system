from sqlalchemy.orm import Session

from app.auth_utils import hash_password
from app.models.doctor import Doctor
from app.schemas.doctor import DoctorCreate, DoctorUpdate


def create_doctor(db: Session, schema: DoctorCreate) -> Doctor:
    doctor = Doctor(
        username=schema.username,
        password_hash=hash_password(schema.password),
        name=schema.name,
        role=schema.role,
    )
    db.add(doctor)
    db.commit()
    db.refresh(doctor)
    return doctor


def get_doctor(db: Session, doctor_id: int) -> Doctor | None:
    return db.get(Doctor, doctor_id)


def get_doctor_by_username(db: Session, username: str) -> Doctor | None:
    return db.query(Doctor).filter(Doctor.username == username).first()


def get_doctors(db: Session) -> list[Doctor]:
    return db.query(Doctor).filter(Doctor.is_active.is_(True)).all()


def update_doctor(db: Session, doctor_id: int, schema: DoctorUpdate) -> Doctor | None:
    doctor = db.get(Doctor, doctor_id)
    if not doctor:
        return None
    for k, v in schema.model_dump(exclude_none=True).items():
        setattr(doctor, k, v)
    db.commit()
    db.refresh(doctor)
    return doctor


def reset_password(db: Session, doctor_id: int, new_password: str) -> Doctor | None:
    doctor = db.get(Doctor, doctor_id)
    if not doctor:
        return None
    doctor.password_hash = hash_password(new_password)
    db.commit()
    db.refresh(doctor)
    return doctor