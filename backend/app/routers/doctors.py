from fastapi import APIRouter, Depends
from pydantic import BaseModel, Field

from app.crud import doctor as crud
from app.dependencies import DbSession, get_current_admin
from app.exceptions import NotFoundError
from app.schemas.doctor import DoctorResponse

router = APIRouter(prefix="/api/v1/doctors", tags=["医师管理"])


class PasswordResetBody(BaseModel):
    new_password: str = Field(min_length=6)


@router.put("/{doctor_id}/reset-password", response_model=DoctorResponse, summary="重置医师密码 [admin]")
def reset_password(
    doctor_id: int,
    body: PasswordResetBody,
    db: DbSession,
    _=Depends(get_current_admin),
):
    doctor = crud.reset_password(db, doctor_id, body.new_password)
    if not doctor:
        raise NotFoundError("医师不存在")
    return doctor