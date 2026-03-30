from pydantic import BaseModel, field_validator


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


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


class PatientLoginResponse(BaseModel):
    exists: bool
    patient_id: int | None = None
    name: str | None = None
    visit_count: int = 0