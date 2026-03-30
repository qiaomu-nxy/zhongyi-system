from fastapi import APIRouter, Depends

from app.crud import medical_record as crud
from app.dependencies import DbSession, get_current_admin, get_current_doctor
from app.exceptions import ForbiddenError, NotFoundError
from app.schemas.medical_record import (
    MedicalRecordCreate,
    MedicalRecordResponse,
    MedicalRecordUpdate,
)

router = APIRouter(tags=["病历"])


@router.post("/api/v1/visits/{visit_id}/medical-record", response_model=MedicalRecordResponse, summary="创建病历 [需JWT]")
def create_medical_record(
    visit_id: int,
    schema: MedicalRecordCreate,
    db: DbSession,
    doctor=Depends(get_current_doctor),
):
    return crud.create_medical_record(db, visit_id, schema, doctor.id)


@router.get("/api/v1/visits/{visit_id}/medical-record", response_model=MedicalRecordResponse, summary="查看病历")
def get_medical_record(visit_id: int, db: DbSession):
    record = crud.get_medical_record(db, visit_id)
    if not record:
        raise NotFoundError("病历不存在")
    return record


@router.put("/api/v1/medical-records/{record_id}", response_model=MedicalRecordResponse, summary="更新病历 [仅admin]")
def update_medical_record(
    record_id: int,
    schema: MedicalRecordUpdate,
    db: DbSession,
    _=Depends(get_current_admin),
):
    return crud.update_medical_record(db, record_id, schema)