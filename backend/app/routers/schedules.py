from fastapi import APIRouter, Depends

from app.crud import schedule as crud
from app.dependencies import DbSession, get_current_doctor
from app.schemas.schedule import (
    ScheduleOverrideCreate,
    ScheduleOverrideResponse,
    ScheduleResponse,
    ScheduleUpdate,
)

router = APIRouter(prefix="/api/v1", tags=["排班"])


@router.get("/schedules", response_model=list[ScheduleResponse], summary="查看排班设置")
def get_schedules(db: DbSession, _=Depends(get_current_doctor)):
    return crud.get_schedules(db)


@router.put("/schedules", response_model=ScheduleResponse, summary="更新单条排班 [需JWT]")
def upsert_schedule(schema: ScheduleUpdate, db: DbSession, _=Depends(get_current_doctor)):
    return crud.upsert_schedule(db, schema)


@router.get("/schedule-overrides", response_model=list[ScheduleOverrideResponse], summary="查看临时调整")
def get_overrides(db: DbSession, _=Depends(get_current_doctor)):
    return crud.get_overrides(db)


@router.post("/schedule-overrides", response_model=ScheduleOverrideResponse, summary="添加临时调整 [需JWT]")
def create_override(schema: ScheduleOverrideCreate, db: DbSession, _=Depends(get_current_doctor)):
    return crud.create_override(db, schema)


@router.delete("/schedule-overrides/{override_id}", summary="删除临时调整 [需JWT]")
def delete_override(override_id: int, db: DbSession, _=Depends(get_current_doctor)):
    ok = crud.delete_override(db, override_id)
    if not ok:
        from app.exceptions import NotFoundError
        raise NotFoundError("临时调整不存在")
    return {"message": "删除成功"}