import logging
from typing import Annotated

from fastapi import Depends, Header
from sqlalchemy.orm import Session

from app.auth_utils import decode_token
from app.database import SessionLocal
from app.exceptions import AuthError, ForbiddenError

logger = logging.getLogger(__name__)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


DbSession = Annotated[Session, Depends(get_db)]


def get_current_doctor(
    authorization: Annotated[str | None, Header()] = None,
    db: Session = Depends(get_db),
):
    if not authorization or not authorization.startswith("Bearer "):
        raise AuthError("请先登录")
    token = authorization.removeprefix("Bearer ").strip()
    try:
        payload = decode_token(token)
    except ValueError:
        raise AuthError("Token 无效或已过期")

    doctor_id = payload.get("sub")
    if not doctor_id:
        raise AuthError("Token 无效")

    from app.models.doctor import Doctor

    doctor = db.get(Doctor, int(doctor_id))
    if not doctor or not doctor.is_active:
        raise AuthError("账号不存在或已禁用")
    return doctor


def get_current_admin(doctor=Depends(get_current_doctor)):
    if doctor.role != "admin":
        raise ForbiddenError("仅管理员可操作")
    return doctor