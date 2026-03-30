import datetime

from sqlalchemy.orm import Session

from app.exceptions import BusinessError, NotFoundError
from app.models.symptom import SymptomRecord
from app.models.visit import Visit
from app.schemas.symptom import SymptomRecordCreate


def create_symptoms_batch(
    db: Session, visit_id: int, schemas: list[SymptomRecordCreate]
) -> list[SymptomRecord]:
    visit = db.get(Visit, visit_id)
    if not visit:
        raise NotFoundError("就诊记录不存在")
    if visit.visit_date != datetime.date.today():
        raise BusinessError("只能在就诊当天提交症状")

    records = [SymptomRecord(visit_id=visit_id, **s.model_dump()) for s in schemas]
    for r in records:
        db.add(r)

    visit.symptom_submitted_at = datetime.datetime.utcnow()
    db.commit()
    for r in records:
        db.refresh(r)
    return records


def get_symptoms(db: Session, visit_id: int) -> list[SymptomRecord]:
    return (
        db.query(SymptomRecord)
        .filter(SymptomRecord.visit_id == visit_id)
        .order_by(SymptomRecord.body_part)
        .all()
    )