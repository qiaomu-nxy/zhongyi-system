from fastapi import APIRouter, Depends

from app.crud import lab_result as crud
from app.crud import visit as visit_crud
from app.dependencies import DbSession, get_current_doctor
from app.exceptions import NotFoundError
from app.schemas.lab_result import LabResultCreate, LabResultResponse

router = APIRouter(tags=["检验指标"])


@router.post("/api/v1/visits/{visit_id}/lab-results", response_model=LabResultResponse, summary="添加检验指标 [需JWT]")
def add_lab_result(
    visit_id: int,
    schema: LabResultCreate,
    db: DbSession,
    _=Depends(get_current_doctor),
):
    visit = visit_crud.get_visit(db, visit_id)
    if not visit:
        raise NotFoundError("就诊记录不存在")
    return crud.create_lab_result(db, visit_id, visit.patient_id, schema)


@router.get("/api/v1/patients/{patient_id}/lab-results", response_model=list[LabResultResponse], summary="患者所有检验指标")
def get_patient_lab_results(patient_id: int, db: DbSession):
    return crud.get_lab_results_by_patient(db, patient_id)