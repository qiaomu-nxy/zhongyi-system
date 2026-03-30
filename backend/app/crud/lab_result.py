from sqlalchemy.orm import Session

from app.models.lab_result import LabResult
from app.schemas.lab_result import LabResultCreate, LabResultUpdate


def create_lab_result(db: Session, visit_id: int, patient_id: int, schema: LabResultCreate) -> LabResult:
    r = LabResult(visit_id=visit_id, patient_id=patient_id, **schema.model_dump())
    db.add(r)
    db.commit()
    db.refresh(r)
    return r


def get_lab_results_by_visit(db: Session, visit_id: int) -> list[LabResult]:
    return db.query(LabResult).filter(LabResult.visit_id == visit_id).all()


def get_lab_results_by_patient(db: Session, patient_id: int) -> list[LabResult]:
    return (
        db.query(LabResult)
        .filter(LabResult.patient_id == patient_id)
        .order_by(LabResult.created_at.desc())
        .all()
    )


def update_lab_result(db: Session, result_id: int, schema: LabResultUpdate) -> LabResult | None:
    r = db.get(LabResult, result_id)
    if not r:
        return None
    for k, v in schema.model_dump(exclude_none=True).items():
        setattr(r, k, v)
    db.commit()
    db.refresh(r)
    return r