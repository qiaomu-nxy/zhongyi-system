import logging

from fastapi import APIRouter, Depends
from pydantic import BaseModel, field_validator
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.auth_utils import create_access_token, verify_password
from app.dependencies import get_db
from app.exceptions import AuthError, BusinessError
from app.models.doctor import Doctor
from app.models.patient import Patient

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/v1/auth", tags=["认证"])


class DoctorLoginRequest(BaseModel):
    username: str
    password: str


class PatientLoginRequest(BaseModel):
    phone: str
    name: str

    @field_validator("phone")
    @classmethod
    def phone_must_be_11_digits(cls, v: str) -> str:
        if not v.isdigit() or len(v) != 11:
            raise ValueError("手机号必须为11位数字")
        return v


@router.post("/doctor/login", summary="医师账号密码登录")
def doctor_login(form: DoctorLoginRequest, db: Session = Depends(get_db)):
    doctor = (
        db.query(Doctor)
        .filter(Doctor.username == form.username, Doctor.is_active.is_(True))
        .first()
    )
    if not doctor or not verify_password(form.password, doctor.password_hash):
        raise AuthError("账号或密码错误")
    token = create_access_token({"sub": str(doctor.id), "role": doctor.role})
    logger.info("医师登录成功: %s (role=%s)", doctor.username, doctor.role)
    return {
        "access_token": token,
        "token_type": "bearer",
        "doctor": {
            "id": doctor.id,
            "username": doctor.username,
            "name": doctor.name,
            "role": doctor.role,
        },
    }


@router.post("/patient/login", summary="患者手机号+姓名登录")
def patient_login(form: PatientLoginRequest, db: Session = Depends(get_db)):
    patient = (
        db.query(Patient)
        .filter(
            Patient.phone == form.phone,
            Patient.name == form.name,
            Patient.is_active.is_(True),
        )
        .first()
    )
    if not patient:
        return {"exists": False}

    try:
        visit_count = db.execute(
            text("SELECT COUNT(*) FROM visits WHERE patient_id = :pid"),
            {"pid": patient.id},
        ).scalar() or 0
    except Exception:
        visit_count = 0

    return {
        "exists": True,
        "patient_id": patient.id,
        "name": patient.name,
        "visit_count": visit_count,
    }


@router.post("/wechat", summary="微信登录（V2 预留）")
def wechat_login():
    raise BusinessError("微信登录功能将在 V2 版本开放")