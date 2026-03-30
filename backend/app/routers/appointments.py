import datetime

from fastapi import APIRouter, Depends, Query

from app.crud import appointment as crud
from app.dependencies import DbSession, get_current_doctor
from app.schemas.appointment import (
    AppointmentCancelRequest,
    AppointmentCreate,
    AppointmentResponse,
)

router = APIRouter(prefix="/api/v1/appointments", tags=["预约"])


# /available-slots 必须在 /{id} 之前
@router.get("/available-slots", summary="可预约时段")
def available_slots(
    date: datetime.date = Query(..., description="查询日期 YYYY-MM-DD"),
    db: DbSession = None,
):
    return crud.get_available_slots(db, date)


@router.post("", response_model=AppointmentResponse, summary="患者创建预约")
def create_appointment(schema: AppointmentCreate, db: DbSession):
    return crud.create_appointment(db, schema)


@router.get("", response_model=list[AppointmentResponse], summary="预约列表 [需JWT]")
def list_appointments(
    db: DbSession,
    date: datetime.date | None = Query(None),
    status: str | None = Query(None),
    skip: int = 0,
    limit: int = 50,
    _=Depends(get_current_doctor),
):
    return crud.get_appointments(db, skip=skip, limit=limit, date=date, status=status)


@router.get("/patient/{patient_id}", response_model=list[AppointmentResponse], summary="患者自己的预约记录")
def patient_appointments(patient_id: int, db: DbSession):
    return crud.get_appointments(db, patient_id=patient_id)


@router.put("/{apt_id}/cancel", response_model=AppointmentResponse, summary="取消预约")
def cancel_appointment(
    apt_id: int,
    body: AppointmentCancelRequest,
    db: DbSession,
    doctor=Depends(get_current_doctor) if False else None,
):
    # 路由层无法区分患者/医师，由业务层决定；此端点供双方调用
    # 医师端调用时需携带 JWT，患者端直接调用（在 router 中统一走患者逻辑）
    return crud.cancel_by_patient(db, apt_id, body.cancel_reason)


@router.put("/{apt_id}/cancel-doctor", response_model=AppointmentResponse, summary="医师取消预约 [需JWT]")
def cancel_by_doctor(
    apt_id: int,
    body: AppointmentCancelRequest,
    db: DbSession,
    _=Depends(get_current_doctor),
):
    return crud.cancel_by_doctor(db, apt_id, body.cancel_reason)


@router.put("/{apt_id}/no-show", response_model=AppointmentResponse, summary="标记爽约 [需JWT]")
def mark_no_show(apt_id: int, db: DbSession, _=Depends(get_current_doctor)):
    return crud.mark_no_show(db, apt_id)