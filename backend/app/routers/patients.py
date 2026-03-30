from fastapi import APIRouter, Depends, Query
from pydantic import BaseModel

from app.crud import patient as crud
from app.crud import patient_history as hist_crud
from app.dependencies import DbSession, get_current_admin, get_current_doctor
from app.exceptions import NotFoundError
from app.schemas.patient import PatientCreate, PatientResponse, PatientUpdate
from app.schemas.patient_history import (
    PatientHistoryCreate,
    PatientHistoryResponse,
    PatientHistoryUpdate,
)

router = APIRouter(prefix="/api/v1/patients", tags=["患者"])


class MergeRequest(BaseModel):
    keep_id: int
    remove_id: int


# 注意：/merge 必须在 /{patient_id} 之前注册，避免路由冲突
@router.put("/merge", summary="合并患者档案 [admin]")
def merge_patients(body: MergeRequest, db: DbSession, _=Depends(get_current_admin)):
    patient = crud.merge_patients(db, body.keep_id, body.remove_id)
    return {"message": "合并成功", "patient_id": patient.id}


@router.post("", response_model=PatientResponse, summary="创建患者（患者自填或医师代填）")
def create_patient(schema: PatientCreate, db: DbSession):
    existing = crud.get_by_phone_and_name(db, schema.phone, schema.name)
    if existing:
        return existing
    return crud.create_patient(db, schema)


@router.get("", response_model=list[PatientResponse], summary="患者列表 [需JWT]")
def list_patients(
    db: DbSession,
    search: str | None = Query(None, description="姓名或手机号搜索"),
    skip: int = 0,
    limit: int = 20,
    _=Depends(get_current_doctor),
):
    return crud.get_patients(db, skip=skip, limit=limit, search=search)


@router.get("/{patient_id}", response_model=PatientResponse, summary="患者详情")
def get_patient(patient_id: int, db: DbSession):
    p = crud.get_patient(db, patient_id)
    if not p:
        raise NotFoundError("患者不存在")
    return p


@router.put("/{patient_id}", response_model=PatientResponse, summary="更新患者信息")
def update_patient(patient_id: int, schema: PatientUpdate, db: DbSession):
    p = crud.update_patient(db, patient_id, schema)
    if not p:
        raise NotFoundError("患者不存在")
    return p


@router.post("/{patient_id}/history", response_model=PatientHistoryResponse, summary="添加既往史 [需JWT]")
def add_history(
    patient_id: int,
    schema: PatientHistoryCreate,
    db: DbSession,
    _=Depends(get_current_doctor),
):
    schema.patient_id = patient_id
    return hist_crud.create_history(db, schema)


@router.get("/{patient_id}/history", response_model=list[PatientHistoryResponse], summary="查看既往史")
def get_history(patient_id: int, db: DbSession):
    return hist_crud.get_histories(db, patient_id)