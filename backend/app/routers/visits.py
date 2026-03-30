import datetime

from fastapi import APIRouter, Depends, Query

from app.crud import visit as crud
from app.dependencies import DbSession, get_current_doctor
from app.exceptions import NotFoundError
from app.schemas.visit import VisitCreate, VisitResponse, VisitUpdate

router = APIRouter(prefix="/api/v1/visits", tags=["就诊记录"])


# /today 必须在 /{id} 之前注册
@router.get("/today", summary="今日就诊列表与统计 [需JWT]")
def today_visits(db: DbSession, _=Depends(get_current_doctor)):
    summary = crud.get_today_summary(db)
    return {
        **{k: v for k, v in summary.items() if k != "visits"},
        "visits": [VisitResponse.model_validate(v) for v in summary["visits"]],
    }


@router.post("", response_model=VisitResponse, summary="创建就诊记录")
def create_visit(schema: VisitCreate, db: DbSession):
    return crud.create_visit(db, schema)


@router.get("", response_model=list[VisitResponse], summary="就诊列表 [需JWT]")
def list_visits(
    db: DbSession,
    patient_id: int | None = Query(None),
    date: datetime.date | None = Query(None),
    status: str | None = Query(None),
    skip: int = 0,
    limit: int = 20,
    _=Depends(get_current_doctor),
):
    return crud.get_visits(db, skip=skip, limit=limit, patient_id=patient_id, date=date, status=status)


@router.get("/{visit_id}", response_model=VisitResponse, summary="就诊详情")
def get_visit(visit_id: int, db: DbSession):
    v = crud.get_visit(db, visit_id)
    if not v:
        raise NotFoundError("就诊记录不存在")
    return v


@router.put("/{visit_id}/check-in", response_model=VisitResponse, summary="患者到店签到")
def check_in(visit_id: int, db: DbSession):
    return crud.check_in(db, visit_id)


@router.put("/{visit_id}/status", response_model=VisitResponse, summary="更新就诊状态 [需JWT]")
def update_status(visit_id: int, schema: VisitUpdate, db: DbSession, _=Depends(get_current_doctor)):
    return crud.update_status(db, visit_id, schema)