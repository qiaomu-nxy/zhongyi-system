import datetime

from sqlalchemy.orm import Session

from app.exceptions import BusinessError, NotFoundError
from app.models.visit import Visit
from app.schemas.visit import VisitCreate, VisitUpdate


def create_visit(db: Session, schema: VisitCreate) -> Visit:
    existing = (
        db.query(Visit)
        .filter(
            Visit.patient_id == schema.patient_id,
            Visit.visit_date == schema.visit_date,
            Visit.status != "已作废",
        )
        .first()
    )
    if existing:
        raise BusinessError("该患者今日已有就诊记录")

    visit_number = (
        db.query(Visit)
        .filter(Visit.patient_id == schema.patient_id, Visit.status != "已作废")
        .count()
        + 1
    )

    visit = Visit(
        patient_id=schema.patient_id,
        visit_date=schema.visit_date,
        visit_number=visit_number,
        chief_complaint=schema.chief_complaint,
        status="待签到",
    )
    db.add(visit)
    db.commit()
    db.refresh(visit)
    return visit


def get_visit(db: Session, visit_id: int) -> Visit | None:
    return db.get(Visit, visit_id)


def get_visits(
    db: Session,
    skip: int = 0,
    limit: int = 20,
    patient_id: int | None = None,
    date: datetime.date | None = None,
    status: str | None = None,
) -> list[Visit]:
    q = db.query(Visit)
    if patient_id:
        q = q.filter(Visit.patient_id == patient_id)
    if date:
        q = q.filter(Visit.visit_date == date)
    if status:
        q = q.filter(Visit.status == status)
    return q.order_by(Visit.created_at.desc()).offset(skip).limit(limit).all()


def get_today_summary(db: Session) -> dict:
    today = datetime.date.today()
    visits = db.query(Visit).filter(Visit.visit_date == today).all()
    return {
        "visits": visits,
        "total": len(visits),
        "waiting": sum(1 for v in visits if v.status == "待接诊"),
        "completed": sum(1 for v in visits if v.status == "已完成"),
        "new_patients": sum(1 for v in visits if v.visit_number == 1),
        "return_patients": sum(1 for v in visits if v.visit_number > 1),
    }


def check_in(db: Session, visit_id: int) -> Visit:
    visit = db.get(Visit, visit_id)
    if not visit:
        raise NotFoundError("就诊记录不存在")
    if visit.status != "待签到":
        raise BusinessError(f"当前状态为「{visit.status}」，无法签到")
    visit.status = "待接诊"
    db.commit()
    db.refresh(visit)
    return visit


def update_status(db: Session, visit_id: int, schema: VisitUpdate) -> Visit:
    visit = db.get(Visit, visit_id)
    if not visit:
        raise NotFoundError("就诊记录不存在")
    if schema.status:
        visit.status = schema.status
    if schema.chief_complaint is not None:
        visit.chief_complaint = schema.chief_complaint
    db.commit()
    db.refresh(visit)
    return visit