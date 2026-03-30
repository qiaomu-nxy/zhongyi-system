from fastapi import APIRouter

from app.crud import symptom as crud
from app.dependencies import DbSession
from app.schemas.symptom import SymptomRecordCreate, SymptomRecordResponse

router = APIRouter(prefix="/api/v1/visits", tags=["症状"])


@router.post("/{visit_id}/symptoms", response_model=list[SymptomRecordResponse], summary="批量提交症状（仅限当天）")
def submit_symptoms(visit_id: int, schemas: list[SymptomRecordCreate], db: DbSession):
    return crud.create_symptoms_batch(db, visit_id, schemas)


@router.get("/{visit_id}/symptoms", response_model=list[SymptomRecordResponse], summary="查看症状列表")
def get_symptoms(visit_id: int, db: DbSession):
    return crud.get_symptoms(db, visit_id)