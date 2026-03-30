from sqlalchemy.orm import Session

from app.models.patient_history import PatientHistory
from app.schemas.patient_history import PatientHistoryCreate, PatientHistoryUpdate


def create_history(db: Session, schema: PatientHistoryCreate) -> PatientHistory:
    h = PatientHistory(**schema.model_dump())
    db.add(h)
    db.commit()
    db.refresh(h)
    return h


def get_histories(db: Session, patient_id: int) -> list[PatientHistory]:
    return (
        db.query(PatientHistory)
        .filter(PatientHistory.patient_id == patient_id)
        .order_by(PatientHistory.created_at.desc())
        .all()
    )


def update_history(db: Session, history_id: int, schema: PatientHistoryUpdate) -> PatientHistory | None:
    h = db.get(PatientHistory, history_id)
    if not h:
        return None
    for k, v in schema.model_dump(exclude_none=True).items():
        setattr(h, k, v)
    db.commit()
    db.refresh(h)
    return h