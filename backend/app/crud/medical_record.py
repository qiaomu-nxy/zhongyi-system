import json

from sqlalchemy.orm import Session

from app.exceptions import BusinessError, NotFoundError
from app.models.appointment import Appointment
from app.models.medical_record import MedicalRecord
from app.models.visit import Visit
from app.schemas.medical_record import MedicalRecordCreate, MedicalRecordUpdate


def _pack(data: dict) -> dict:
    if "treatment_types" in data and isinstance(data["treatment_types"], list):
        data["treatment_types"] = json.dumps(data["treatment_types"], ensure_ascii=False)
    if "acupuncture_points" in data and isinstance(data["acupuncture_points"], list):
        data["acupuncture_points"] = json.dumps(data["acupuncture_points"], ensure_ascii=False)
    return data


def create_medical_record(
    db: Session, visit_id: int, schema: MedicalRecordCreate, doctor_id: int
) -> MedicalRecord:
    visit = db.get(Visit, visit_id)
    if not visit:
        raise NotFoundError("就诊记录不存在")
    if db.query(MedicalRecord).filter(MedicalRecord.visit_id == visit_id).first():
        raise BusinessError("该就诊记录已有病历，如需修改请联系管理员")

    data = _pack(schema.model_dump())
    record = MedicalRecord(visit_id=visit_id, doctor_id=doctor_id, **data)
    db.add(record)

    # 自动完成就诊状态
    visit.status = "已完成"

    # 自动完成关联预约
    apt = (
        db.query(Appointment)
        .filter(
            Appointment.patient_id == visit.patient_id,
            Appointment.appointment_date == visit.visit_date,
            Appointment.status == "待就诊",
        )
        .first()
    )
    if apt:
        apt.status = "已完成"

    db.commit()
    db.refresh(record)
    return record


def update_medical_record(
    db: Session, record_id: int, schema: MedicalRecordUpdate
) -> MedicalRecord:
    record = db.get(MedicalRecord, record_id)
    if not record:
        raise NotFoundError("病历不存在")
    data = _pack(schema.model_dump(exclude_none=True))
    for k, v in data.items():
        setattr(record, k, v)
    db.commit()
    db.refresh(record)
    return record


def get_medical_record(db: Session, visit_id: int) -> MedicalRecord | None:
    return db.query(MedicalRecord).filter(MedicalRecord.visit_id == visit_id).first()